#!/usr/bin/env python
"""1000 Genomes decoy assembly sequence, version 5."""

from ..resource import BaseResource
from ..servers.thousandg import ThousandG


class Resource(BaseResource):
  """docstring for CCDS Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "decoy"

    self.ftp = ThousandG()
    self.baseUrl = "1000genomes/ftp/technical/reference/phase2_reference_assembly_sequence"

    self.parts = 1
    self.names = ["hs37d5.fa.gz"]

  def versions(self):
    return [5]

  def latest(self):
    return 5

  def newer(self, current, challenger):
    return challenger > current

  def paths(self, version):
    uri = "{base}/hs37d{v}.fa.gz".format(base=self.baseUrl, v=version)
    return [uri]
