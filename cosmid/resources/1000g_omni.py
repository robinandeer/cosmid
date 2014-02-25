#!/usr/bin/env python
"""1000 Genomes - A Deep Catalog of Human Genetic Variation."""

# We can another GATK resource since it's pretty much the same
from example import Resource as iResource


class Resource(iResource):
  """docstring for 1000 Genomes Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "1000g_omni"

    self.parts = 1
    self.names = ['1000G_omni.vcf.gz']

  def paths(self, version):
    # 1 file
    bundle_id, assembly = self.defineVersion(version)
    base = "{base}/{bundle}/{assembly}".format(base=self.baseUrl,
                                               bundle=bundle_id,
                                               assembly=assembly)
    f = "1000G_omni2.5.{}.vcf.gz".format(assembly)

    return ["{base}/{file}".format(base=base, file=f)]
