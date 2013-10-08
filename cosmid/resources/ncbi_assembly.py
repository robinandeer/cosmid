#!/usr/bin/env python

from ..resource import BaseResource
from ..servers.ncbi import NCBI


class Resource(BaseResource):
  """docstring for CCDS Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "ncbi_assembly"

    self.ftp = NCBI()
    self.baseUrl = "genomes/Homo_sapiens"

    self.parts = 25  # Including MT
    self.names = ["NCBI.Homo_sapiens.{chrom}.fa.gz".format(chrom=chrom)
                  for chrom in range(1, 23) + ["X", "Y", "MT"]]

  def versions(self):
    # Basically the combination of assembly + path is a valid float

    # First get versions from the archive (<=37.3)
    # Assemlies earlier than 35 are organized differently...
    archive = [dirName.replace("BUILD.")
               for dirName in self.ftp.ls(self.baseUrl + "/ARCHIVE")
               if dirName.startswith("BUILD")
               and not dirName.startswith("BUILD.34")]

    return archive + ["latest"]

  def newer(self, current, challenger):
    if current == "latest":
      return False  # Always
    elif challenger == "latest":
      return True  # Always
    else:
      # For now...
      return float(challenger) > float(current)

  def latest(self):
    # Return highest version number (float)
    return "latest"

  def paths(self, version):
    if version == "latest":
      base = ("{base}/Assembled_chromosomes/seq".format(base=self.baseUrl))

    else:
      # For all the archived releases
      base = ("{base}/ARCHIVE/BUILD.{v}/Assembled_chromosomes/seq"
              .format(base=self.baseUrl, v=version))

    files = self.ftp.listFiles(base, "hs_ref_*_chr*.fa.gz")

    # Should only be one file that matches
    return ["{base}/{file}".format(base=base, file=f) for f in files]
