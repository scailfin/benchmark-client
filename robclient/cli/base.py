# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface for the Reproducible Open Benchmark Web API."""

import click

from flowserv.service.api import HEADER_TOKEN
from robclient.route import UrlFactory

import robclient.cli.benchmark as benchmark
import robclient.cli.files as file
import robclient.cli.run as run
import robclient.cli.submission as submission
import robclient.cli.user as user
import robclient.config as config


@click.group()
@click.option(
    '--raw',
    is_flag=True,
    default=False,
    help='Show raw (JSON) response'
)
@click.pass_context
def cli(ctx, raw):
    """Command Line Interface for the Reproducible Open Benchmark Web API."""
    # Ensure that ctx.obj exists and is a dict. Based on
    # https://click.palletsprojects.com/en/7.x/commands/#nested-handling-and-contexts
    ctx.ensure_object(dict)
    # Set the raw output flag and initialize the url factory in the context
    # object. The API base url is expected to be set in the environment
    # variable 'FLOWSERV_API_HOST'.
    ctx.obj['RAW'] = raw
    ctx.obj['URLS'] = UrlFactory(base_url=config.API_URL())
    ctx.obj['HEADERS'] = {HEADER_TOKEN: config.ACCESS_TOKEN()}


# -- User Commands ------------------------------------------------------------

# Users
cli.add_command(user.list)
cli.add_command(user.login)
cli.add_command(user.logout)
cli.add_command(user.register)
cli.add_command(user.reset_password)
cli.add_command(user.whoami)
# Benchmarks
cli.add_command(benchmark.benchmarks)
# Files
cli.add_command(file.files)
# Runs
cli.add_command(run.runs)
# Submissions
cli.add_command(submission.submissions)
