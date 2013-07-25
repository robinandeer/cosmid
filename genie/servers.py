#!/usr/bin/env python

from __future__ import print_function
import os
import ftputil
import fnmatch
import shutil
import sh


class File(object):
  """
  File: represents a file on a remote server.
  ===============

  url     [str] - Path to directory of the file
  pattern [str] - Unique pattern to select file in directory
  """
  def __init__(self, url, pattern="", count=1):
    super(File, self).__init__()
    self.url = url
    self.pattern = pattern
    self.count = count

  def __str__(self):
    return "    URL:   {url}\nPattern:   {ptrn}"\
           .format(url=self.url, ptrn=self.pattern)


class FTP(object):
  """
  FTP: base class for FTP server. Wraps high level FTPHost. Will not unzip files
  since this is elementary in bash. Will check for currently downloading files
  and wait until finished.
  ===============

  server   [str]  - Base URL for the server
  username [str]  - Authentication username (usually your email)
  password [str]  - Authentication password (sometimes email)
  force    [bool] - Set True to force overwrites etc.
  """
  def __init__(self, server, username, password, force=False):
    super(FTP, self).__init__()

    # Inheriting from the class doesn't seem to work - wrapping
    self.ftp = ftputil.FTPHost(server, username, password)

    self.file = None
    self.version = "latest"  # Default
    self.saveName = None

    # Default directory to save to is the current one
    self.saveDir = "./"

    # Force overwriting existing target files
    self._force = force

    # Defaults to unzip gzipped files
    self.userWantsToUnzip = True

  def force(self, option=None):
    """
    Public: Decides if existing files will be overwritten without no questions
    asked.

    option [bool] - Assert: files should be overwritten.
    =============
    """
    self._force = option or True

    return self

  def save(self, file_id):
    """
    Public: Decides which file is to be downloaded. Required.
    =============
    """

    if file_id in self.files:
      # Get the requested file object
      self.file = self.files[file_id]

    else:
      print("Sorry, I'm not aware of that file: {}".format(file_id))

    return self

  def v(self, version):
    """
    Public: Decides which version of a file to be downloaded.
    Will be supported in the future.
    =============
    """
    self.version = version

    return self

  def to(self, path):
    """
    Public: Sets the path where the file will be saved.
    =============

    path [str] - The path to the save location
    """

    # Extract the file name the will be save to
    fileName = os.path.basename()

    # If the user provided a file name, use that
    # => otherwise name the downloaded file the same as on the remote server
    if fileName != "":

      if fileName.endswith(".gz"):
        self.userWantsToUnzip = False
        # Remove the .gz file ending
        fileName = fileName[:-3]

      self.saveName = fileName

    # Extract the path to the save directory
    dirPath = os.path.dirname()
    if os.path.isdir(dirPath):
      self.saveDir = dirPath
    else:
      print("You don't fool me. This path doesn't exist: {}".format(dirPath))

    return self

  def savePath(self, ext=""):
    return "{path}/{file}{ext}".format(path=self.saveDir, file=self.saveName,
                                       ext=ext)

  def tempPath(self, ext=""):
    return "{path}/__temp.{file}{ext}".format(path=self.saveDir,
                                              file=self.saveName, ext=ext)

  def _findInList(self, items, pattern):
    """
    Private.
    """
    return [item for item in items if fnmatch.fnmatch(item, pattern)]

  def _exists(self, ext=""):
    if self.force:
      return False
    else:
      if os.path.isfile(self.tempPath(ext)):
        # The requested file is being downloaded => wait until it is finished
        return True

      # Check if temp file is downloading "{folder}/__temp.{file}"
      # If so: start watching for file changes and wait until that file is
      # downloaded.
      return os.path.isfile(self.savePath())

  def move(self, source, dest):
    try:
      # Move/renmae the file when ready
      shutil.move(source, dest)
    except shutil.Error, e:
      raise e

  def commit(self, dry=False):
    """
    Public: Saves a file from the server to the computer.
    =============

    returns [int] - 0: OK, >0: NOT OK
    """
    # Now we have enough to contact the server and fetch file names to download
    fileNames = self._findInList(self.ftp.listdir(self.file.url),
                                                  self.file.pattern)

    if len(fileNames) == self.file.count:

      # Set a save name unless already set
      if self.saveName is None:
        # Use the same name as on server
        self.to("{path}/{file}".format(path=self.saveDir, file=fileNames[0]))

      # Is the remote file gzipped? (Binary format)
      if fileNames[0].endswith(".gz"):
        mode = "b"
        ext = ".gz"
      else:
        # Default mode is to download non-binary files
        mode = "a"
        ext = ""

      # Avoid overwriting files (unless "force")
      if not self._exists():
        path = "{path}/{file}".format(path=self.file.url, file=fileNames[0])

        if not dry:
          # Initiate download of the file
          self.ftp.download(path, self.tempPath(ext), mode)

          if mode == "b" and self.userWantsToUnzip:
            # Unzip and remove archive
            sh.gunzip(self.tempPath(".gz"))
            # Now the file ending ".gz" has been removed
            ext = ""

          # Rename the file to the final file name (removing leading "__temp.")
          self.move(self.tempPath(ext), self.savePath(ext))

        else:
          return {"fileNames": fileNames, "savePath": self.savePath(ext),
                  "tempPath": self.tempPath(ext), "mode": mode}

    else:
      # NOT OK (for now)
      return 1

    # OK
    return 0


