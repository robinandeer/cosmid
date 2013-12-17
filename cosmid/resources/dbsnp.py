#!/usr/bin/env python
"""dbSNP - genetic variation within and across different species."""

# We can another GATK resource since it's pretty much the same
from example import Resource as iResource


class Resource(iResource):
  """docstring for dbSNP Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "dbsnp"

    self.parts = 1
    self.names = ["dbsnp_137.vcf.gz"]

  def paths(self, version):
    # 1 file
    base = "{base}/{v}/b37".format(base=self.baseUrl, v=version)
    f = "dbsnp_137.b37.vcf.gz"

    return ["{base}/{file}".format(base=base, file=f)]
