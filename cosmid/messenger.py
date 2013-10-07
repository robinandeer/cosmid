#!/usr/bin/env python

from __future__ import print_function
import sys
from termcolor import colored, cprint


class Messenger(object):
  """docstring for Messenger"""
  def __init__(self, command=None):
    super(Messenger, self).__init__()

    # Who is sending the message?
    self.command = command

  def welcome(self):
    raw = """
     .o88b.  .d88b.  .d8888. .88b  d88. d888888b d8888b. 
    d8P  Y8 .8P  Y8. 88'  YP 88'YbdP`88   `88'   88  `8D 
    8P      88    88 `8bo.   88  88  88    88    88   88 
    8b      88    88   `Y8b. 88  88  88    88    88   88 
    Y8b  d8 `8b  d8' db   8D 88  88  88   .88.   88  .8D 
     `Y88P'  `Y88P'  `8888Y' YP  YP  YP Y888888P Y8888D' 

     {}
    """.format(colored("=================| version 1.0 |=================",
                       "white"))

    print(colored(raw, "cyan"))

  def send(self, message, category=None):
    """
    Main entrypoint
    """
    if category == "warning":
      statement = self.warn()
    elif category == "error":
      statement = self.error()
    elif category == "update":
      statement = self.update()
    else:
      statement = self.note()

    # Print the parts with tab-separation
    print("\t".join((self.command, statement, message)))

  def warn(self):
    return colored("WARN", "yellow", attrs=["bold"])

  def error(self):
    return colored("ERROR", "red", attrs=["bold"])

  def note(self):
    return colored("NOTE", "white", attrs=["bold"])

  def update(self):
    return colored("UPDATE", "green", attrs=["bold"])
