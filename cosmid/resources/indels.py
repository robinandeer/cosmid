#!/usr/bin/env python
"""1000 Genomes phase 1 indels from GATK."""

# We can another GATK resource since it's pretty much the same
from example import Resource as iResource


class Resource(iResource):
  """docstring for dbSNP Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "indels"

    self.parts = 1
    self.names = ["1000G_phase1.indels.vcf.gz"]

  def paths(self, version):
    # 1 file
    base = "{base}/{v}/b37".format(base=self.baseUrl, v=version)
    f = "1000G_phase1.indels.b37.vcf.gz"

    return ["{base}/{file}".format(base=base, file=f)]
