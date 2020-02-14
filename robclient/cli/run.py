# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with submission runs."""

import click
import json
import os
import requests

from flowserv.cli.parameter import read
from flowserv.core.files import FileDescriptor
from robclient.table import ResultTable

import flowserv.core.util as util
import flowserv.model.parameter.base as pb
import flowserv.model.parameter.declaration as pd
import robclient.config as config


@click.group(name='runs')
def runs():
    """Create, query and delete submission runs."""
    pass


# -- Cancel run ---------------------------------------------------------------

@click.command(name='cancel')
@click.pass_context
@click.option('-r', '--run', required=True, help='Run identifier')
def cancel_run(ctx, run):
    """Cancel active run."""
    try:
        url = ctx.obj['URLS'].cancel_run(run_id=run)
        headers = ctx.obj['HEADERS']
        data = {'reason': 'User request'}
        r = requests.put(url, json=data, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            click.echo('Run  \'{}\' canceled.'.format(run))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))
    except (ValueError, IOError, OSError) as ex:
        click.echo('{}'.format(ex))


# -- Delete run ---------------------------------------------------------------

@click.command(name='delete')
@click.pass_context
@click.option('-r', '--run', required=True, help='Run identifier')
def delete_run(ctx, run):
    """Delete run."""
    try:
        url = ctx.obj['URLS'].delete_run(run_id=run)
        headers = ctx.obj['HEADERS']
        r = requests.delete(url, headers=headers)
        r.raise_for_status()
        click.echo('Run  \'{}\' deleted.'.format(run))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))
    except (ValueError, IOError, OSError) as ex:
        click.echo('{}'.format(ex))


# -- Download resource file(s) ------------------------------------------------

@click.command(name='download')
@click.pass_context
@click.option('-r', '--run', required=True, help='Run identifier')
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
def download_resource(ctx, run, resource, all, output):
    """Download a run resource file."""
    # We cannot have a resource and the all flag being True
    if resource is not None and all:
        click.echo('invalid argument combination')
        return
    elif resource is None and not all:
        click.echo('select resource or all')
        return
    urls = ctx.obj['URLS']
    if resource is not None:
        url = urls.download_run_file(run_id=run, resource_id=resource)
    else:
        url = urls.download_run_archive(run_id=run)
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


# -- Get run ------------------------------------------------------------------

@click.command(name='show')
@click.pass_context
@click.option('-r', '--run', required=True, help='Run identifier')
def get_run(ctx, run):
    """List all submission runs."""
    try:
        url = ctx.obj['URLS'].get_run(run_id=run)
        headers = ctx.obj['HEADERS']
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            click.echo('ID: {}'.format(body['id']))
            if 'startedAt' in body:
                ts = util.to_localstr(text=body['startedAt'])
                click.echo('Started at: {}'.format(ts))
            if 'finishedAt' in body:
                ts = util.to_localstr(text=body['finishedAt'])
                click.echo('Finished at: {}'.format(ts))
            click.echo('State: {}'.format(body['state']))
            # Get index of parameters. The index contains the parameter name
            # and type
            parameters = dict()
            for p in body['parameters']:
                name = p[pd.LABEL_NAME]
                data_type = p[pd.LABEL_DATATYPE]
                parameters[p['id']] = (name, data_type)
            click.echo('Arguments:')
            for arg in body['arguments']:
                name, data_type = parameters[arg['id']]
                if data_type == pd.DT_FILE:
                    fh = arg['value']['file']
                    f_name = fh['name']
                    f_id = fh['id']
                    value = '{} ({})'.format(f_name, f_id)
                else:
                    value = arg['value']
                click.echo('  {} = {}'.format(name, value))
            if 'messages' in body:
                click.echo('Messages:')
                for msg in body['messages']:
                    click.echo('  {}'.format(msg))
            if 'resources' in body:
                click.echo('Resources:')
                for res in body['resources']:
                    r_id = res['id']
                    r_name = res['name']
                    click.echo('  {} ({})'.format(r_name, r_id))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))
    except (ValueError, IOError, OSError) as ex:
        click.echo('{}'.format(ex))


# -- List runs ----------------------------------------------------------------

@click.command(name='list')
@click.pass_context
@click.option(
    '-s', '--submission',
    required=False,
    help='Submission identifier'
)
def list_runs(ctx, submission):
    """List all submission runs."""
    s_id = submission if submission else config.SUBMISSION_ID()
    if s_id is None:
        click.echo('no submission specified')
        return
    try:
        url = ctx.obj['URLS'].list_runs(submission_id=s_id)
        headers = ctx.obj['HEADERS']
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            table = ResultTable(
                headline=['ID', 'Submitted at', 'State'],
                types=[pd.DT_STRING] * 4
            )
            for r in body['runs']:
                run = list([r['id'], r['createdAt'], r['state']])
                table.add(run)
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))
    except (ValueError, IOError, OSError) as ex:
        click.echo('{}'.format(ex))


# -- Start new submission run -------------------------------------------------

@click.command(name='start')
@click.pass_context
@click.option(
    '-s', '--submission',
    required=False,
    help='Submission identifier'
)
def start_run(ctx, submission):
    """Start new submission run."""
    s_id = submission if submission else config.SUBMISSION_ID()
    if s_id is None:
        click.echo('no submission specified')
        return
    try:
        url = ctx.obj['URLS'].get_submission(submission_id=s_id)
        headers = ctx.obj['HEADERS']
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        # Create list of file descriptors for uploaded files that are included
        # in the submission handle
        files = []
        for fh in body['files']:
            files.append(
                FileDescriptor(
                    identifier=fh['id'],
                    name=fh['name'],
                    created_at=util.to_datetime(fh['createdAt']))
                )
        # Create list of additional user-provided template parameters
        parameters = pb.create_parameter_index(body['parameters'])
        ps = sorted(parameters.values(), key=lambda p: (p.index, p.identifier))
        # Read values for all parameters
        arguments = read(ps, files=files)
        data = {'arguments': []}
        for key in arguments:
            para = parameters[key]
            arg = {'id': para.identifier}
            if para.is_file():
                filename, target_path = arguments[key]
                arg['value'] = filename
                if target_path is not None:
                    arg['as'] = target_path
            else:
                arg['value'] = arguments[key]
            data['arguments'].append(arg)
        url = ctx.obj['URLS'].start_run(submission_id=s_id)
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            run_id = body['id']
            run_state = body['state']
            click.echo('run {} in state {}'.format(run_id, run_state))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))
    except (ValueError, IOError, OSError) as ex:
        click.echo('{}'.format(ex))


runs.add_command(cancel_run)
runs.add_command(delete_run)
runs.add_command(download_resource)
runs.add_command(get_run)
runs.add_command(list_runs)
runs.add_command(start_run)
