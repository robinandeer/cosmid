#!/usr/bin/env python
from ..core import FTP

class ThousandG(FTP):
  """docstring for EBI 1000 Genomes FTP"""
  def __init__(self):
    super(ThousandG, self).__init__("ftp-trace.ncbi.nih.gov", "anonymous", "")
