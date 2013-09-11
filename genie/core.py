#!/usr/bin/env python

from __future__ import print_function
import ftputil
import os
from path import path
import fnmatch


class DB(object):
  def __init__(self, server, dirPath, pattern, dbName, count=1, versions=[]):
    super(DB, self).__init__()
    # Instantiate
    self.server = server
    self.dirPath = path(dirPath)
    self.pattern = pattern
    self.dbName = path(dbName)
    self.count = count
    self.versions = versions


class File(path):
  """
  File: represents a file on a remote server.
  ===============

  url     [str] - Path to directory of the file
  pattern [str] - Unique pattern to select file in directory
  """
  def __init__(self, path, ext="--temp"):
    super(File, self).__init__(path)

    # This is a reference to the temp file (while downloading)
    self.temp = self + ext


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

  def fileSize(self, path):
    return round(self.ftp.path.getsize(path) / float(1000000), 2)

  def listFiles(self, dirPath, pattern):
    return [item for item in self.ftp.listdir(dirPath)
            if fnmatch.fnmatch(item, pattern)]

  def commit(self, fullPath, dest, dry=False):
    """
    Public: Saves a file from the server to the computer.

    :returns: 0: OK, >0: NOT OK
    """
    # Is the remote file gzipped? (Binary format)
    # Expect all files are of the same format
    if fullPath.endswith(".gz"):
      mode = "b"
      ext = ".gz"
    else:
      # Default mode is to download non-binary files
      mode = "a"
      ext = ""

    if not dry:
      # Initiate download of the file
      self.ftp.download(fullPath, dest, mode)
