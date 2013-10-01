#!/usr/bin/env python

class Resource(object):
  """
  A Resource represents a local genomics resource that can be on the file
  system or destined to be downloaded.
  """
  def __init__(self):
    super(Resource, self).__init__()
    # The version tag used to match with actual release
    self.target = "*"

    # The actual release tag
    self.release = "v0.0.1"

    # The keyword for the resource
    self.keyword = "resource"

    # The filename of the resource
    self.filename = "resource.txt"

    # The source URL for the resource
    self.source = "ftp://ftp.server.com/resource.txt"
