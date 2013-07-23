from nose.tools import *
from genie.servers import Ensembl, NCBI, GATK, UCSC
import fnmatch


class Test_Ensembl(object):
  """docstring for Test_Ensembl"""
  def __init__(self):
    super(Test_Ensembl, self).__init__()

    self.ftp = Ensembl()

  def test_get_assembly(self):
    files = self.ftp.getPath("assembly")
    assert_equal(len(files), 1)
    assert_equal(files[0], "Homo_sapiens.GRCh37.72.dna.primary_assembly.fa.gz")

  def test_get_gtf(self):
    files = self.ftp.getPath("gtf")
    assert_equal(len(files), 1)
    assert_equal(files[0], "Homo_sapiens.GRCh37.72.gtf.gz")

class Test_NCBI(object):
  """docstring for Test_NCBI"""
  def __init__(self):
    super(Test_NCBI, self).__init__()

    self.ftp = NCBI()

  def test_get_genbank(self):
    # Get the filenames of all chromosome assemblies
    files = self.ftp.getPath("genbank")

    # Test that we find all chromosome files
    assert_equal(len(files), 24)

    # Test that all files follow the same pattern
    for item in files:
      assert_true(fnmatch.fnmatch(item, "chr*.fa.gz"))

  def test_get_assembly(self):
    # Get the filenames of all chromosome assemblies
    files = self.ftp.getPath("assembly")

    # Test that we find all chromosome files (+MT)
    assert_equal(len(files), 25)

    # Test that all files follow the same pattern
    for item in files:
      assert_true(fnmatch.fnmatch(item, "hs_ref_GRCh37.p10_*.fa.gz"))

  def test_get_ccds(self):
    files = self.ftp.getPath("ccds")

    assert_equal(len(files), 1)
    assert_equal(files[0], "CCDS.current.txt")


class Test_GATK(object):
  """docstring for Test_GATK"""
  def __init__(self):
    super(Test_GATK, self).__init__()

    self.ftp = GATK()

  def test_get_1000g(self):
    files = self.ftp.getPath("1000g")

    assert_equal(len(files), 1)
    assert_equal(files[0], "1000G_omni2.5.b37.vcf.gz")

  def test_get_indels(self):
    files = self.ftp.getPath("indels")

    assert_equal(len(files), 1)
    assert_equal(files[0], "1000G_phase1.indels.b37.vcf.gz")

  def test_get_mills(self):
    files = self.ftp.getPath("mills")

    assert_equal(len(files), 1)
    assert_equal(files[0], "Mills_and_1000G_gold_standard.indels.b37.vcf.gz")

  def test_get_dbsnp(self):
    files = self.ftp.getPath("dbsnp")

    assert_equal(len(files), 1)
    assert_equal(files[0], "dbsnp_137.b37.vcf.gz")

  def test_get_hapmap(self):
    files = self.ftp.getPath("hapmap")

    assert_equal(len(files), 1)
    assert_equal(files[0], "hapmap_3.3.b37.vcf.gz")

  def test_get_dbsnpex(self):
    files = self.ftp.getPath("dbsnpex")

    assert_equal(len(files), 1)
    assert_equal(files[0], "dbsnp_137.b37.excluding_sites_after_129.vcf.gz")


class Test_UCSC(object):
  """docstring for Test_UCSC"""
  def __init__(self):
    super(Test_UCSC, self).__init__()

    self.ftp = UCSC()

  def test_get_assembly(self):
    files = self.ftp.getPath("assembly")

    assert_equal(len(files), 1)
    assert_equal(files[0], "chromFa.tar.gz")
