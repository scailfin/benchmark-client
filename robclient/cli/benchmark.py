# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with benchmarks."""

import click
import json
import os
import requests

from robclient.table import ResultTable

import flowserv.core.util as util
import flowserv.model.parameter.declaration as pd
import robclient.config as config


@click.group(name='benchmarks')
def benchmarks():
    """Add and remove benchmarks."""
    pass


# -- Get benchmark handle -----------------------------------------------------

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
            click.echo('{} ({})'.format(body['name'], body['id']))
            if 'description' in body:
                click.echo('\n{}'.format(body['description']))
            if 'instructions' in body:
                click.echo('\n{}'.format(body['instructions']))
            click.echo('\nParameters:')
            for p in body.get('parameters', list()):
                name = p['name']
                data_type = p[pd.LABEL_DATATYPE]
                click.echo('  {} ({})'.format(name, data_type))
            resources = body.get('postproc', dict()).get('resources')
            if resources is not None:
                click.echo('\nResources:')
                for res in resources:
                    r_id = res['id']
                    r_name = res['name']
                    click.echo('  {} ({})'.format(r_name, r_id))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- List benchmarks ----------------------------------------------------------

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
            table = ResultTable(
                ['ID', 'Name', 'Description'],
                [pd.DT_STRING] * 3
            )
            for b in body['benchmarks']:
                table.add([b['id'], b['name'], b['description']])
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Get benchmark leaderboard------------------------------------------------

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
            for col in body['schema']:
                headline.append(col['name'])
                types.append(col['type'])
            table = ResultTable(headline=headline, types=types)
            rank = 1
            for run in body['ranking']:
                row = [str(rank), run['submission']['name']]
                result = dict()
                for val in run['results']:
                    result[val['id']] = val['value']
                for col in body['schema']:
                    col_id = col['id']
                    row.append(str(result[col_id]))
                table.add(row)
                rank += 1
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Download resource file(s) ------------------------------------------------

@click.command(name='download')
@click.pass_context
@click.option('-b', '--benchmark', required=False, help='Benchmark identifier')
@click.option('-f', '--resource', required=False, help='Resource identifier')
@click.option(
    '-a', '--all',
    is_flag=True,
    default=False,
    help='Download archive'
)
@click.option(
    '-o', '--output',
    type=click.Path(writable=True),
    required=False,
    help='Save as ...'
)
def download_resource(ctx, benchmark, resource, all, output):
    """Download a run resource file."""
    # We cannot have a resource and the all flag being True
    if resource is not None and all:
        click.echo('invalid argument combination')
        return
    elif resource is None and not all:
        click.echo('select resource or all')
        return
    b_id = benchmark if benchmark else config.BENCHMARK_ID()
    urls = ctx.obj['URLS']
    if resource is not None:
        url = urls.download_benchmark_file(
            benchmark_id=b_id,
            resource_id=resource
        )
    else:
        url = urls.download_benchmark_archive(benchmark_id=b_id)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        content = r.headers['Content-Disposition']
        if output is not None:
            filename = output
        elif 'filename=' in content:
            filename = content[content.find('filename='):].split('=')[1]
            if filename.startswith('"') or filename.startswith("'"):
                filename = filename[1:]
            if filename.endswith('"') or filename.endswith("'"):
                filename = filename[:-1]
        else:
            click.echo('not output filename found')
            return
        # Write the file contents in the response to the specified path
        # Based on https://www.techcoil.com/blog/how-to-download-a-file-via-http-post-and-http-get-with-python-3-requests-library/
        targetdir = os.path.dirname(filename)
        if targetdir:
            util.create_dir(targetdir)
        with open(filename, 'wb') as local_file:
            for chunk in r.iter_content(chunk_size=128):
                local_file.write(chunk)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


benchmarks.add_command(get_benchmark)
benchmarks.add_command(list_benchmarks)
benchmarks.add_command(get_leaderboard)
benchmarks.add_command(download_resource)
