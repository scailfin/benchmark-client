"""Helper methods to get command line interface configuration parameters from
the environment.
"""

import os


"""Environment variables for the command line interface."""
# Access token for the command line interface
ENV_ACCESS_TOKEN = 'ROB_ACCESS_TOKEN'
# Identifier of the default benchmark
ENV_BENCHMARK = 'ROB_BENCHMARK'


def access_token():
    """Short-cut to get the value of the access token from the environment.

    Returns
    -------
    string
    """
    return os.environ[ENV_ACCESS_TOKEN]


def benchmark_identifier(default_value=None):
    """Short-cut to get the value for the default benchmark identifier from the
    environment.

    Returns
    -------
    string
    """
    return os.environ.get(ENV_BENCHMARK, default_value)
