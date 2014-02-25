#!/usr/bin/env python
"""dbSNP - genetic variation within and across different species."""

# We can another GATK resource since it's pretty much the same
from example import Resource as iResource


class Resource(iResource):
  """docstring for dbSNP Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "dbsnpex"

    self.parts = 1
    self.names = ['dbsnp_137.excluding_sites_after_129.vcf.gz']

  def paths(self, version):
    bundle_id, assembly = self.defineVersion(version)

    if bundle_id == self.latest():
      num = "138"
    else:
      num = "137"

    # 1 file
    base = "{base}/{bundle}/{assembly}"\
           .format(base=self.baseUrl, bundle=bundle_id, assembly=assembly)
    f = "dbsnp_{num}.{assembly}.excluding_sites_after_129.vcf.gz"\
        .format(num=num, assembly=assembly)

    return ["{base}/{file}".format(base=base, file=f)]
