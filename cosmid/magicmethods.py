import contextlib
import os
import importlib


@contextlib.contextmanager
def cd(path):
  """A context manager which changes the working directory to the given
  path, and then changes it back to its previous value on exit.

  """
  prev_cwd = os.getcwd()
  os.chdir(path)
  try:
    yield
  finally:
    os.chdir(prev_cwd)

def load_class(full_class_string):
  """
  dynamically load a class from a string
  """

  class_data = full_class_string.split(".")
  module_path = ".".join(class_data[:-1])
  class_str = class_data[-1]

  module = importlib.import_module(module_path)
  # Finally, we retrieve the Class
  return getattr(module, class_str)


class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = "\033[1m"

  def disable(self):
    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''