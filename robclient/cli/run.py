# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with submission runs."""

import click
import json
import requests

from robclient.io import ResultTable, save_file
from robcore.core.files import FileDescriptor

import robclient.config as config
import robcore.controller.run as fhlabels
import robcore.model.template.parameter.declaration as pd
import robcore.model.template.parameter.util as putil
import robcore.core.util as util
import robcore.view.labels as labels


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
        data = {labels.REASON: 'User request'}
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
@click.option('-f', '--resource', help='Resource identifier')
@click.option(
    '-o', '--output',
    type=click.Path(writable=True),
    required=False,
    help='Save as ...'
)
def download_resource(ctx, run, resource, output):
    """Download a run resource file."""
    if resource is not None:
        url = ctx.obj['URLS'].download_result_file(
            run_id=run,
            resource_id=resource
        )
    else:
        url = ctx.obj['URLS'].download_result_archive(run_id=run)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        content = r.headers['Content-Disposition']
        if output is not None:
            filename = output
        elif 'filename=' in content:
            filename = content[content.find('filename='):].split('=')[1]
        else:
            click.echo('not output filename found')
            return
        # Write the file contents in the response to the specified path
        save_file(r, filename)
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
            click.echo('ID: {}'.format(body[labels.ID]))
            if labels.STARTED_AT in body:
                ts = util.to_localstr(text=body[labels.STARTED_AT])
                click.echo('Started at: {}'.format(ts))
            if labels.FINISHED_AT in body:
                ts = util.to_localstr(text=body[labels.FINISHED_AT])
                click.echo('Finished at: {}'.format(ts))
            click.echo('State: {}'.format(body[labels.STATE]))
            # Get index of parameters. The index contains the parameter name
            # and type
            parameters = dict()
            for p in body[labels.PARAMETERS]:
                name = p[pd.LABEL_NAME]
                data_type = p[pd.LABEL_DATATYPE]
                parameters[p[labels.ID]] = (name, data_type)
            click.echo('Arguments:')
            for arg in body[labels.ARGUMENTS]:
                name, data_type = parameters[arg[labels.ID]]
                if data_type == pd.DT_FILE:
                    fh = arg[labels.VALUE][fhlabels.LABEL_FILEHANDLE]
                    f_name = fh[fhlabels.LABEL_FILENAME]
                    f_id = fh[fhlabels.LABEL_ID]
                    value = '{} ({})'.format(f_name, f_id)
                else:
                    value = arg[labels.VALUE]
                click.echo('  {} = {}'.format(name, value))
            if labels.MESSAGES in body:
                click.echo('Messages:')
                for msg in body[labels.MESSAGES]:
                    click.echo('  {}'.format(msg))
            if labels.RESOURCES in body:
                click.echo('Resources:')
                for res in body[labels.RESOURCES]:
                    r_id = res[labels.ID]
                    r_name = res[labels.NAME]
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
                headline=['ID', 'Started at', 'Finished at', 'State'],
                types=[pd.DT_STRING] * 4
            )
            for r in body[labels.RUNS]:
                run = list([r[labels.ID]])
                if labels.STARTED_AT in r:
                    run.append(util.to_localstr(text=r[labels.STARTED_AT]))
                else:
                    run.append('')
                if labels.FINISHED_AT in r:
                    run.append(util.to_localstr(text=r[labels.FINISHED_AT]))
                else:
                    run.append('')
                run.append(r[labels.STATE])
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
        for fh in body[labels.FILES]:
            files.append(
                FileDescriptor(
                    identifier=fh[labels.ID],
                    name=fh[labels.NAME],
                    created_at=util.to_datetime(fh[labels.CREATED_AT]))
                )
        # Create list of additional user-provided template parameters
        parameters = putil.create_parameter_index(body[labels.PARAMETERS])
        ps = sorted(parameters.values(), key=lambda p: (p.index, p.identifier))
        # Read values for all parameters
        arguments = putil.read(ps, files=files)
        data = {labels.ARGUMENTS: []}
        for key in arguments:
            para = parameters[key]
            arg = {labels.ID: para.identifier}
            if para.is_file():
                filename, target_path = arguments[key]
                arg[labels.VALUE] = filename
                if target_path is not None:
                    arg[labels.AS] = target_path
            else:
                arg[labels.VALUE] = arguments[key]
            data[labels.ARGUMENTS].append(arg)
        url = ctx.obj['URLS'].start_run(submission_id=s_id)
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            run_id = body[labels.ID]
            run_state = body[labels.STATE]
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
