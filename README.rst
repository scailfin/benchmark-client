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
    mkdir ~/projects/rob
    cd ~/projects/rob
    
    # This example uses virtualenv to install all python modules in one environment
    virtualenv ~/.venv/rob
    source ~/.venv/rob/bin/activate

    # Clone the required benchmark repositories and install the python modules they implement
    git clone https://github.com/scailfin/benchmark-templates.git
    pip install -r benchmark-templates/requirements.txt
    pip install -r benchmark-templates/requirements.txt

    git clone https://github.com/scailfin/benchmark-engine.git
    pip install -r benchmark-engine/requirements.txt
    pip install -r benchmark-engine/requirements.txt

    git clone https://github.com/scailfin/benchmark-client.git
    pip install -r benchmark-client/requirements.txt
    pip install -r benchmark-client/requirements.txt
