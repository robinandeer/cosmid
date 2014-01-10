#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import ftplib
from fnmatch import fnmatch
from StringIO import StringIO
import pkgutil
import importlib
from path import path
from fuzzywuzzy import process

import resources
from magicmethods import load_class
from yml import ConfigReader, HistoryReader
from messenger import Messenger


class FTP(object):
  """
  Model of a basic FTP server. Inherits a few methods from class:`ftplib.FTP`
  as well as extends with a few new methods making it more like `ftputil`.

  .. code-block::

    >>> from cosmid.core import FTP
    >>> ftp = FTP("ftp.ensembl.org", "anonymous", "")
    >>> ftp.ls("")
    ['ls-lR.gz',
     '.message',
     '.ok_to_rsync',
     'pub',
     ...
    ]

  :param str url: URL for the server to connect to
  :param str username: Username for an account on the server
  :param str password: Password to the accound on the server
  """
  def __init__(self, url, username, password):
    super(FTP, self).__init__()
    self.url = url
    self.username = username
    self.password = password

    # Connect to the FTP server
    self.ftp = ftplib.FTP(url, username, password)

    # Shortcuts
    self.nlst = self.ftp.nlst
    self.retrbinary = self.ftp.retrbinary
    self.sendcmd = self.ftp.sendcmd
    self.size = self.ftp.size

  def ls(self, dir_path="."):
    """
    <public> Functions like `ls` in Unix where it lists the folders and files
    in a specific directory. Compared to `nlst` it doesn't return the full
    path for each file/folder.

    :param str dir_path: (optional) Path to directory
    :returns: List of files/folders in the directory
    :rtype: list
    """
    return [path_.split("/")[-1] for path_ in self.nlst(dir_path)]

  def file(self, path):
    """
    <public> Open a file-like object for reading txt-files on the server
    without downloading it locally first.

    :param str path: Path to file
    :returns: File-like object
    :rtype: StringIO object
    """
    r = StringIO()

    self.retrbinary("RETR " + path, r.write)

    # Rewind the "file"
    r.seek(0)

    return r

  def fileSize(self, path):
    """
    <public> Returns the file size of a certain file on the server in MB.

    :param str path: Path to file
    :returns: Size of file in megabytes
    :rtype: int
    """
    # Switch to Binary mode (to be able to get size)
    self.sendcmd("TYPE i")

    return round(self.size(path)/1000000, 2)

  def listFiles(self, dirPath, pattern):
    """
    <public> Like `ls` but has the option to match file/folder names to a
    pattern.

    :param str dirPath: Path to directory
    :param str pattern: Glob-like pattern to match against files
    :returns: List of files/folders in the directory matching the pattern
    :rtype: list
    """
    return [item for item in self.ls(dirPath) if fnmatch(item, pattern)]

  def commit(self, fullPath, dest, mode=None):
    """
    <public>: Saves a file from the server, locally in the `dest`.

    :param str fullPath: Path from the cwd to the file to download
    :param str dest: Local path+filename where you want to save the file
    :param str mode: (optional) "b" for binary files
    :returns: 0: OK, >0: NOT OK
    """
    # Is the remote file gzipped? (Binary format)
    if mode is None:
      if fullPath.endswith(".gz") or fullPath.endswith(".bam"):
        mode = "b"
      else:
        # Default mode is to download non-binary files
        mode = ""

    # Open connection to the destination file and retrive the file
    with open(dest, "w" + mode) as handle:
      self.retrbinary("RETR " + fullPath, handle.write)


class Registry(object):
  """
  Hub of-sorts to talk with different `Cosmid` related files and resources. Can
  be seen as the API endpoint for `Cosmid`.
  """
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

  def get(self, resource_id, type_="class"):
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

      if type_ == "class":
        return load_class("cosmid.resources.{}.Resource".format(resource_id))()

      elif type_ == "module":
        return importlib.import_module("cosmid.resources." + resource_id)

      else:
          raise ValueError("Argument must be either 'class' or 'module'.")

    except ImportError:
      return None

  def grab(self, resource_id, target, collapse=False):
    """
    <public> Returns all that's nessesary to download a specific resource.
    The method will try to correct both ``resource_id`` and the ``target``
    release tag.

    :param str resource_id: What resource to download
    :param str target: What release of the resource to download
    """
    # Either import resource class or print warning and move on.
    # Test matching the resource ID
    options = [item[0] for item in self.ls()]
    resource_id = self.matchOne(resource_id, options)

    if resource_id is None:

      message = "Couldn't match resource ID: '{}'".format(resource_id)
      self.messenger.send("warning", message)

      return None, None, None, None

    # Get the resource
    resource = self.get(resource_id)

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

      return None, None, None, None

    # Get the goahead! (that we haven't already downloaded it)
    if self.goahead(resource, version):

      # Finally we can determine the paths to download and save the files
      dl_paths = resource.paths(version)

      if collapse:
        # The user can select to store all downloaded files in the same
        # directory
        resource_dir = ""

      else:
        # Or by default separate different resources into subdirectories
        resource_dir = "/" + resource.id

      save_paths = [("{dir}{mid}/{file}"
                     .format(dir=self.directory, mid=resource_dir, file=name))
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
      return None, None, None, None

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
    for importer, modpath, ispkg in modules:
      # Strip path
      modname = modpath.split(".")[-1]

      # Load the `Resource` class for the module
      module = self.get(modname, type_="module")

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

    # Make sure we haven't already downloaded the resource
    if current.get("version") == version:
      message = "'{}' already downloaded and up-to-date.".format(resource.id)
      self.messenger.send("update", message)

      return False

    return True
