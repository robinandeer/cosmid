#!/usr/bin/env python

from ensembl_assembly import Resource as iResource


class Resource(iResource):
  """docstring for Ensembl GTF Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.names = ["Ensembl.Homo_sapiens.gtf.gz"]

  def paths(self, version):
    # 1 file
    base = "pub/release-{}/gtf/homo_sapiens".format(version)
    files = self.ftp.listFiles(base, "*gtf.gz")

    return ["{base}/{file}".format(base=base, file=files[0])]
