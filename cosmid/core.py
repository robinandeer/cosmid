#!/usr/bin/env python

from __future__ import print_function
import ftputil
import fnmatch


class FTP(object):
  """docstring for FTP"""
  def __init__(self, url, username, password):
    super(FTP, self).__init__()
    self.url = url
    self.username = username
    self.password = password

    # Inheriting from the ftputil class doesn't seem to work - wrapping
    # Connect to the FTP server
    self.ftp = ftputil.FTPHost(url, username, password)

    # Shortcuts
    self.ls = self.ftp.listdir
    self.file = self.ftp.file

  def fileSize(self, path):
    return round(self.ftp.path.getsize(path) / float(1000000), 2)

  def listFiles(self, dirPath, pattern):
    return [item for item in self.ftp.listdir(dirPath)
            if fnmatch.fnmatch(item, pattern)]

  def commit(self, fullPath, dest):
    """
    Public: Saves a file from the server to the computer.

    :returns: 0: OK, >0: NOT OK
    """
    # Is the remote file gzipped? (Binary format)
    # Expect all files are of the same format
    if fullPath.endswith(".gz"):
      mode = "b"
    else:
      # Default mode is to download non-binary files
      mode = "a"

    # Initiate download of the file
    self.ftp.download(fullPath, dest, mode)
