#!/usr/bin/env python
"""GenBank - reference human genome assembly."""

from ..resource import BaseResource
from ..servers.ncbi import NCBI
import sh


class Resource(BaseResource):
  """docstring for CCDS Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "genbank"

    self.ftp = NCBI()
    self.baseUrl = ("genbank/genomes/Eukaryotes/vertebrates_mammals/"
                    "Homo_sapiens")

    self.parts = 24
    self.names = ["Genbank.Homo_sapiens.{chrom}.fa.gz".format(chrom=chrom)
                  for chrom in range(1, 23) + ["X", "Y"]]

  def versions(self):
    return [dirName for dirName in self.ftp.listFiles(self.baseUrl, "GRCh*")]

  def latest(self):
    # Extract assembly and patch number
    versions = [(int(v[4:6]), int(v[8:] or 0)) for v in self.versions()]

    # Sort based on assembly and patch => return the last item
    combo = sorted(versions, key=lambda x: (x[0], x[1]))[-1]

    # Compose version string
    version = "GRCh{v}".format(v=combo[0], patch=combo[1])

    # Only add patch extention for numbers > 0
    if combo[1] != 0:
      version += ".p" + combo[1]

    return version

  def newer(self, current, challenger):
    # Extract assembly and patch number
    combos = [(int(v[4:6]), int(v[8:] or 0)) for v in (current, challenger)]

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

  def postClone(self, cloned_files, target_dir, version):
    """
    .. versionadded:: 0.3.0
    """
    # Start by extracting all the files
    for f in cloned_files:
      # GunZIP the file (and remove the archive)
      sh.gunzip(f)

    # Then let's concat them
    target_path = "{}/Genbank.Homo_sapiens.fa".format(target_dir)
    # Remove ".gz" ending to point to extracted files
    cat_args = [f[:-3] for f in cloned_files]

    # Execute the concatenation in the background and write to the target path
    sh.cat(*cat_args, _out=target_path, _bg=True)
