#!/usr/bin/env python

from ..resource import BaseResource
from ..servers.gatk import GATK


class Resource(BaseResource):
  """docstring for exampleBAM Resource"""
  def __init__(self):
    super(Resource, self).__init__()

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