class Ensembl(FTP):
  """docstring for Ensembl"""
  def __init__(self, username="anonymous", password=""):
    super(Ensembl, self).__init__("ftp.ensembl.org", username, password)

    self.files = {
      # The primary assembly in FASTA format
      "assembly": File("pub/current_fasta/homo_sapiens/dna",
                       "*.dna.primary_assembly.fa.gz"),

      "gtf": File("pub/current_gtf/homo_sapiens/", "*gtf.gz")
    }


class NCBI(FTP):
  """docstring for NCBI"""
  def __init__(self, username="anonymous", password=""):
    # The password is supposed to be your email...
    super(NCBI, self).__init__("ftp.ncbi.nlm.nih.gov", username, password)

    # TODO: refseq? /refseq/

    self.files = {
      # Genbank assembly in FASTA format
      "genbank": File("genbank/genomes/Eukaryotes/vertebrates_mammals/"
                      "Homo_sapiens/GRCh37.p13/Primary_Assembly/"
                      "assembled_chromosomes/FASTA/", "*.fa.gz", 24),

      # All the assembeled chromosomes (+ MT)
      "assembly": File("genomes/Homo_sapiens/Assembled_chromosomes/seq/",
                       "hs_ref_*_chr*.fa.gz", 25),

      # CCDS, manually curated database of transcript annotations
      "ccds": File("pub/CCDS/current_human", "CCDS.current.txt") 
    }

class GATK(FTP):
  """docstring for GATK"""
  def __init__(self, username="gsapubftp-anonymous", password="", version=None,
               assembly="b37"):
    super(GATK, self).__init__("ftp.broadinstitute.org", username, password)

    if version is None:
      # Figure out which is the latest version folder
      folders = [float(folder) for folder in self.ftp.listdir("bundle/")]
      version = max(folders)

    url = "bundle/{dist}/{assembly}".format(dist=folder, assembly=assembly)
    self.files = {
      "1000g": File(url, "1000G_omni*.vcf.gz"),
      "mills": File(url, "Mills_and_1000G_gold_standard.indels.*.vcf.gz"),
      "dbsnp": File(url, "dbsnp_*{}.vcf.gz".format(assembly)),
      "hapmap": File(url, "hapmap_*.vcf.gz"),
      "indels": File(url, "1000G_phase1.indels.*.vcf.gz"),
      "dbsnpex": File(url, "dbsnp_*.excluding_sites_after_*.vcf.gz")
    }

class UCSC(FTP):
  """docstring for UCSC"""
  def __init__(self, username="anonymous", password="yourEmail",
               assembly="hg19"):
    super(UCSC, self).__init__("hgdownload.cse.ucsc.edu", username, password)

    self.files = {
      "assembly": File("goldenPath/currentGenomes/Homo_sapiens/bigZips/",
                       "chromFa.tar.gz")
    }
