#!/usr/bin/env python
from ..core import FTP

class NCBI(FTP):
  """docstring for NCBI"""
  def __init__(self):
    super(NCBI, self).__init__("ftp.ncbi.nlm.nih.gov", "anonymous", "")
