.. image:: assets/cosmid-logo.png
  :alt: Cosmid logo
  :align: center

There's a wealth of publicly available genomics resources; assemblies, database dumps, sample data etc. Problem is, they are spread across various FTP servers all over the world. Cosmid can help you find, clone and manage resources, including a quick way to keep up-to-date on the latest releases.

.. code-block:: console

  # Clone the UCSC Human genome assembly
  $ cosmid clone ucsc_assembly

  # Clone all resources listed in 'cosmid.yaml'
  $ cat cosmid.yaml
  directory: resources
  resources:
    ccds: Hs103
    hapmap: latest
  $ cosmid clone
  # ... downloads CCDS and HapMap to the 'resources' directory


Getting started
----------------
You can easily install `Cosmid` by running:

.. code-block:: console
  
  $ pip install cosmid

`Cosmid` relies on a YAML-formatted config file 'cosmid.yaml' in the current working directory. To create this file you can run:

.. code-block:: console

  $ cosmid init

This will walk you through the nessesary steps to create a basic config file that could look a little something like this:

.. code-block:: yaml

  email: myname@example.com
  directory: resources
  resources:
    example: 2.3

* ``email`` is required for some FTP-servers as a kind of volountary authentication.

* ``directory`` should be a path pointing to the folder where you would like `Cosmid` to store the cloned resources.

* ``resources`` is `dictionary`-like structure where with the format: ``<resource_id>: <target_version>``. If you would like the resource to stay up-to-date on the latest releases you should specify "latest".


Search for resources
--------------------
The number of available resources will grow over time. To search the current roster:

.. code-block:: console

  $ cosmid search <query>


Clone resources
----------------
There are a few ways to clone resources. The simplest is to list the resource IDs you would like to clone.

.. code-block:: console

  $ cosmid clone ccds#Hs103 example

Adding "#" is how you specify a specific version version of the resource to download. Unless you specify a version, the latest release will be selected.

It's recommended to create a project config file (see *Getting started*) where you store all the managed resources. This is useful as a separeate (and parsable) reference for the project "dependencies". You can also install all resources with a simple command:

.. code-block:: console

  $ cosmid clone

To both clone and add a resource to your 'cosmid.yaml' config file you simply have to supply the ``--save`` flag.

.. code-block:: console

  $ cosmid clone ccds#Hs103 example --save

This command will add/update 2 resources to the config file.

.. code-block:: yaml

  email: myname@example.com
  directory: resources
  resources:
    ccds: Hs103
    example: latest


Use cloned resources
---------------------
Cloning a resource will download it to the specified `directory` in your config file. By default `Cosmid` saves resources to a `resources` folder in your current working directory.

Each resource is thereafter added within it's own subfolder matching the resource ID you used when cloning it.

Note
~~~~~
You will probably notice that `Cosmid` generally doesn't include release/version information in the resource filename. E.g. the CCDS_ database would simply be called "CCDS.txt". This way you can always reference one specific filename for a given resource no matter the actual version.

This decision is by design to separate concern as `Cosmid` manages which version of a resource that is currently in downloaded. This information is stored in a history file ".cosmid.yaml" in the root resources `directory`. This file *shouldn't be altered manually* unless you know what you are doing.


Update cloned resources
------------------------
You can update all cloned resources or specify a list of resources to update. `Cosmid` will only attempt to update resources with *non-specific* target versions like "latest".

.. code-block:: console

  $ cosmid update [<resource_id>...]


Registering a resource
-----------------------
Do you have a request for a resource you would like to see added to the registry? Unlike similar tools (e.g. bower_) `Cosmid` doesn't have an easy way to define new resources.

This is mostly because of the complete lack of standardization when it comes to file structure on FTP-servers, specifiying different resource versions etc. The best I can do until a better solution is ideated/presented to me, is to open a `GitHub issue`_ where you specify the nessesary information. I will then do my best to add the resource to the registry.

Note
~~~~~~
If you really feel like helping out and have decent Python skills it should be very difficult to add your own resource (in the shape of a .py file). Simply open a pull request for me to ensure no funny business. More extensive documentation on the Python API will come in the near future.


Background
-----------
Cosmid is heavily inspired by bower_, "a package manager for the web".


Why 'Cosmid'?
--------------
Cosmids_ are often used as cloning vectors. `Cosmid` (program) lets you "clone" various genomics resources for use in your own projects. Get it? :)


Authors
--------
Robin Andeer (me)


Licence
---------
Copyright 2013 Robin Andeer

Licensed under the MIT License


.. _bower: http://bower.io/
.. _CCDS: http://www.ncbi.nlm.nih.gov/CCDS/CcdsBrowse.cgi
.. _Cosmids: http://en.wikipedia.org/wiki/Cosmid
.. _GitHub issue: https://github.com/robinandeer/cosmid/issues