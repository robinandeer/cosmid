#!/usr/bin/env python
"""A few example BAM/Fasta files for testing provided by GATK."""

from ..resource import BaseResource
from ..servers.gatk import GATK
import sh


class Resource(BaseResource):
  """docstring for exampleBAM Resource"""
  def __init__(self):
    super(Resource, self).__init__()

    self.id = "example"

    self.ftp = GATK()
    self.baseUrl = "bundle"

    self.parts = 4
    self.names = ["exampleBAM.bam", "exampleBAM.bam.bai.gz",
                  "exampleFASTA.fasta.fai.gz", "exampleFASTA.fasta.gz"]

  def versions(self):
    assemblies = ['b36', 'b37', 'hg18', 'hg19']
    versions = self.ftp.ls(self.baseUrl)
    options = []
    for version in versions:
      for assembly in assemblies:
        options.append("{}/{}".format(version, assembly))
    return options

  def defineVersion(self, version_tag, assembly='b37'):
    """
    <public> Determines the tuple representing the 'version' of a GATK bundle
    resource.

    .. versionadded:: 0.4.7

    :param str version_tag: The version string input by user
    :param str assembly: (optional) The default assembly to use if not
                         provided by user
    :returns: Tuple with bundle_id and assembly
    """
    version_parts = version_tag.split('/')
    bundle_id = version_parts[0]

    if '/' in version_tag:
      assembly = version_parts[1]

    return bundle_id, assembly

  def latest(self):
    return max([float(v.split('/')[0]) for v in self.versions()])

  def newer(self, current, challenger):
    # Simply check which float is biggest
    return float(challenger.split('/')[0]) > float(current.split('/')[0])

  def paths(self, version):
    bundle_id, assembly = self.defineVersion(version)

    # 4 files
    base = "{base}/{v}/exampleFASTA".format(base=self.baseUrl, v=bundle_id)

    return ["{base}/{file}".format(base=base, file=f) for f in self.names]

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

    return 0
