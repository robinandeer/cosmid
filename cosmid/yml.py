#!/usr/bin/env python

import yaml
from path import path


class DefaultReader(object):
  """
  A default YAML reader. Allows for safe parsing, basic adding and fetching
  items as well as saving an updated YAML datastructre (``dict``).

  :param str yaml_path: (optional) Path to the YAML file to parse/save to.
  """
  def __init__(self, yaml_path=None):
    super(DefaultReader, self).__init__()
    self.items = {}

    # Load in the resources listed in the YAML file if provided
    if yaml_path:
      self.load(yaml_path)

  def __iter__(self):
    """
    <magic> Shortcut to iterate over all the keys and items.

    :returns: An iterable returning tuples: (key, item)
    """
    return iter(self.items.iteritems())

  def load(self, yaml_path=None):
    """
    <public> Parse a local YAML-formatted file. Raises an ``IOError`` if the
    path doesn't points to an existing file.

    .. code-block:: python

      >>> reader.load("~/Desktop/config.yaml")

    :param str yaml_path: (optional) A path to the YAML file to parse
    :returns: self
    """
    if yaml_path:
      self.source = path(yaml_path)

    if self.source.isfile():
      with open(self.source, "r") as handle:
        # Use safe load to protect from accidentally running malicious
        # functions defined in the YAML file. Limit to simple str/int values.
        self.items = yaml.safe_load(handle.read())

    else:
      # Initialize empty 
      self.items = {}

    return self

  def add(self, key, item):
    """
    <public> Adds an item associated with a key to the bottom level of the
    YAML structure. The item could be any Python object but should be limited
    to simple strings, ints, or dicts of such objects.

    .. code-block:: python

      >>> reader.add("ccds", "Hs104")

    :param object key: Usually a string for use as an association key
    :param object item: Associated ``str``, ``int``, or ``dict``
    :returns: self
    """
    self.items[key] = item

    return self

  def save(self):
    """
    <public> Overwrites the file currently pointed to by the ``path``
    attribute with valid YAML formatting.

    :returns: self
    """
    with open(self.source, "w") as handle:
      handle.write(yaml.safe_dump(self.items, default_flow_style=False))

    return self

  def find(self, key=None, default=None):
    """
    <public> Returns all items or a single item associated with a given key.
    If a given key is not present the `default` object will be returned
    instead.

    .. code-block:: python

      >>> reader.find("ccds", default="latest")

    :param object key: (optional) Usually a string associated with the item
    :param object default: (optional) What to return if the key isn't found
    :returns: Either all items as a ``dict`` or a one matching the key
    """
    if key is None:
      # Return all
      return self.items
    else:
      return self.items.get(key, default)


class HistoryReader(DefaultReader):
  """
  A specialized YAML reader for dealing with Cosmid History files. Inherits
  from ``DefaultReader``.

  :param str yaml_path: Path to the cosmid history file (.cosmid.yaml)
  """
  def __init__(self, yaml_path):
    super(HistoryReader, self).__init__(yaml_path)

  def updateable(self, force=False):
    """
    <public> Returns all resources that could be updated.

    .. code-block:: python

      >>> history.updateable()
      {"ccds": "latest", ...}

    :param bool force: (optional) Include all resources by default
    :returns: A dict with ``{ resource_id: version_tag }``
    :rtype: dict
    """
    resources = {}
    for key, item in self.items.iteritems():

      # Exclude perfect target<->version matches
      # Always include resources with target=latest
      # If force is selected we include all resources
      if item['target'] != item['version'] or force:
        resources[key] = item['target']

    return resources


class ConfigReader(DefaultReader):
  """
  A specialized YAML reader for dealing with Cosmid History files. Inherits
  from ``DefaultReader``.

  :param str yaml_path: Path to the cosmid history file (.cosmid.yaml)
  """
  def __init__(self, yaml_path):
    super(ConfigReader, self).__init__(yaml_path)

  def addResource(self, resource_id, v_target="latest"):
    """
    <public> Adds a resources and version target to the config file.

    :param str resource_id: A valid resource ID
    :param str v_target: (optional) A version target to for the resource
    :returns: self
    """
    resources = self.find("resources", default=None)

    if resources is None:
      # Add the "resources" key first
      self.add("resources", {})

      # Recursively call the function
      self.addResource(resource_id, v_target)

    else:
      # We're good to go!
      resources[resource_id] = v_target

    return self

  def getResource(self, resource_id, default=None):
    """
    <public> Fetches a resource from the config file or returns `default`.

    :param str resource_id: A valid resource ID
    :param object default: (optional) What to return unless the ID matches
    :returns: A dict with a `resource_id`/`target` pair
    """
    resources = self.find("resources", default=None)

    if resources is None:
      return default

    else:
      return resources.get(resource_id, default)
