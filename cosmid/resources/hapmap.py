#!/usr/bin/env python
"""Hapmap 3.3 from GATK."""

# We can another GATK resource since it's pretty much the same
from example import Resource as iResource


class Resource(iResource):
  """docstring for dbSNP Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "hapmap"

    self.parts = 1
    self.names = ["hapmap_3.3.vcf.gz"]

  def paths(self, version):
    # 1 file
    base = "{base}/{v}/b37".format(base=self.baseUrl, v=version)
    f = "hapmap_3.3.b37.vcf.gz"

    return ["{base}/{file}".format(base=base, file=f)]
