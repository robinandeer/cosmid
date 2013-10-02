#!/usr/bin/env python

import yaml
from path import path


class YamlReader(object):
  """docstring for YamlReader"""
  def __init__(self, yaml_path):
    super(YamlReader, self).__init__()
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

  def get(self, resource_id, default=None):
    return self.resources.get(resource_id, default)
