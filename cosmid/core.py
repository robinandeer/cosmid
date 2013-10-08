#!/usr/bin/env python

from __future__ import print_function
import ftputil
import fnmatch
import pkgutil

from fuzzywuzzy import process

import resources
from magicmethods import load_class
from yaml_reader import Reader


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
    if fullPath.endswith(".gz") or fullPath.endswith(".bam"):
      mode = "b"
    else:
      # Default mode is to download non-binary files
      mode = "a"

    # Initiate download of the file
    self.ftp.download(fullPath, dest, mode)


class Registry(object):
  """docstring for Registry"""
  def __init__(self, cosmid_path, history_path):
    super(Registry, self).__init__()

    self.project = Reader(cosmid_path)
    self.history = Reader(history_path)

  def get(self, resource_id):
    """
    <public> Returns an instance of the specified resource class. Raises
    ``ImportError`` when failing to import a resource.

    .. code-block:: python

      >>> resource = registry.get("ccds")
      >>> resource.latest()
      'Hs104'

    :param str resource_id: The resource key (name of module)
    :returns: A class instance of the resource
    """
    return load_class("cosmid.resources.{}.Resource".format(resource_id))()
    
  def ls(self):
    """
    <public> Returns a list of resource IDs and docstrings for all the
    included resource modules.

    *Reference*: http://stackoverflow.com/questions/1707709/list-all-the-modules-that-are-part-of-a-python-package

    .. code-block:: python

      >>> registry.ls()
      [('ccds', 'A curated database of generic element'), ...]

    :returns: A list of tuples: ``(resource_id, docstring)``
    :rtype: list
    """
    # Store everything here
    items = []

    prefix = resources.__name__ + "."
    # Fetch all the resource modules
    modules = pkgutil.iter_modules(resources.__path__, prefix)

    # Loop over all resource modules
    for importer, modname, ispkg in modules:
      # Load the `Resource` class for the module
      module = load_class(modname)

      # Save name and docstring
      items.append((modname, module.__doc__))

    return items

  def search(self, query, limit=5):
    """
    <public> Fuzzy matches a query string against each of the resource IDs and
    returns a limited number of results in order of match score.

    .. code-block:: python

      >>> registry.search("asmebly", limit=2)
      [('ensembl_assembly', 68),
       ('ncbi_assembly', 68)]

    :param str query: A string to match against the resource IDs
    :param int limit: (optional) A maximum number of results to return
    :returns: A list of tuples: ``(resource_id, score)`
    :rtype: list
    """
    # List all the available resources
    resources = self.ls()

    # Focus on resource IDs
    resource_ids = [resource[0] for resource in resources]

    # Fuzzy match against the resource IDs and return in order of best match
    return process.extract(query, resource_ids, limit=limit)

  def matchOne(self, target, options, threshold=60):
    """
    <public> Fuzzy matches e.g. a target version tag against a list of options.
    Returns the most likely match if the match score is sufficient.

    .. code-block:: python

      >>> resource = registry.get("ccds")
      >>> registry.matchOne(104, resource.versions())
      'Hs104'

      >>> registry.matchOne("ensembl", registry.ls())
      'ensembl_assembly'

    :param object target: Any Python object to match with
    :param list options: A list of possible options to match against
    :param int threshold: A lower threshold for accepting a best match
    :returns: The object with the best match (unless score is below threshold)
    :rtype: Python object
    """
    # Match against the options and extract the top match only
    result, score = process.extractOne(target, options)

    # Arbitrary lower limit for returning a *mathcing* result
    if score >= threshold:
      return result
    else:
      return None
