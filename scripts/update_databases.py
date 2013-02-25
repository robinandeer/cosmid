#!/usr/bin/env python

from __future__ import print_function
import argparse
import ftplib
from ftplib import FTP
from StringIO import StringIO
import os
import re
import sys
from glob import glob
import logging
import subprocess


class Fetcher(object):
    """
        ### Fetcher ###
        Able to update and download the following files:
        * Ensembl reference FASTA-file (saved as Homo_sapiens.GRCh??_nochr.fasta)
        * The CCDS database (saved as CCDS.GRCh??.??_nochr.txt)
        * From GATK:
            "1000G_phase1.indels.{0}.vcf.gz",
            "Mills_and_1000G_gold_standard.indels.{0}.vcf.gz",
            "dbsnp_137.{0}.vcf.gz",
            "hapmap_3.3.{0}.vcf.gz",
            "1000G_omni2.5.{0}.vcf.gz"
            "dbsnp_137.{0}.excluding_sites_after_129.vcf.gz"
        * hg19/18 etc reference genome from UCSC
    """
    def __init__(self, username, project="b2010080"):
        super(Fetcher, self).__init__()

        self.username = username
        self.project = project

        self.logger = logging.getLogger()

    @property
    def base_ref_path(self):
        return "/bubo/proj/" + self.project + "/private/wgs_wf_references/"

    def this_file_exists(self, path):
        """Does a specified file exist?"""
        return os.path.exists(path)

    def warn_error(self, ftp, e):
        # Warn the user in standardized way
        self.logger.warn(ftp.host + str(e))

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

    def latest_uppmax_ensembl_fasta(self):
        """
            Returns the currently latest assembly on Uppmax. We don't care about
            the patch version for now.
        """

        latest_assembly = [0, 0]

        # To extract the version numbers from the filename
        ptrn = re.compile("Homo_sapiens.GRCh(.*?)_nochr.fasta")

        # Get all the versions on Uppmax
        ensembl_files = glob(self.base_ref_path + "Homo_sapiens.GRCh*_nochr.fasta")

        # Loop through all the files/versions
        for ensembl_file in ensembl_files:
            # Extract the assembly number and version repectively
            temp_assembly = [int(i) for i in ptrn.findall(ensembl_file)[0].split(".")]

            # Check if that assembly number and version is later than the currently latest
            # First check assembly number
            if temp_assembly[0] >= latest_assembly[0]:
                # Then check assembly version
                if temp_assembly[1] > latest_assembly[1]:
                    # Replace
                    latest_assembly = temp_assembly

        return "GRCh{0}.{1}".format(latest_assembly[0], latest_assembly[1])

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

    def gatk(self, files_to_get, version="latest", assembly="hg19", username="gsapubftp-anonymous"):

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
            for file_name in files_to_get:
                # Add the version of the file if possible (remove gz just in case)
                filename = file_name.format(assembly).replace(".gz", "")
                filename_gz = filename + ".gz"

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


def main(args):

    fetcher = Fetcher(args.email, project=args.project)

    if args.ensembl:
        # Get Ensembl fasta reference
        fetcher.ensembl(args.ensembl_assembly)

    if args.ccds:
        # Get the NCBI files
        fetcher.ncbi(args.ccds_release)

    if args.gatk:
        # Get all the GATK curated files
        fetcher.gatk(args.gatk_files, version=args.gatk_version, assembly=args.gatk_assembly)

    if args.ucsc:
        # Get the RefSeq FASTA file from UCSC
        fetcher.ucsc(args.ucsc_assembly)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Your email address
    parser.add_argument('-email', '--email', type=str, required=True)
    parser.add_argument('-p', '--project', type=str, default="b2010080")

    # Ensembl options
    parser.add_argument('-e', '--ensembl', action='store_true', default=False)
    parser.add_argument('-ea', '--ensembl_assembly', type=str, default="latest")

    # NCBI CCDS options
    parser.add_argument('-c', '--ccds', action='store_true', default=False)
    parser.add_argument('-cr', '--ccds_release', type=str, default="latest")

    # UCSC options
    parser.add_argument('-u', '--ucsc', action='store_true', default=False)
    parser.add_argument('-ua', '--ucsc_assembly', type=str, default="hg19")

    # GATK options
    parser.add_argument('-g', '--gatk', action='store_true', default=False)
    parser.add_argument('-gv', '--gatk_version', type=str, default="latest")
    # Input the actual file names since the request will be from a script that
    # already knows which file it's looking for.
    parser.add_argument('-gf', '--gatk_files', type=str, nargs="+")
    parser.add_argument('-ga', '--gatk_assembly', type=str, default="hg19")

    args = parser.parse_args()
    main(args)

# # Bash
# for chrm in "chr1" "chr2" "chr3" "chr4" "chr5" "chr6" "chr7" "chr8" "chr9" "chr10" "chr11" "chr12" "chr13" "chr14" "chr15" "chr16" "chr17" "chr18" "chr19" "chr20" "chr21" "chr22" "chrX" "chrY"
# do
#   gzip -d "$chrm.fa.gz"
# done

# cat chr*.fa > Homo_sapiens.GRCh37.dna.concat.fa
