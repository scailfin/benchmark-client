# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with benchmarks."""

import click
import json
import requests

from robclient.io import ResultTable

import robclient.config as config
import robcore.model.template.parameter.declaration as pd
import robcore.view.labels as labels


@click.group(name='benchmarks')
def benchmarks():
    """Add and remove benchmarks."""
    pass


# -- Get benchmark handle ------------------------------------------------------

@click.command(name='show')
@click.pass_context
@click.option('-b', '--benchmark', required=False, help='Benchmark identifier')
def get_benchmark(ctx, benchmark):
    """Show benchmark information."""
    b_id = benchmark if benchmark else config.BENCHMARK_ID()
    if b_id is None:
        click.echo('no benchmark specified')
        return
    url = ctx.obj['URLS'].get_benchmark(b_id)
    try:
        r = requests.get(url)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            click.echo('{} ({})'.format(body[labels.NAME], body[labels.ID]))
            if labels.DESCRIPTION in body:
                click.echo('\n{}'.format(body[labels.DESCRIPTION]))
            if labels.INSTRUCTIONS in body:
                click.echo('\n{}'.format(body[labels.INSTRUCTIONS]))
            click.echo('\nParameters:')
            for p in body.get(labels.PARAMETERS, list()):
                name = p[labels.NAME]
                data_type = p[pd.LABEL_DATATYPE]
                click.echo('  {} ({})'.format(name, data_type))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- List benchmarks -----------------------------------------------------------

@click.command(name='list')
@click.pass_context
def list_benchmarks(ctx):
    """List all benchmarks."""
    url = ctx.obj['URLS'].list_benchmarks()
    try:
        r = requests.get(url)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            table = ResultTable(['ID', 'Name', 'Description'], [pd.DT_STRING] * 3)
            for b in body[labels.BENCHMARKS]:
                table.add([b[labels.ID], b[labels.NAME], b[labels.DESCRIPTION]])
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Get benchmark leaderboard--------------------------------------------------

@click.command(name='leaders')
@click.option('-b', '--benchmark', required=False, help='Benchmark identifier')
@click.option(
    '-a', '--all',
    is_flag=True,
    default=False,
    help='Show all run results'
)
@click.pass_context
def get_leaderboard(ctx, benchmark, all):
    """Show benchmark leaderboard."""
    b_id = benchmark if benchmark else config.BENCHMARK_ID()
    if b_id is None:
        click.echo('no benchmark specified')
        return
    url = ctx.obj['URLS'].get_leaderboard(b_id, include_all=all)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            headline = ['Rank', 'Submission']
            types = [pd.DT_INTEGER, pd.DT_STRING]
            for col in body[labels.SCHEMA]:
                headline.append(col[labels.NAME])
                types.append(col[labels.DATA_TYPE])
            table = ResultTable(headline=headline, types=types)
            rank = 1
            for run in body[labels.RANKING]:
                row  = [str(rank), run[labels.SUBMISSION][labels.NAME]]
                result = dict()
                for val in run[labels.RESULTS]:
                    result[val[labels.ID]] = val[labels.VALUE]
                for col in body[labels.SCHEMA]:
                    col_id = col[labels.ID]
                    row.append(str(result[col_id]))
                table.add(row)
                rank += 1
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


benchmarks.add_command(get_benchmark)
benchmarks.add_command(list_benchmarks)
benchmarks.add_command(get_leaderboard)
