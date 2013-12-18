#!/usr/bin/env python
"""Mills and 1000G gold standard indels: a very stringently curated list of indels."""

# We can another GATK resource since it's pretty much the same
from example import Resource as iResource


class Resource(iResource):
  """docstring for Mills and 1000G Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "mills"

    self.parts = 1
    self.names = ["Mills_and_1000G_gold_standard.indels.vcf.gz"]

  def paths(self, version):
    # 1 file
    base = "{base}/{v}/b37".format(base=self.baseUrl, v=version)
    f = "Mills_and_1000G_gold_standard.indels.b37.vcf.gz".format(version)

    return ["{base}/{file}".format(base=base, file=f)]
