#!/usr/bin/env python

import yaml
from path import path


class DefaultReader(object):
  """docstring for DefaultReader"""
  def __init__(self, yaml_path):
    super(DefaultReader, self).__init__()
    self.path = path(yaml_path)
    self.resources = {}

    # Load in the resources listed in the YAML file
    self.load()

  def load(self, yaml_path=None):
    if yaml_path:
      self.path = path(yaml_path)

    if self.path.exists():
      with open(self.path, "r") as handle:
        self.resources = yaml.safe_load(handle.read()) or {}

    else:
      raise IOError("No such file found: " + self.path)

    return self

  def add(self, resource_id, version):
    self.resources[resource_id] = version

    return self

  def __iter__(self):
    return iter(self.resources.iteritems())

  def save(self):
    with open(self.path, "w") as handle:
      handle.write(yaml.safe_dump(self.resources, default_flow_style=False))

    return self

  def find(self, resource_id=None, default=None):
    if resource_id is None:
      # Return all
      return self.resources
    else:
      return self.resources.get(resource_id, default)


class HistoryReader(DefaultReader):
  """docstring for HistoryReader"""
  def __init__(self, path):
    super(HistoryReader, self).__init__(path)

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
    # Exclude perfect target<->version matches
    # If force is selected we include all resources
    return {key:item["target"] for key, item in self.resources.iteritems()
            if item["target"] != item["version"] or force}
