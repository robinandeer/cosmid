#!/usr/bin/env python
from ..core import FTP

class UCSC(FTP):
  """docstring for UCSC"""
  def __init__(self):
    super(UCSC, self).__init__("hgdownload.cse.ucsc.edu", "anonymous", "email")
