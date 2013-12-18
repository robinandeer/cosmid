#!/usr/bin/env python
"""Human genes from Ensembl."""

from ensembl_assembly import Resource as iResource
import sh


class Resource(iResource):
  """docstring for Ensembl GTF Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "gtf"

    self.names = ["Ensembl.Homo_sapiens.gtf.gz"]

  def paths(self, version):
    # 1 file
    base = "pub/release-{}/gtf/homo_sapiens".format(version)
    files = self.ftp.listFiles(base, "*gtf.gz")

    return ["{base}/{file}".format(base=base, file=files[0])]

  def postClone(self, cloned_files, target_dir, version):
    """
    Extracts the compressed archives.

    .. versionadded:: 0.3.0
    """
    # GZIP the files (and remove the archive)
    for f in cloned_files:

      # Only some of the files needs to be gzipped
      if f.endswith(".gz"):
        sh.gunzip(f)
