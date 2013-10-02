#!/usr/bin/env python

from ..resource import BaseResource
from ..servers.gatk import GATK


class Resource(BaseResource):
  """docstring for exampleBAM Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.ftp = GATK()
    self.baseUrl = "bundle"

    self.name = "exampleBAM.bam"

  def versions(self):
    return [dirName for dirName in self.ftp.ls(self.baseUrl)]

  def latest(self):
    return max([float(v) for v in self.versions])

  def newer(self, current, challenger):
    # Simply check which float is biggest
    return float(challenger) > float(current)

  def paths(self, version):
    # Only a single file
    return ["{base}/{v}/exampleFASTA/exampleBAM.bam"
            .format(base=self.baseUrl, v=version)]
