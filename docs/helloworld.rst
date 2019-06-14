==========================
Hello World Benchmark Demo
==========================

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://github.com/scailfin/benchmark-client/blob/master/LICENSE


The **Hello World Benchmark Demo** is part of the *Reproducible Open Benchmarks for Data Analysis Platform (ROB)*. This aim is to show the basic features of the benchmark engine and client.


===============
Getting Started
===============

Follow the `setup instructions <https://github.com/scailfin/benchmark-client/blob/master/README.rst>`_ before going through the steps of this demo. The shown commands assume that the current working directory is ``~/projects/open-benchmarks`` and that the virtual environment is activated:

.. code-block:: bash

   cd ~/projects/open-benchmarks
   source ~/.venv/rob/bin/activate


The source code and input files for the demo are `included in the repository <https://github.com/scailfin/benchmark-client/tree/master/examples/helloworld>`_. The example is adopted from the `REANA Hello World Demo <https://github.com/reanahub/reana-demo-helloworld>`_. the workflow has a single step that takes a text file with person names as input, together with a greeting phrase, and a sleep time. For each name in the input file a greeting will be written to an output file that is the concatenation of the greeting phrase and the name. For the purpose of this demo the result file is then analyzed and the average number of character per output line together with the longest output line are calculated as `benchmark results`. The first value is used to create a leaderboard. The input file that contains the person names is part of the input parameters for the benchmark.


======================
Register the Benchmark
======================

The first step is to register the benchmark template with the benchmark engine. To register a benchmark it is sufficient to point to the directory that contains the benchmark template and all static files. Each benchmark has a unique name. Internally, the system will also assignt it a unique identifier. This identifier is used by successive commands that interact with the benchmark. In order to avoid having to type the benchmark identifier you can set the environment variable ROB_BENCHMARK to contain the benchmark identifier. Use the following command to create a new benchmark and set the environment variable ROB_BENCHMARK to the identifier of the created benchmark.

.. code-block:: bash

    eval $(rob benchmark create --name "Hello World" --src "benchmark-client/examples/helloworld/")


Use the ``benchmark show`` command to verify that the benchmark was created and your environment variable is set. This should print the benchmark identifier and name as well as the input parameters (note that the bechmark identifier is likely to be different to the one shown below).

.. code-block:: bash

    rob benchmark show

.. code-block:: console

    Identifier  : 7fb14b10
    Name        : Hello World

    Parameters:
      greeting (string)
      Input file (file)
      sleeptime (int)


=================
Run the Benchmark
=================

Before running a benchmark the user has to be logged in. In the following we will switch between **alice** and **bob** to simulate different users participating in the benchmark.

.. code-block:: bash

    # Login as alice
    eval $(rob login -u alice -p mypwd)
    # Run the hello world benchmark
    rob benchmark run

.. code-block:: console

    greeting (string) [default 'Hello']:
    Input file (file): benchmark-client/examples/helloworld/data/names.txt
    sleeptime (integer) [default 10]: 1

When we run the benchmark the system prompts the user to input values for each of the benchmark parameters. Here we accept the default value for the greeting phrase (type <return>), use the default names.txt file that is provided with as part of the repository, and use a sleeptime of 1 sec.

Now it is **bob**'s turn. For **bob** we use the same input file but provide a longer greeting phrase.

.. code-block:: bash

    # Login as bob
    eval $(rob login -u bob -p mypwd)
    # Run the hello world benchmark
    rob benchmark run

.. code-block:: console

    greeting (string) [default 'Hello']: Welcome
    Input file (file): benchmark-client/examples/helloworld/data/names.txt
    sleeptime (integer) [default 10]: 1

To show the current leaderboard for a benchmark use the following command:

.. code-block:: bash

    rob benchmark leaders

.. code-block:: console

    Rank | User  | Avg. Characters per Line | Max. Output Line Length | Longest Output Line
    -----|-------|--------------------------|-------------------------|--------------------
       1 | bob   |                     13.0 |                    14.0 | Welcome Alice!
       2 | alice |                     11.0 |                    12.0 | Hello Alice!


We then run the benchmark again for **alice** but use an input file with longer names this time. We still use the default greeting phrase but after this run **alice** is on top of the leaderboard.

.. code-block:: bash

    # Login as alice
    eval $(rob login -u alice -p mypwd)
    # Run the hello world benchmark
    rob benchmark run

.. code-block:: console

    greeting (string) [default 'Hello']:
    Input file (file): benchmark-client/examples/helloworld/data/long-names.txt
    sleeptime (integer) [default 10]: 1

.. code-block:: bash

    rob benchmark leaders

.. code-block:: console

    Rank | User  | Avg. Characters per Line | Max. Output Line Length | Longest Output Line
    -----|-------|--------------------------|-------------------------|--------------------
       1 | alice |                     15.0 |                    15.0 | Hello Dorothea!
       2 | bob   |                     13.0 |                    14.0 | Welcome Alice!

The leaderboard will only show the best result for each user. To see all previous run results use:

.. code-block:: bash

    rob benchmark leaders --all

.. code-block:: console

    Rank | User  | Avg. Characters per Line | Max. Output Line Length | Longest Output Line
    -----|-------|--------------------------|-------------------------|--------------------
       1 | alice |                     15.0 |                    15.0 | Hello Dorothea!
       2 | bob   |                     13.0 |                    14.0 | Welcome Alice!
       3 | alice |                     11.0 |                    12.0 | Hello Alice!
