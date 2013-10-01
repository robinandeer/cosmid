from nose.tools import *  # PEP8 asserts
from cosmid.metadata import MetaData


class TestMetaData:
  """Testing a remove registry object."""

  def setUp(self):
    self.metadata = MetaData()

  def tearDown(self):
    del self.metadata

  def test_attributes(self):
    # Test connecting to a remote registry and set up the basics
    self.registry.connect()

    assert_equal()
