.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://github.com/scailfin/rob-client/blob/master/LICENSE


.. figure:: https://github.com/scailfin/rob-client/blob/flowserv/docs/graphics/header-client.png
  :align: center
  :alt: ROB Command Line Interface



About
=====

The **Reproducible Benchmark Client** is the command line user interface for the *Reproducible Open Benchmarks for Data Analysis Platform (ROB)*. The command line interface interacts with a ROB Web API to create, access, and manipulate users, benchmark submissions and benchmark runs.


Installation and Configuration
==============================

The following installation instructions assume that you install all packages in a local folder `~/projects/rob`.

.. code-block:: bash

    # -- Change the working directory

    cd ~/projects/rob


The Reproducible Open Benchmarks platform is implemented in Python. We recommend using a `virtual environment <https://virtualenv.pypa.io/en/stable/>`_ for the installation.

.. code-block:: bash

    # -- Create a new virtual environment
    virtualenv venv
    # -- Activate the virtual environment
    source venv/bin/activate


The ROB Client requires the ``flowserv`` package as well as a `Web API Server <https://github.com/scailfin/rob-webapi-flask>`_. The following steps will install the ROB client and all required packages:


.. code-block:: bash

    git clone git@github.com:scailfin/flowserv-core.git
    pip install -e rob-core
    git clone git@github.com:scailfin/rob-client.git
    pip install -e rob-client


The primary configuration parameters are defined in the `ROB Configuration documentation <https://github.com/scailfin/rob-core/blob/master/docs/configuration.rst>`_. In particular, the environment variables **FLOWSERV_API_HOST**, **FLOWSERV_API_PORT**, and **FLOWSERV_API_PATH** are used to define the base URL for the API that is used for client requests. Three additional environment variables are defined by the client:

- **ROB_ACCESS_TOKEN**: Access token for the user obtained after authentication
- **ROB_BENCHMARK**: Identifier of the default benchmark
- **ROB_SUBMISSION**: Identifier of the default submission



Command Line Interface
======================

To get an overview of the commands that are available via the command line interface use ``rob --help``.

.. code-block:: console

    Usage: rob [OPTIONS] COMMAND [ARGS]...

    Options:
      --raw   Show raw (JSON) response
      --help  Show this message and exit.

    Commands:
      benchmarks   Add and remove benchmarks.
      files        Upload, download, list and delete submission files.
      login        Login to to obtain access token.
      logout       Logout from current user session.
      pwd          Reset user password.
      register     Register a new user.
      runs         Create, query and delete submission runs.
      submissions  Create, modify, query and delete benchmark submissions.
      users        List all registered users.
      whoami       Print name of current user.


For more detailed examples of how to use the ROB Client please have a look at the documentation in the demo repositories `Hello World Demo <https://github.com/scailfin/rob-demo-hello-world>`_ and `Number Predictor Demo <https://github.com/scailfin/rob-demo-predictor>`_.
