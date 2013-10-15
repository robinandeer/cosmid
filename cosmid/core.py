#!/usr/bin/env python

from __future__ import print_function
import ftputil
import fnmatch
import pkgutil
from path import path
from fuzzywuzzy import process

import resources
from magicmethods import load_class
from yml import ConfigReader, HistoryReader
from messenger import Messenger


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
  def __init__(self):
    super(Registry, self).__init__()

    # Set up YAML parser for optional config file
    self.config_path = path("cosmid.yaml")
    self.config = ConfigReader(self.config_path)

    # Extract stuff from config
    self.email = self.config.find("email")

    # Path to resource storage directory
    self.directory = path(self.config.find("directory", default="resources"))

    # Load history file consisting of already downloaded resources
    self.history_path = path(self.directory + "/.cosmid.yaml")
    self.history = HistoryReader(self.history_path)

    # Set up a :class:`cosmid.messenger.Messenger`
    self.messenger = Messenger("cosmid")

  def get(self, resource_id):
    """
    <public> Returns an instance of the specified resource class. Dodges an
    ``ImportError`` when failing to import a resource and returns ``None``
    instead.

    .. code-block:: python

      >>> resource = registry.get("ccds")
      >>> resource.latest()
      'Hs104'

    :param str resource_id: The resource key (name of module)
    :returns: A class instance of the resource
    """
    try:
      return load_class("cosmid.resources.{}.Resource".format(resource_id))()

    except ImportError:
      return None

  def grab(self, resource_id, target):
    """
    <public> Returns all that's nessesary to download a specific resource.
    The method will try to correct both ``resource_id`` and the ``target``
    release tag.

    :param str resource_id: What resource to download
    :param str target: What release of the resource to download
    """
    # Either import resource class or print warning and move on.
    resource = self.get(resource_id)

    if resource is None:
      message = "Couldn't match resource ID: '{}'".format(resource_id)
      self.messenger.send("warning", message)

      return None, None, None
    
    # Now let's figure out the version
    # No specified version will match to the latest resource release
    if target == "latest":
      version = resource.latest()
    else:
      options = resource.versions()
      version = self.matchOne(target, options)

    if version is None:
      message = ("Couldn't match version '{id}#{v}'; {vers}"
                 .format(v=target, id=resource.id, vers=", ".join(options)))

      self.messenger.send("warning", message)

      return None, None, None

    # Get the goahead! (we haven't already downloaded it)
    if self.goahead(resource, version):

      # Finally we can determine the paths to download and save the files
      dl_paths = resource.paths(version)
      save_paths = [("{dir}/{id}/{file}"
                     .format(dir=self.directory, id=resource.id, file=name))
                    for name in resource.names]

      # Add the resource to the history file as downloaded
      self.history.add(resource_id, {
        "version": version,
        "target": target,
        "names": resource.names,
        "sources": dl_paths
      })

      return resource, dl_paths, save_paths, version

    else:

      # The resource was already downloaded
      return None, None, None


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
      module = self.get(modname)

      # Save name and docstring
      items.append((modname.split(".")[-1], module.__doc__))

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
    result, score = process.extractOne(target, map(str, options))

    # Arbitrary lower limit for returning a *mathcing* result
    if score >= threshold:
      return result
    else:
      return None

  def goahead(self, resource, version):
    """
    Determines whether it's any idea in going ahead with a download.
    """
    # Get any currently downloaded resources
    current = self.history.find(resource.id, default={})

    # Make sure we haven't already download the resource
    if version == current.get("version"):
      message = "Resource already downloaded: '{id}'".format(id=resource.id)
      self.messenger.send("update", message)

      return False

    return True

