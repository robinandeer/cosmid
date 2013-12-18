#!/usr/bin/env python
"""The Consensus CoDing Sequence (CCDS) project; "a core set of human and mouse protein-coding regions"."""

from ..resource import BaseResource
from ..servers.ncbi import NCBI


class Resource(BaseResource):
  """docstring for CCDS Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "ccds"

    self.ftp = NCBI()
    self.baseUrl = "pub/CCDS"

    self.parts = 1
    self.names = ["CCDS.txt"]

  def versions(self):
    return [dirName for dirName in self.ftp.ls(self.baseUrl + "/archive")
            if dirName.startswith("Hs")]

  def latest(self):
    # Load in info-file
    f = self.ftp.file("{}/current_human/BuildInfo.current.txt"
                      .format(self.baseUrl))

    # Discard comment line
    _ = f.readline()

    # Return formatted NCBI release number
    return "Hs{}".format(f.readline().split("\t")[1])

  def newer(self, current, challenger):
    currentFloat = float(current.replace("Hs", ""))
    challengerFloat = float(challenger.replace("Hs", ""))

    # Simply check which float is biggest
    return challengerFloat > currentFloat

  def paths(self, version):
    base = "{base}/archive/{v}".format(base=self.baseUrl, v=version)
    files = self.ftp.listFiles(base, "CCDS.[0-9]*")

    # Should only be one file that matches
    return ["{base}/{file}".format(base=base, file=f) for f in files]
