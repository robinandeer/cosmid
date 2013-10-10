#!/usr/bin/env python
from ..core import FTP

class Ensembl(FTP):
  """docstring for Ensembl"""
  def __init__(self):
    super(Ensembl, self).__init__("ftp.ensembl.org", "anonymous", "")
