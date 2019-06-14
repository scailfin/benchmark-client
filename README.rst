=============================
Reproducible Benchmark Client
=============================

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://github.com/scailfin/benchmark-client/blob/master/LICENSE


About
=====

The **Reproducible Benchmark Client** is the current user interface for the *Reproducible Open Benchmarks for Data Analysis Platform (ROB)*. The client contains a command line interface that can be used to create users and benchmarks for the `Reproducible Benchmark Engine <https://github.com/scailfin/benchmark-engine>`_, and to execute benchmarks and show benchmark results.


Setup
=====

The benchmark client uses the `Reproducible Benchmark Engine <https://github.com/scailfin/benchmark-engine>`_ and the `Workflow Templates for Reproducible for Data Analysis Benchmarks <https://github.com/scailfin/benchmark-templates>`_ repository.


.. code-block:: bash

    # Create a new directory for the project
    mkdir ~/projects/open-benchmarks
    cd ~/projects/open-benchmarks

    # This example uses virtualenv to install all python modules in one environment
    virtualenv ~/.venv/rob
    source ~/.venv/rob/bin/activate

    # Clone the required benchmark repositories and install the python modules they implement
    git clone https://github.com/scailfin/benchmark-templates.git
    pip install -e benchmark-templates/

    git clone https://github.com/scailfin/benchmark-engine.git
    pip install -e benchmark-engine/

    git clone https://github.com/scailfin/benchmark-client.git
    pip install -e benchmark-client/


Configuration
=============

After finishing the setup the command line interface `rob` for *Reproducible Open Benchmarks* should be available when the virtual environment is activated. The client is configured using environment variables. The environment variable `BENCHENGINE_BASEDIR` specifies the path to the directory that will store user information, benchmark templates, and benchmark results. If the variable is not set the client will expect (or create) a folder `.rob` in the current working directory. Here we set the variable to the project directory that we created at the beginning.

.. code-block:: bash

    export BENCHENGINE_BASEDIR=~/projects/open-benchmarks

To test if the command line interface is setup properly type ``rob info``. This should print a message that looks like this:

.. code-block:: console

    Engine API
      Name   : Reproducible Benchmarks for Data Analysis (Development API)
      Version: 0.1.0

Executing the info command should create a new folder ``.rob`` in the open-benchmarks directory. This folder will contain the benchmark templates, benchmark run results, and user information. To get an overview of the commands that are available via the command line interface use ``rob --help``.

.. code-block:: console

    Usage: rob [OPTIONS] COMMAND [ARGS]...
    
      Command Line Interface for Reproducible Benchmarks for Data Analysis API.
    
    Options:
      --raw   Show raw (JSON) response
      --help  Show this message and exit.
    
    Commands:
      benchmark  Add and remove benchmarks.
      info       Print API name and version.
      init       Initialize database for the reproducible benchmark engine API.
      login      Login to to obtain access token.
      logout     Logout from current user session.
      register   Register a new user.
      whoami     Print name of current user.
    


The first step for using the command line interface is to create an instance of the database that is used to store most of the information that the benchmark engine maintains.

.. code-block:: bash

    rob init


Benchmark Examples
==================

For a simple demo of the benchmark engine we start by creating two new users **alice** and **bob** using the follwoing commands:

.. code-block:: bash

    rob register -u alice -p mypwd
    rob register -u bob -p mypwd

Note that the user name (-u) and passowrd (-p) can be omitted. If omitted the command line interface will prompt the user for these values.

Before running any benchmarks a user has to be logged in and obtain an access token. Interface commands that require authentication will expect the access token to be set using the environment variable *ROB_ACCESS_TOKEN*.

.. code-block:: bash

    rob login -u alice -p mypwd

    export ROB_ACCESS_TOKEN=08068e4be7f948d88d1576f5a809eceb


The value of the access token will change with every login. The login command returns the respective export string for the access token. You can use the following command to set the environment variable  right away:

.. code-block:: bash

    eval $(rob login -u alice -p mypwd)

To check whether the access token environment variable is set use ``rob whoami``. Note that access tokens will experia after 24 hours.

For further demos please refer to the `Hello World Benchmark <https://github.com/scailfin/benchmark-client/blob/master/docs/helloworld.rst>`_ and the `Simple Number Predictor Benchmark <https://github.com/scailfin/benchmark-client/blob/master/docs/predictor.rst>`_.




    