import contextlib
import os
import importlib


@contextlib.contextmanager
def cd(path):
  """
  A context manager which changes the working directory to the given
  path, and then changes it back to its previous value on exit.
  """
  prev_cwd = os.getcwd()
  os.chdir(path)
  try:
    yield
  finally:
    os.chdir(prev_cwd)

def memoize(f):
  """
  Memoization decorator for a function taking one or more arguments.
  """
  class memodict(dict):
    def __getitem__(self, *key):
      return dict.__getitem__(self, key)

    def __missing__(self, key):
      ret = self[key] = f(*key)
      return ret

  return memodict().__getitem__

def load_class(full_class_string):
  """
  Dynamically load a class from a string.
  """
  class_data = full_class_string.split(".")
  module_path = ".".join(class_data[:-1])
  class_str = class_data[-1]

  module = importlib.import_module(module_path)
  # Finally, we retrieve the Class
  return getattr(module, class_str)
