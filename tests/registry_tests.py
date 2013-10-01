from nose.tools import *  # PEP8 asserts
from cosmid.registry import Registry


class TestRegistry:
  """Testing a remove registry object."""

  def setUp(self):
    self.registry = Registry()

  def tearDown(self):
    del self.resource

  def test_connect(self):
    # Test connecting to a remote registry and set up the basics
    self.registry.connect()

    assert_equal()

  def test_get(self):
    # Test retriving a resource definition
    metadata = self.registry.get("exampleBAM")
