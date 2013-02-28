#!/usr/bin/env python

from __future__ import print_function
import sys
import os
import ftplib
from ftplib import FTP
from StringIO import StringIO
from pybedtools import BedTool
import subprocess


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
        return "/bubo/proj/" + self.project + "/private/wgs_wf_references/"

    def this_file_exists(self, path):
        """Does a specified file exist?"""
        # If the user wants to force overwrite, let her.
        if not self.force:
            answer = os.path.exists(path)
        else:
            answer = False

        return answer

    def warn_error(self, ftp, e):
        """Warn the user in standardized way"""

        print(ftp.host + str(e))

        # Always best to close
        ftp.close()

        # Exit script
        sys.exit(1)

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

    def ensembl(self, requested_assembly):

        try:
            # Log on to the Ensembl FTP
            ftp_ensembl = FTP("ftp.ensembl.org")
            ftp_ensembl.login()

            # Print welcome message
            print(ftp_ensembl.getwelcome(), end="\n")

            if requested_assembly == "latest":

                # Get the latest assembly version, GRCh37 is implied (until they release 38 ...)
                releases = [dirname.replace("release-", "") for dirname in ftp_ensembl.nlst("pub") if dirname.find("release") != -1]
                releases.sort()  # Just to be sure
                latest_ensembl_release = releases[-1]

                # Update the requested assembly identifier
                requested_assembly = "GRCh37.{0}".format(latest_ensembl_release)

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
                file_list = ftp_ensembl.nlst(path_to_fasta_files)

                # Get the correct file name (independent of release number, if you want the latest)
                for file_name in file_list:
                    # The first match is the correct file!
                    if file_name.find("dna.primary_assembly.fa.gz") != -1:
                        fasta_name = file_name

                        break

                # Request and get the reference genome file from the server, catch the response
                ftp_ensembl.retrbinary("RETR {0}{1}".format(path_to_fasta_files, fasta_name), open(self.base_ref_path + fasta_filename + ".gz", "wb").write)
                self.unzip(fasta_filename + ".gz")

            ftp_ensembl.close()

        except ftplib.all_errors, e:
            self.warn_error(ftp_ensembl, e)

    def ncbi(self, ccds_release):

        try:
            # Get the awesome CCDS database
            ftp_ncbi = FTP("ftp.ncbi.nih.gov")
            ftp_ncbi.login("anonymous", self.username)

            # Print welcome message
            print(ftp_ncbi.getwelcome(), end="\n")

            # To read the info file
            ccds_info = StringIO()
            if ccds_release == "latest":
                ftp_ncbi.retrbinary("RETR pub/CCDS/current_human/BuildInfo.current.txt", ccds_info.write)
            else:
                ftp_ncbi.retrbinary("RETR pub/CCDS/archive/" + ccds_release + "/BuildInfo.current.txt", ccds_info.write)

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
                    ftp_ncbi.retrbinary("RETR pub/CCDS/current_human/CCDS.current.txt", open(self.base_ref_path + savename, "wb").write)
                else:
                    ftp_ncbi.retrbinary("RETR pub/CCDS/archive/Hs" + ccds_release + "/CCDS.current.txt", open(self.base_ref_path + savename, "wb").write)

                print("{} downloaded successfully!".format(savename), end="\n")

            ftp_ncbi.close()

        except ftplib.all_errors, e:
            self.warn_error(ftp_ncbi, e)

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
            ftp_gatk = FTP("ftp.broadinstitute.org")
            ftp_gatk.login(username, "")

            if version == "latest":
                # List all versions (floats)
                gatk_versions = [float(ver.replace("bundle/", "")) for ver in ftp_gatk.nlst("bundle")]

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

                # Check if the file already exists
                if self.this_file_exists(self.base_ref_path + filename):
                    print("{} already exists.".format(filename), end="\n")
                else:
                    print("Downloading {} ...".format(filename_gz), end="\n")
                    ftp_gatk.retrbinary("RETR " + base_path + filename_gz, open(self.base_ref_path + filename_gz, "wb").write)

                    self.unzip(filename_gz)

        except ftplib.all_errors, e:
            self.warn_error(ftp_gatk, e)

    def ucsc(self, assembly):

        try:
            # Connect and provide user info
            ftp_ucsc = FTP("hgdownload.cse.ucsc.edu")
            # [username: anonymous, password: your email address]
            ftp_ucsc.login("anonymous", self.username)

            savename = "Homo_sapiens.{}_chr.fasta".format(assembly)
            savename_gz = savename + ".tar.gz"

            # Does the file already exist?
            if self.this_file_exists(self.base_ref_path + savename):
                print("{} already exists.".format(savename), end="\n")
            else:
                # Download the big FASTA file
                print("Downloading {} ...".format(savename_gz), end="\n")
                ftp_ucsc.retrbinary("RETR goldenPath/" + assembly + "/bigZips/chromFa.tar.gz", open(self.base_ref_path + savename_gz, "wb").write)

                self.unzip(savename_gz)

        except ftplib.all_errors, e:
            self.warn_error(ftp_ucsc, e)

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
