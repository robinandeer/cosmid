from nose.tools import *  # PEP8 asserts
from cosmid.ftp import FTP


class TestFTP:
  """Testing a remove registry object."""

  def setUp(self):
    self.ftp = FTP()

  def tearDown(self):
    del self.ftp

  def test_connect(self):
    self.ftp.connect(url, username, password)

  def test_attributes(self):
    # Test connecting to a remote registry and set up the basics
    self.registry.connect()

    assert_equal()
