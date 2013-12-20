#!/usr/bin/env python
"""1000 Genomes - A Deep Catalog of Human Genetic Variation."""

# We can another GATK resource since it's pretty much the same
from example import Resource as iResource


class Resource(iResource):
  """docstring for 1000 Genomes Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "1000g"

    self.parts = 1
    self.names = ["1000G_omni.vcf.gz"]

  def paths(self, version):
    # 1 file
    base = "{base}/{v}/b37".format(base=self.baseUrl, v=version)
    f = "1000G_omni2.5.b37.vcf.gz"

    return ["{base}/{file}".format(base=base, file=f)]
