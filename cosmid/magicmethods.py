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
