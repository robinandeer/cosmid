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
    bundle_id, assembly = self.defineVersion(version)

    # 1 file
    base = "{base}/{bundle}/{assembly}"\
           .format(base=self.baseUrl, bundle=bundle_id, assembly=assembly)
    f = "hapmap_3.3.{}.vcf.gz".format(assembly)

    return ["{base}/{file}".format(base=base, file=f)]
