from nose.tools import *
from genie.fetcher import Fetcher


class A(object):
    """docstring for A"""
    def __init__(self):
        super(A, self).__init__()

        self.username = "robin.andeer@gmail.com"

    def setup(self):
        self.fetcher = Fetcher(self.username, project="b2010080")

    def teardown(self):
        self.fetcher = None

    def test_base_ref_path(self):
        assert_equal(self.fetcher.base_ref_path, "/bubo/proj/b2010080/private/wgs_wf_references/")

    def test_this_file_exists(self):
        # Test a file that exists
        assert_true(self.fetcher.this_file_exists(self.fetcher.base_ref_path + "Homo_sapiens.GRCh37.70_nochr.fasta"))

        # Test a file that doesn't exist
        assert_false(self.fetcher.this_file_exists(self.fetcher.base_ref_path + "Homo_sapiens.GRCh37.71_nochr.fasta"))

    def test_connect(self):
        # Username should be "gsapubftp-anonymous"
        ftp = self.fetcher.connect("ftp.broadinstitute.org", "idontbelonghere", "")

        # The connect method should catch the error and return -1
        assert_equal(ftp, -1)

        # Test working login
        ftp = self.fetcher.connect("ftp.broadinstitute.org", "gsapubftp-anonymous", "")

        # Should be the same as the server we provided
        assert_equal(ftp.host, "ftp.broadinstitute.org")

        # Close connection
        ftp.close()
