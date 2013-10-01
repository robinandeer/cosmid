from nose.tools import *  # PEP8 asserts
from cosmid.project import Project


class TestProject:
  """
  An example unit test case.
  """

  def setUp(self):
    self.project = Project("fixtures/cosmid.yaml")

  def tearDown(self):
    del self.project

  def test_load(self):
    # Test (re)loading a YAML file with resources to download
    self.project.load("fixtures/cosmid.yaml")

    assert_equal(self.project.source, "fixtures/cosmid.yaml")

  def test_missing_resources(self):
    # Test examining which resources haven't yet been downloaded
    resources = self.project.missing_resources()

    assert_equal(resources, ["exampleBAM"])

  def test_match_version(self):
    # Test matching a version of a requested file with a downloaded file
    # Test global match (matching anything)
    anything = self.project.match_version("exampleFASTA", v="*")
    assert_true(anything)

    # Test "lastest" match
    lastest = self.project.match_version("exampleFASTA", v="lastest")
    assert_true(lastest)

    # Test approximate matching
    approx = self.project.match_version("exampleFASTA", v="~2.6")
    assert_true(approx)

    # Test exact match
    exact = self.project.match_version("exampleFASTA", v="2.5")
    assert_true(exact)