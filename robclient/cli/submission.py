# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with benchmark submissions."""

import click
import json
import requests

from flowserv.model.parameter.numeric import PARA_INT
from flowserv.model.parameter.string import PARA_STRING
from robclient.table import ResultTable

import flowserv.util as util
import robclient.config as config


@click.group(name='submissions')
def submissions():
    """Create, modify, query and delete benchmark submissions."""
    pass


# -- Create new submission ----------------------------------------------------

@click.command(name='create')
@click.pass_context
@click.option('-b', '--benchmark', required=False, help='Benchmark identifier')
@click.option('-n', '--name', required=True, help='Submission name')
@click.option('-m', '--members', required=False, help='Submission members')
def create_submission(ctx, benchmark, name, members):
    """Create a new submission."""
    b_id = benchmark if benchmark else config.BENCHMARK_ID()
    if b_id is None:
        click.echo('no benchmark specified')
        return
    url = ctx.obj['URLS'].create_submission(benchmark_id=b_id)
    headers = ctx.obj['HEADERS']
    data = {'name': name}
    if members is not None:
        data['members'] = members.split(',')
    try:
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            s_id = body['id']
            click.echo('export {}={}'.format(config.ROB_SUBMISSION, s_id))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Delete submission --------------------------------------------------------

@click.command(name='delete')
@click.pass_context
@click.option(
    '-s', '--submission',
    required=False,
    help='Submission identifier'
)
def delete_submission(ctx, submission):
    """Delete an existing submission."""
    s_id = submission if submission else config.SUBMISSION_ID()
    if s_id is None:
        click.echo('no submission specified')
        return
    msg = 'Do you really want to delete submission {}'
    if not click.confirm(msg.format(s_id)):
        return
    url = ctx.obj['URLS'].delete_submission(submission_id=s_id)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.delete(url, headers=headers)
        r.raise_for_status()
        click.echo('Submission \'{}\' deleted.'.format(s_id))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Get submission -----------------------------------------------------------

@click.command(name='show')
@click.pass_context
@click.option(
    '-s', '--submission',
    required=False,
    help='Submission identifier'
)
def get_submission(ctx, submission):
    """Show submissions information."""
    s_id = submission if submission else config.SUBMISSION_ID()
    if s_id is None:
        click.echo('no submission specified')
        return
    url = ctx.obj['URLS'].get_submission(s_id)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            members = list()
            for u in body['members']:
                members.append(u['username'])
            click.echo('ID      : {}'.format(body['id']))
            click.echo('Name    : {}'.format(body['name']))
            click.echo('Members : {}'.format(','.join(members)))
            # -- Uploaded files -----------------------------------------------
            click.echo('\nUploaded Files\n--------------\n')
            table = ResultTable(
                headline=['ID', 'Name', 'Created At', 'Size'],
                types=[PARA_STRING, PARA_STRING, PARA_STRING, PARA_INT]
            )
            for f in body['files']:
                table.add([
                    f['id'],
                    f['name'],
                    f['createdAt'][:19],
                    f['size']
                ])
            for line in table.format():
                click.echo(line)
            # -- Runs ---------------------------------------------------------
            click.echo('\nRuns\n----\n')
            table = ResultTable(
                headline=['ID', 'Created At', 'State'],
                types=[PARA_STRING] * 3
            )
            for r in body['runs']:
                table.add([
                    r['id'],
                    r['createdAt'][:19],
                    r['state']
                ])
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- List submissions ---------------------------------------------------------

@click.command(name='list')
@click.pass_context
@click.option(
    '-b', '--benchmark',
    required=False,
    help='Benchmark identifier'
)
def list_submissions(ctx, benchmark):
    """Show submissions for a benchmark or user."""
    b_id = benchmark if benchmark else config.BENCHMARK_ID()
    url = ctx.obj['URLS'].list_submissions(benchmark_id=b_id)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            table = ResultTable(['ID', 'Name'], [PARA_STRING] * 2)
            for s in body['submissions']:
                table.add([s['id'], s['name']])
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Update submission --------------------------------------------------------

@click.command(name='update')
@click.pass_context
@click.option(
    '-s', '--submission',
    required=False,
    help='Submission identifier'
)
@click.option('-n', '--name', required=False, help='Submission name')
@click.option('-m', '--members', required=False, help='Submission members')
def update_submission(ctx, submission, name, members):
    """Create a new submission."""
    if name is None and members is None:
        click.echo('nothing to update')
        return
    s_id = submission if submission else config.SUBMISSION_ID()
    if s_id is None:
        click.echo('no submission specified')
        return
    url = ctx.obj['URLS'].update_submission(submission_id=s_id)
    headers = ctx.obj['HEADERS']
    data = dict()
    if name is not None:
        data['name'] = name
    if members is not None:
        data['members'] = members.split(',')
    try:
        r = requests.put(url, json=data, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            s_id = body['id']
            click.echo('Submission \'{}\' updated.'.format(s_id))
            members = list()
            for u in body['members']:
                members.append(u['username'])
            click.echo('Name    : {}'.format(body['name']))
            click.echo('Members : {}'.format(','.join(members)))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


submissions.add_command(create_submission)
submissions.add_command(delete_submission)
submissions.add_command(get_submission)
submissions.add_command(list_submissions)
submissions.add_command(update_submission)
