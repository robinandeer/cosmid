#!/usr/bin/env python
from ..core import FTP

class GATK(FTP):
  """docstring for NCBI"""
  def __init__(self):
    super(GATK, self).__init__("ftp.broadinstitute.org",
                               "gsapubftp-anonymous", "")
