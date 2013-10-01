from nose.tools import *  # PEP8 asserts
from cosmid.resource import Resource


class TestResource:
  """Testing a local resource object."""

  def setUp(self):
    self.resource = Resource("exampleFASTA")

  def tearDown(self):
    del self.resource

  def test_load(self):
    # Test (re)loading a YAML file with resources to download
    self.project.load("fixtures/cosmid.yaml")

    assert_equal(self.project.source, "fixtures/cosmid.yaml")
