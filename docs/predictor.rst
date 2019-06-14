============================
Simple Number Predictor Demo
============================

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://github.com/scailfin/benchmark-client/blob/master/LICENSE


The **Simple Number Predictor Demo** is part of the *Reproducible Open Benchmarks for Data Analysis Platform (ROB)*. The aim of this demo is to show the basic feature of the benchmark engine that allows users to provide their own implementation for individual workflow steps.


===============
Getting Started
===============

Follow the `setup instructions <https://github.com/scailfin/benchmark-client/blob/master/README.rst>`_ before going through the steps of this demo. The shown commands assume that the current working directory is ``~/projects/open-benchmarks`` and that the virtual environment is activated:

.. code-block:: bash

   cd ~/projects/open-benchmarks
   source ~/.venv/rob/bin/activate


The source code and input files for the demo are `included in the repository <https://github.com/scailfin/benchmark-client/tree/master/examples/predictor>`_. The idea is very simple. The predictor model is shown five sequences of five numbers each. For each sequence it *predicts* the next number. The resulting five predictions are written to an output file. The benchmark result is computed as the deviation of the predicted values from the actual values. Note that all values are hand-picked for the purpose of this demo and there is no further logic involved.


======================
Register the Benchmark
======================

The first step is to register the benchmark template with the benchmark engine. To register a benchmark we point to the directory that contains the benchmark template and the static files for the workflow. Each benchmark has a unique name. Internally, the system will also assignt it a unique identifier. This identifier is used by successive commands that interact with the benchmark. In order to avoid having to type the benchmark identifier you can set the environment variable ROB_BENCHMARK to contain the benchmark identifier. Use the following command to create a new benchmark and set the environment variable ROB_BENCHMARK to the identifier of the created benchmark.

.. code-block:: bash

    eval $(rob benchmark create --name "Simple Number Predictor" --src "benchmark-client/examples/predictor/template/")


The ``benchmark show`` command shows the input parameters for the benchmark. For this benchmark the only parameter is a pointer to a python script that reads the provided input and writes the predicted values to an output file.

.. code-block:: bash

    rob benchmark show

.. code-block:: console

    Identifier  : f426b3eb
    Name        : Simple Number Predictor

    Parameters:
      Code file (file)

The benchmark template file contains the declaration of the benchmark parameter and references to the parameter using the ``$[[code]]`` syntax.

.. code-block:: yaml

    workflow:
        version: 0.3.0
        inputs:
          files:
            - $[[code]]
            - code/analyze.py
            - data/sequences.txt
          parameters:
            codefile: code/predict.py
            inputfile: data/sequences.txt
            outputfile: results/predict.txt
        workflow:
          type: serial
          specification:
            steps:
              - environment: 'python:3.7'
                commands:
                  - python code/predict.py
                      --inputfile "${inputfile}"
                      --outputfile "${outputfile}"
                  - python code/analyze.py
                      --inputfile "${outputfile}"
                      --outputfile results/analytics.json
        outputs:
          files:
           - results/predict.txt
           - results/analytics.json
    parameters:
        - id: code
          name: 'Code file'
          datatype: file
          as: code/predict.py
    results:
        file: results/analytics.json
        schema:
            - id: avg_diff
              name: 'Deviation'
              type: decimal
              sortOrder: asc
            - id: exact_match
              name: 'Exact Predictions'
              type: int


The repository provides three different implementations for the predictor:

- `maxpredictor.py <https://github.com/scailfin/benchmark-client/blob/master/examples/predictor/code/maxpredictor.py>`_: The predicted output is the maximum of the seen values plus 1
- `medianpredictor.py <https://github.com/scailfin/benchmark-client/blob/master/examples/predictor/code/medianpredictor.py>`_: The predicted output is the median of the seen values plus 1
- `minpredictor.py <https://github.com/scailfin/benchmark-client/blob/master/examples/predictor/code/minpredictor.py>`_: The predicted output is the minimum of the seen values minus 1


=================
Run the Benchmark
=================

In the following we will switch between **alice** and **bob** to simulate different users participating in the benchmark. **alice** runs the benchmark using the *maxpredictor* and **bob** uses the *minpredictor*.

.. code-block:: bash

    # Login as alice
    eval $(rob login -u alice -p mypwd)
    # Run benchmark with maxpredictor
    rob benchmark run

.. code-block:: console

    Code file (file): benchmark-client/examples/predictor/code/maxpredictor.py

.. code-block:: bash

    # Login as bob
    eval $(rob login -u bob -p mypwd)
    # Run the hello world benchmark
    rob benchmark run

.. code-block:: console

    Code file (file): benchmark-client/examples/predictor/code/minpredictor.py

A look at the current leaderboard confirm that the *minpredictor* has superior results over the *maxpredictor*.

.. code-block:: bash

    rob benchmark leaders

.. code-block:: console

    Rank | User  | Deviation | Exact Predictions
    -----|-------|-----------|------------------
       1 | bob   |       2.2 |                 2
       2 | alice |       4.8 |                 0


**alice** then runs the benchmark again but this time using the *medianpredictor*. Looking at the leaderboard we see that the *medianpredictor* is the one that outperforms the other two.

.. code-block:: bash

    # Login as alice
    eval $(rob login -u alice -p mypwd)
    # Run the hello world benchmark
    rob benchmark run

.. code-block:: console

    Code file (file): benchmark-client/examples/predictor/code/medianpredictor.py

.. code-block:: bash

    rob benchmark leaders

.. code-block:: console

    Rank | User  | Deviation | Exact Predictions
    -----|-------|-----------|------------------
       1 | alice |       1.2 |                 1
       2 | bob   |       2.2 |                 2
