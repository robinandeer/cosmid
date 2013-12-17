#!/usr/bin/env python
"""UCSC Human genome assembly."""

from __future__ import print_function
from ..resource import BaseResource
from ..servers.ucsc import UCSC
import sh


class Resource(BaseResource):
  """docstring for Ensembl Assembly Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "ucsc_assembly"

    self.ftp = UCSC()
    self.baseUrl = "goldenPath"

    self.parts = 1
    self.names = ["UCSC.Homo_sapiens.tar.gz"]

  def versions(self):
    # Only one release
    # Skip releases like "hg15june2000" (if)
    return [dirName for dirName in
            self.ftp.listFiles(self.baseUrl, "hg[1-9]*")
            if not len(dirName) > 4]

  def latest(self):
    number = max([int(v.replace("hg", "")) for v in self.versions()])
    return "hg{}".format(number)

  def newer(self, current, challenger):
    return int(challenger.replace("hg", "")) > int(current.replace("hg", ""))

  def paths(self, version):
    base = "{base}/{v}/bigZips".format(base=self.baseUrl, v=version)

    # If the version is newer than 'hg18' it will be a '.tar.gz' file
    if self.newer("hg18", version):
      return ["{base}/chromFa.tar.gz".format(base=self.baseUrl)]

    else:
      return ["{base}/chromFa.zip".format(base=base)]

  def postClone(self, cloned_files, target_dir, version):
    """
    Extracts the compressed archives.

    .. versionadded:: 0.3.0
    """
    f = cloned_files[0]

    if self.newer("hg18", version):
      # GZIP and TAR the file and save to the target directory
      sh.tar("-xzf", f, "-C", target_dir)

    else:
      # Rename to ".zip"
      sh.mv(f, f.replace("tar.gz", "zip"))

      # GunZIP the file (and remove the archive)
      sh.gunzip(f)
