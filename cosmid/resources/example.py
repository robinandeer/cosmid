#!/usr/bin/env python
"""A few example BAM/Fasta files for testing provided by GATK."""

from ..resource import BaseResource
from ..servers.gatk import GATK
import sh


class Resource(BaseResource):
  """docstring for exampleBAM Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "example"

    self.ftp = GATK()
    self.baseUrl = "bundle"

    self.parts = 4
    self.names = ["exampleBAM.bam", "exampleBAM.bam.bai.gz",
                  "exampleFASTA.fasta.fai.gz", "exampleFASTA.fasta.gz"]

  def versions(self):
    return [float(dirName) for dirName in self.ftp.ls(self.baseUrl)]

  def latest(self):
    return max(self.versions())

  def newer(self, current, challenger):
    # Simply check which float is biggest
    return float(challenger) > float(current)

  def paths(self, version):
    # 4 files
    base = "{base}/{v}/exampleFASTA".format(base=self.baseUrl, v=version)

    return ["{base}/{file}".format(base=base, file=f) for f in self.names]

  def postClone(self, cloned_files, target_dir, version):
    """
    Extracts the compressed archives.

    .. versionadded:: 0.3.0
    """
    # GZIP the files (and remove the archive)
    for f in cloned_files:

      # Only some of the files needs to be gzipped
      if f.endswith(".gz"):
        sh.gunzip(f)

    return 0
