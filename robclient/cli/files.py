# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with submission files."""

import click
import json
import requests

from robclient.io import ResultTable

import robclient.config as config
import robcore.model.template.parameter.declaration as pd
import robcore.util as util
import robcore.view.labels as labels


@click.group(name='files')
def files():
    """Upload, download, list and delete submission files."""
    pass


# -- Delete file ---------------------------------------------------------------

@click.command(name='delete')
@click.pass_context
@click.option('-s', '--submission', required=False, help='Submission identifier')
@click.option('-f', '--file', required=True, help='File identifier')
def delete_file(ctx, submission, file):
    """Delete a previously uploaded file."""
    s_id = config.SUBMISSION_ID(default_value=submission)
    if s_id is None:
        click.echo('no submission specified')
        return
    msg = 'Do you really want to delete file {}'
    if not click.confirm(msg.format(file)):
        return
    url = ctx.obj['URLS'].delete_file(submission_id=s_id, file_id=file)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.delete(url, headers=headers)
        r.raise_for_status()
        click.echo('File \'{}\' deleted.'.format(file))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Download file -------------------------------------------------------------

@click.command(name='download')
@click.pass_context
@click.option('-s', '--submission', required=False, help='Submission identifier')
@click.option('-f', '--file', required=True, help='File identifier')
@click.option(
    '-o', '--output',
    type=click.Path(writable=True),
    required=False,
    help='Save as ...'
)
def download_file(ctx, submission, file, output):
    """Download a previously uploaded file."""
    s_id = config.SUBMISSION_ID(default_value=id)
    if s_id is None:
        click.echo('no submission specified')
        return
    url = ctx.obj['URLS'].download_file(submission_id=s_id, file_id=file)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        content = r.headers['Content-Disposition']
        if not output is None:
            filename = output
        elif 'filename=' in content:
            filename = content[content.find('filename='):].split('=')[1]
        else:
            click.echo('not output filename found')
            return
        # Write the file contents in the response to the specified path
        # Based on https://www.techcoil.com/blog/how-to-download-a-file-via-http-post-and-http-get-with-python-3-requests-library/
        with open(filename, 'wb') as local_file:
            for chunk in r.iter_content(chunk_size=128):
                local_file.write(chunk)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- List files ----------------------------------------------------------------

@click.command(name='list')
@click.pass_context
@click.option('-s', '--submission', required=False, help='Submission identifier')
def list_files(ctx, submission):
    """List uploaded files for a submission."""
    s_id = config.SUBMISSION_ID(default_value=submission)
    if s_id is None:
        click.echo('no submission specified')
        return
    url = ctx.obj['URLS'].list_files(submission_id=s_id)
    headers = ctx.obj['HEADERS']
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            table = ResultTable(
                headline=['ID', 'Name', 'Created At', 'Size'],
                types=[pd.DT_STRING, pd.DT_STRING, pd.DT_STRING, pd.DT_INTEGER]
            )
            for f in body[labels.FILES]:
                table.add([
                    f[labels.ID],
                    f[labels.NAME],
                    util.to_localstr(text=f[labels.CREATED_AT]),
                    f[labels.FILESIZE]
                ])
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Upload file ---------------------------------------------------------------

@click.command(name='upload')
@click.pass_context
@click.option('-s', '--submission', required=False, help='Submission identifier')
@click.option(
    '-i', '--input',
    type=click.Path(exists=True, readable=True),
    required=True,
    help='Input file'
)
def upload_file(ctx, submission, input):
    """Upload a file for a submission."""
    s_id = config.SUBMISSION_ID(default_value=submission)
    if s_id is None:
        click.echo('no submission specified')
        return
    url = ctx.obj['URLS'].upload_file(submission_id=s_id)
    headers = ctx.obj['HEADERS']
    files = {'file': open(input, 'rb')}
    try:
        r = requests.post(url, files=files, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            f_id = body[labels.ID]
            f_name = body[labels.NAME]
            click.echo('Uploaded \'{}\' with ID {}.'.format(f_name, f_id))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


files.add_command(delete_file)
files.add_command(download_file)
files.add_command(list_files)
files.add_command(upload_file)
