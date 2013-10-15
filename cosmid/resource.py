#!/usr/bin/env python
"""
A genomics resource.

Each resource is responsible for:
- Fetching a list of availble versions
- Figuring out which the latest version is
- Comparing and determining which of two versions are the latest
- Returning link(s) for the files to download
- Specify binary/gzip/concat options
- Keeps track of what the resource is called locally
"""


class BaseResource(object):
  """
  A Resource represents a local genomics resource that can be on the file
  system or destined to be downloaded.
  """
  def __init__(self):
    super(BaseResource, self).__init__()
    # The server for the resource
    self.server = None

    # The keyword for the resource
    self.id = "resource"

  def versions(self):
    """
    <public> Returns a list of version tags for availble resource versions.
    """
    return []

  def latest(self):
    """
    <public> Returns the version tag for the latest availble version of the
    resource.
    """
    return ""

  def path(self, version):
    """
    <public> Returns the full download path matching the given ``version`` tag.
    """
    return ""

  def postClone(self, cloned_files, target_dir, version):
    """
    <public> This callback method will be called once the files in the resource
    have been successfully downloaded. The paths to the files will be provided
    as a list to the method.

    This can be used as a way to rename, unzip, or concat files; generally
    post process them to prepare them for the user.

    :param list cloned_files: List of paths to the downloaded resource files
    :param str target_dir: Path to resource directory
    :param object version: Version of the resource that was downloaded

    .. versionadded:: 0.3.0
    """
    return 0
