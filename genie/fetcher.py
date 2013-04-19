#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import ftplib
from ftplib import FTP
from StringIO import StringIO
from pybedtools import BedTool
import subprocess
import csv
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Allow parsing of huge files
csv.field_size_limit(1000000000)


class ChangeHandler(FileSystemEventHandler):
    """
    React to changes in files in the reference directory
    """

    def __init__(self, filename):

        # This is the filename to look for changes to
        self.filename = filename

    def on_moved(self, event):
        "If any file or folder is changed"

        if event.dest_path.split("/")[-1] == self.filename:
            raise FileReady


class FileReady(Exception):
    pass


class Fetcher(object):
    """docstring for Fetcher"""
    def __init__(self, username, project="b2010080", force=False):
        super(Fetcher, self).__init__()

        # Set up the attributes
        self.username = username
        self.project = project
        self.force = force

    @property
    def base_ref_path(self):
        return "/proj/" + self.project + "/private/wgs_wf_references/"

    def this_file_exists(self, path, required=False):
        """
        Does a specified file exist?
        """

        # For reference files that are needed to perform the requested convertion/calculations
        if required:

            if not os.path.exists(path):
                # If not: ask the user if she would like to download it now
                user_wants_to_download = raw_input("The DNA reference file doesn't exist. Do you want to download it now? [y/n] ")
                if user_wants_to_download in ["yes", "y", "Y"]:
                    return False
                else:
                    return False

        # If the user wants to force overwrite, let her.
        if not self.force:
            return os.path.exists(path)
        else:
            return False

    def file_being_downloaded(self, dir, filename, temp_path):

        if not os.path.exists(temp_path):

            # Use the custom event handler
            event_handler = ChangeHandler(filename)
            observer = Observer()
            observer.schedule(event_handler, dir)

            # Start the observer to look for creation of the file
            observer.start()

            try:
                while True:
                    time.sleep(1)
            except FileReady:
                # Raised when the file has been created (renamed from TEMP_*)
                observer.stop()

            observer.join()

            return "ready"

        return "proceed"

    def warn_error(self, ftp, e):
        """Warn the user in standardized way"""

        print(ftp.host + str(e))

        # Always best to close
        ftp.close()

    def unzip(self, filename):
        #gzip -d Homo_sapiens.GRCh37.70.dna.chromosome.22.fa.gz
        if filename.find("tar") != -1:
            # tar.gz file!
            response = subprocess.call(['tar', '-zxvf', self.base_ref_path + filename])
        else:
            # Regular .gz file
            response = subprocess.call(['gzip', '-d', self.base_ref_path + filename])

        if response == 0:
            print("{} downloaded and extracted successfully!".format(filename.replace(".gz", "").replace(".tar", "")), end="\n")
        else:
            print("{} failed decryption. Please do it manually.".format(filename))

    def connect(self, server, username, password):
        try:
            # Start up and login
            ftp = FTP(server)
            ftp.login(username, password)

            # Return the FTP when ready
            return ftp

        except ftplib.all_errors, e:
            # This could be a login error
            if e.message.find("530") != -1:
                print("Your login information wasn't valid for: {}".format(server))
            else:
                print("FTP error for {0}, message: {1}".format(server, e.message))

            # Always best to close connection
            ftp.close()

            # Return "not good"
            return -1

    def ensembl(self, requested_assembly):

        try:
            # Log on to the Ensembl FTP
            ftp = self.connect("ftp.ensembl.org", "", "")

            # Print welcome message
            print(ftp.getwelcome(), end="\n")

            # If the user has requested the latest release we need to find out the accession
            if requested_assembly == "latest":

                # Get the latest assembly version, GRCh37 is implied (until they release 38 ...)
                releases = [dirname.replace("release-", "") for dirname in ftp.nlst("pub") if dirname.find("release") != -1]
                releases.sort()  # Just to be sure
                latest_ensembl_release = releases[-1]

                # Update the requested assembly identifier
                requested_assembly = "GRCh37.{0}".format(latest_ensembl_release)

            # CMMS convention for naming FASTA files
            fasta_filename_base = "Homo_sapiens.{0}_nochr.fasta"

            fasta_filename = fasta_filename_base.format(requested_assembly)

            # We can now check if the file is already on Uppmax
            if self.this_file_exists(self.base_ref_path + fasta_filename):
                print("{0} already exists.".format(fasta_filename), end="\n")

            else:

                # The base URL to the FASTA files directory
                base_path = "pub/{}/fasta/homo_sapiens/dna/"

                release_path = "release-{0}".format(requested_assembly[7:])

                path_to_fasta_files = base_path.format(release_path)

                # Look at all the files in the dir
                file_list = ftp.nlst(path_to_fasta_files)

                # Get the correct file name (independent of release number, if you want the latest)
                for file_name in file_list:
                    # The first match is the correct file!
                    if file_name.find("dna.primary_assembly.fa.gz") != -1:
                        fasta_name = file_name

                        break

                # Check and possibly wait for the file if it is being downloaded/processed
                file_status = self.file_being_downloaded(self.base_ref_path, fasta_filename, fasta_filename + ".gz")

                if file_status == "proceed":
                    # Request and get the reference genome file from the server, catch the response
                    ftp.retrbinary("RETR {0}{1}".format(path_to_fasta_files, fasta_name), open(self.base_ref_path + fasta_filename + ".gz", "wb").write)
                    self.unzip(fasta_filename + ".gz")

                elif file_status == "ready":
                    # The file was already being downloaded, we waited and it is now ready to be used.
                    pass

            ftp.close()

        except ftplib.all_errors, e:
            self.warn_error(ftp, e)

    def ncbi(self, ccds_release):

        try:
            # Get the awesome CCDS database
            ftp = self.connect("ftp.ncbi.nih.gov", "anonymous", self.username)

            # Print welcome message
            print(ftp.getwelcome(), end="\n")

            # To read the info file
            ccds_info = StringIO()
            if ccds_release == "latest":
                ftp.retrbinary("RETR pub/CCDS/current_human/BuildInfo.current.txt", ccds_info.write)
            else:
                ftp.retrbinary("RETR pub/CCDS/archive/" + ccds_release + "/BuildInfo.current.txt", ccds_info.write)

            # For naming the output file
            for line in ccds_info.getvalue().split("\n"):
                split_line = line.split("\t")
                # Avoid empty lines
                if split_line[0] != "":
                    if split_line[0][0] != "#":
                        assembly_name = split_line[3][:6]
                        assembly_version = split_line[2]

                        assembly = assembly_name + "." + assembly_version

                        break

            # The Ensembl assembly is used as identifier
            savename = "CCDS.{}_nochr.txt".format(assembly)

            # Write the file
            if self.this_file_exists(self.base_ref_path + savename):
                print("{} already exists.".format(savename), end="\n")

            else:

                if ccds_release == "latest":
                    # The relase is tied to NCBI version so I separate these to
                    # not have to check that number also
                    get_path = "RETR pub/CCDS/current_human/CCDS.current.txt"
                else:
                    get_path = "RETR pub/CCDS/archive/{}/CCDS.current.txt".format(ccds_release)

                # Check and possibly wait for the file if it is being downloaded/processed
                file_status = self.file_being_downloaded(self.base_ref_path, savename, "TEMP_" + savename)

                if file_status == "proceed":
                    ftp.retrbinary(get_path, open(self.base_ref_path + savename, "wb").write)

                    # Rename the "TEMP_*" file to complete the transfer
                    os.rename("{0}TEMP_{1}".format(self.base_ref_path, savename), self.base_ref_path + savename)

                elif file_status == "ready":
                    # The file was already being downloaded, we waited and it is now ready to be used.
                    pass

                print("{} downloaded successfully!".format(savename), end="\n")

            ftp.close()

        except ftplib.all_errors, e:
            self.warn_error(ftp, e)

    def gatk(self, file_codes, version="latest", assembly="hg19", username="gsapubftp-anonymous"):

        # Convert between short codes and filename bases
        converter = {
            "1000g_indels": "1000G_phase1.indels.{}.vcf",
            "mills": "Mills_and_1000G_gold_standard.indels.{}.vcf",
            "dbsnp": "dbsnp_137.{}.vcf",
            "hapmap": "hapmap_3.3.{}.vcf",
            "1000g": "1000G_omni2.5.{}.vcf",
            "dnsnp_ex": "dbsnp_137.{}.excluding_sites_after_129.vcf"
        }

        try:
            # Connect to the server
            ftp = self.connect("ftp.broadinstitute.org", username, "")

            if version == "latest":
                # List all versions (floats)
                gatk_versions = [float(ver.replace("bundle/", "")) for ver in ftp.nlst("bundle")]

                # Sort acending
                gatk_versions.sort()

                # Pick the last one (latest)
                version = gatk_versions[-1]

            if assembly.find("hg") == -1:
                # Ensembl assemblies named differently => "b" + GRCh(**)
                assembly = "b{0}".format(assembly[4:6])

            # This is the URL that the bundles are stored at
            base_path = "bundle/{0}/{1}/".format(version, assembly)

            # Get the files and save as binary (GZIP archives)
            for code in file_codes:
                # Add the version of the file if possible (remove gz just in case)
                # If the code is not recognized => just skip
                try:
                    filename = converter[code].format(assembly).replace(".gz", "")
                    filename_gz = filename + ".gz"
                except KeyError:
                    print("Sorry but that short code ({}) wasn't recognized. Skipping.".format(code))
                    continue

                # Check if the file already exists
                if self.this_file_exists(self.base_ref_path + filename):
                    print("{} already exists.".format(filename), end="\n")
                else:

                    # Check and possibly wait for the file if it is being downloaded/processed
                    file_status = self.file_being_downloaded(self.base_ref_path, filename, filename_gz)

                    if file_status == "proceed":

                        print("Downloading {} ...".format(filename_gz), end="\n")
                        ftp.retrbinary("RETR " + base_path + filename_gz, open(self.base_ref_path + filename_gz, "wb").write)

                        self.unzip(filename_gz)

                    elif file_status == "ready":
                        # The file was already being downloaded, we waited and it is now ready to be used.
                        continue

            ftp.close()

        except ftplib.all_errors, e:
            self.warn_error(ftp, e)

    def ucsc(self, assembly):

        try:
            # Connect and provide user info
            ftp = self.connect("hgdownload.cse.ucsc.edu", "anonymous", self.username)

            savename = "Homo_sapiens.{}_chr.fasta".format(assembly)
            savename_gz = savename + ".tar.gz"

            # Does the file already exist?
            if self.this_file_exists(self.base_ref_path + savename):
                print("{} already exists.".format(savename), end="\n")
            else:

                # Check and possibly wait for the file if it is being downloaded/processed
                file_status = self.file_being_downloaded(self.base_ref_path, savename, savename_gz)

                if file_status == "proceed":

                    # Download the big FASTA file
                    print("Downloading {} ...".format(savename_gz), end="\n")
                    ftp.retrbinary("RETR goldenPath/{}/bigZips/chromFa.tar.gz".format(assembly), open(self.base_ref_path + savename_gz, "wb").write)

                    self.unzip(savename_gz)

                elif file_status == "ready":
                    # The file was already being downloaded, we waited and it is now ready to be used.
                    pass

            ftp.close()

        except ftplib.all_errors, e:
            self.warn_error(ftp, e)

    def converter(self, from_path, to_path, cut=False):
        """
            The eqivalent of running:
            intersectBed -a from_path.bed -b to_path.bed -wa -wb | cut -f1,2,3,5,6,7,8 > conversion_filename.bed
        """

        from_file = from_path.split("/")[-1]
        to_file = to_path.split("/")[-1]

        conversion_filename = from_file.replace(".bed", "") + "__" + to_file
        if self.this_file_exists(self.base_ref_path + conversion_filename):
            print("{} already exists".format(conversion_filename), end="\n")

        else:

            # Check and possibly wait for the file if it is being downloaded/processed
            file_status = self.file_being_downloaded(self.base_ref_path, conversion_filename, "TEMP_" + conversion_filename)

            if file_status == "proceed":

                # RENAME ALWAYS
                pass

            elif file_status == "ready":
                # The file was already being downloaded, we waited and it is now ready to be used.
                pass

            from_elements_bt = BedTool(from_path)
            to_elements_bt = BedTool(to_path)

            # SureSelect targets files contain a lot of unessesary information
            if cut:
                from_elements_bt.intersect(to_elements_bt, wa=True, wb=True).saveas(self.base_ref_path + "temp_" + conversion_filename)

                with open(self.base_ref_path + conversion_filename, "w") as handle:
                    subprocess.call(['cut', '-f{}'.format(cut), self.base_ref_path + "temp_" + conversion_filename], stdout=handle)

                os.remove(self.base_ref_path + "temp_" + conversion_filename)

            else:

                from_elements_bt.intersect(to_elements_bt, wa=True, wb=True).saveas(self.base_ref_path + conversion_filename)

    def gc_content(self, bed_path, assembly="GRCh37.70", reference_path=None, out_path=None):
        """
        Takes a BED file and adds the GC content information as extra columns and saves as a new file.
        """

        if not reference_path:
            # Unless the DNA reference file is provided, attempt to get one form the file system
            reference_path = "{0}Homo_sapiens.{1}_nochr.fasta".format(self.base_ref_path, assembly)

        # Make sure that the reference file exists
        if not self.this_file_exists(reference_path):
            return -1

        if not out_path:
            # Extract the filename from the bed_path and remove the file extension
            in_filename = bed_path.split("/")[-1].replace(".bed", "")

            # Output the file using the input file name + "_gccontent" to signify the difference
            out_filename = "{}_gccontent.bed".format(in_filename)
            out_path = "{0}{1}".format(self.base_ref_path, out_filename)

        # Check if the file already has been generated
        if self.this_file_exists(out_path):
            print("{} already exists".format(out_path), end="\n")
        else:
            # Load in the file with regions to determine GC content for
            regions = BedTool(bed_path)

            # Run the BEDTools "nuc" command and save directly to a file
            regions.nucleotide_content(fi=reference_path).saveas(out_path)

    def chromosomes(self, prepend="chr"):
        # List all chromosomes
        chrom_list = range(1, 23) + ["X", "Y"]
        return ["{0}{1}".format(prepend, str(chrom)) for chrom in chrom_list]

    def convert2bed(self, bed_path, remove_wierd_chr=False, out_path=None):
        """
        Since BED format is defined with chrmosome positions that are 0-based (start) and 1-based (end)
        it's sometimes needed to convert a file to the proper BED format. For example when downloading
        gene coordinates from Biomart.
        """

        # Unless otherwise specified; overwrite the current file
        if not out_path:
            out_path = bed_path

        # All the normal chromosomes (the once present in the capture kits)
        chromosomes = self.chromosomes(prepend="")

        with open(bed_path, "r") as handle:
            if remove_wierd_chr:
                lines = ["\t".join([row[0]] + [str(int(row[1]) - 1)] + row[2:]) for row in csv.reader(handle, dialect="excel-tab") if row[0] in chromosomes]
            else:
                lines = ["\t".join([row[0]] + [str(int(row[1]) - 1)] + row[2:]) for row in csv.reader(handle, dialect="excel-tab")]

        with open(out_path, "w") as handle:

            handle.write("\n".join(lines))

    def reorganize(self, main_path, order, misc_path=None, out_path=None):
        """
        Helper method that lets you take one or two files (tab separated
        for starters) and reorganize the columns of informations. If two
        files are used you will be able to merge information from those files.

        The requirements are that both files are the same length and are
        ordered the same way. Sort the file before running the script if
        nessesary.

        The order is 0-based. It also continues from the main file to the
        misc file. If main has 3 columns and misc has 4 columns, the misc
        column IDs would be [3,4,5,6].

        It currently doesn't handle header comments that only appear in
        one file.
        """

        if not out_path:
            out_path = main_path

        with open(main_path, "r") as main:
            if misc_path:
                with open(misc_path, "r") as misc:
                    lines = [self._addComplexLine(main_row, misc_row, order)
                             for main_row, misc_row in
                             zip(csv.reader(main, dialect="excel-tab"),
                                 csv.reader(misc, dialect="excel-tab"))]

            else:
                lines = [self._addLine(row, order)
                         for row in csv.reader(main, dialect="excel-tab")]

        with open(out_path, "w") as out:
            out.write("\n".join(lines))

    def _addLine(self, row, order):
        return "\t".join([row[i] for i in order])

    def _addComplexLine(self, main_row, misc_row, order):
        line = []
        for i in order:
            main_len = len(main_row)
            if i > main_len:
                line.append(misc_row[i-main_len])
            else:
                line.append(main_row[i])

        return "\t".join(line)

    def join(self, mainPath, newPath, order, outPath,
             idColumns=[0, 1, 2], sep="\t", default=""):

        elements = {}

        # To be able to select the right column when picking values
        mainColCount = 0
        firstLine = True

        with open(mainPath, "r") as handle:

            for line in csv.reader(handle, delimiter=sep):

                if firstLine:
                    mainColCount = len(line)
                    firstLine = False
                    if line[0][0] == "#": continue

                elementID = self._getID(line, idColumns)

                if elementID not in elements:

                    values = [str(default) for _ in range(len(order))]

                    # Loop through all the columns with values to be saved
                    for count, col in enumerate(order):
                        # If the value is from the main file
                        if col < mainColCount:
                            values[count] = line[col]

                    # Add all values with the ID as key
                    elements[elementID] = values

                else:
                    sys.exit("The main file has non-unique IDs: {}"
                             .format(elementID))

        with open(newPath, "r") as handle:

            firstLine = True
            for line in csv.reader(handle, delimiter=sep):

                if firstLine:
                    firstLine = False
                    if line[0][0] == "#": continue

                elementID = self._getID(line, idColumns)

                if elementID in elements:

                    for count, col in enumerate(order):
                        # If the value is from the new file
                        if col >= mainColCount:
                            elements[elementID][count] = line[col -
                                                              mainColCount]

                else:
                    sys.stdout.write("Element not in the main file: {}\n"
                                     .format(line))

        with open(outPath, "w") as handle:

            # Join all elements with given separator,
            # then join lines with newline
            handle.write("\n".join([sep.join(line)
                                    for line in elements.itervalues()]))

        with open(outPath, "a") as handle:

            # Add an empty last line
            handle.write("\n")

    def _getID(self, line, idColumns):
        if isinstance(idColumns, (list, tuple)):

            elementID = "|".join([line[col]
                                  for col in idColumns])

        else:
            elementID = line[idColumns]

        return elementID
