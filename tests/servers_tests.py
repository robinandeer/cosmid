from nose.tools import *
from genie.servers import Ensembl, NCBI, GATK, UCSC
import fnmatch


class Test_Ensembl(object):
  """docstring for Test_Ensembl"""
  def __init__(self):
    super(Test_Ensembl, self).__init__()

    self.ftp = Ensembl()

  def test_get_assembly(self):
    result = self.ftp.save("assembly").to("./data/").named("assembly.fa.gz")\
                     .commit(dry=True)

    # Check that we found the expected file on the server
    assert_equal(result["fileNames"],
                 ["Homo_sapiens.GRCh37.72.dna.primary_assembly.fa.gz"])

    # Gzipped files are binary, check mode
    assert_equal(result["mode"], "b")

  def test_get_gtf(self):
    result = self.ftp.save("gtf").to("./data/").named("Homo_sapiens.gtf.gz")\
                     .commit(dry=True)

    # Check that we found the expected file on the server
    assert_equal(result["fileNames"], ["Homo_sapiens.GRCh37.72.gtf.gz"])

class Test_NCBI(object):
  """docstring for Test_NCBI"""
  def __init__(self):
    super(Test_NCBI, self).__init__()

    self.ftp = NCBI()

  # def test_get_genbank(self):
  #   # Get the filenames of all chromosome assemblies
  #   files = self.ftp.getPath("genbank")

  #   # Test that we find all chromosome files
  #   assert_equal(len(files), 24)

  #   # Test that all files follow the same pattern
  #   for item in files:
  #     assert_true(fnmatch.fnmatch(item, "chr*.fa.gz"))

  # def test_get_assembly(self):
  #   # Get the filenames of all chromosome assemblies
  #   files = self.ftp.getPath("assembly")

  #   # Test that we find all chromosome files (+MT)
  #   assert_equal(len(files), 25)

  #   # Test that all files follow the same pattern
  #   for item in files:
  #     assert_true(fnmatch.fnmatch(item, "hs_ref_GRCh37.p10_*.fa.gz"))

  def test_get_ccds(self):
    result = self.ftp.save("ccds").to("./data/").named("CCDS.txt")\
                     .commit(dry=True)

    assert_equal(result["fileNames"], ["CCDS.current.txt"])
    assert_equal(result["mode"], "a")


class Test_GATK(object):
  """docstring for Test_GATK"""
  def __init__(self):
    super(Test_GATK, self).__init__()

    self.ftp = GATK()

  def test_get_1000g(self):
    result = self.ftp.save("1000g").commit(dry=True)

    assert_equal(result["fileNames"], ["1000G_omni2.5.b37.vcf.gz"])

  def test_get_indels(self):
    result = self.ftp.save("indels").commit(dry=True)

    assert_equal(result["fileNames"], ["1000G_phase1.indels.b37.vcf.gz"])

  def test_get_mills(self):
    result = self.ftp.save("mills").commit(dry=True)

    assert_equal(result["fileNames"], ["Mills_and_1000G_gold_standard.indels.b37.vcf.gz"])

  def test_get_dbsnp(self):
    result = self.ftp.save("dbsnp").commit(dry=True)

    assert_equal(result["fileNames"], ["dbsnp_137.b37.vcf.gz"])

  def test_get_hapmap(self):
    result = self.ftp.save("hapmap").commit(dry=True)

    assert_equal(result["fileNames"], ["hapmap_3.3.b37.vcf.gz"])

  def test_get_dbsnpex(self):
    result = self.ftp.save("dbsnpex").commit(dry=True)

    assert_equal(result["fileNames"], ["dbsnp_137.b37.excluding_sites_after_129.vcf.gz"])


class Test_UCSC(object):
  """docstring for Test_UCSC"""
  def __init__(self):
    super(Test_UCSC, self).__init__()

    self.ftp = UCSC()

  def test_get_assembly(self):
    result = self.ftp.save("assembly").commit(dry=True)

    assert_equal(result["fileNames"], ["chromFa.tar.gz"])
