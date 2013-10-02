#!/usr/bin/env python

from ..resource import BaseResource
from ..servers.ncbi import NCBI


class Resource(BaseResource):
  """docstring for CCDS Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.ftp = NCBI()
    self.baseUrl = ("genbank/genomes/Eukaryotes/vertebrates_mammals/"
                    "Homo_sapiens")

    self.parts = 24
    self.names = ["Genbank.Homo_sapiens.{chrom}.fa.gz".format(chrom=chrom)
                  for chrom in range(1, 23) + ["X", "Y"]]

  def versions(self):
    return [dirName for dirName in self.ftp.listFiles(self.baseUrl, "GRCh*")]

  def latest(self):
    # Extract assembly and path number
    versions = [(int(v[3:5]), int(v[8:] or 0)) for v in self.versions()]

    # Sort based on assembly and patch => return the last item
    return sorted(versions, key=lambda x: (x[0], x[1]))[-1]

  def newer(self, current, challenger):
    # Extract assembly and path number
    combos = [(int(v[3:5]), int(v[8:] or 0)) for v in (current, challenger)]

    # If the assemblies differ
    if combos[0][0] != combos[1][0]:
      return combos[1][0] > combos[0][0]

    else:
      # The assemblies are the same => compare patch numbers
      return combos[1][1] > combos[0][1]

  def paths(self, version):
    base = ("{base}/{v}/Primary_Assembly/assembled_chromosomes/FASTA"
            .format(base=self.baseUrl, v=version))
    files = self.ftp.listFiles(base, "*.fa.gz")

    # Should match each of the 24 chromosomes (not MT)
    return ["{base}/{file}".format(base=base, file=f) for f in files]
