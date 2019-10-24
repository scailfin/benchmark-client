# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface to register users."""

import click
import json
import requests

from robclient.io import ResultTable

import robclient.config as config
import robcore.model.template.parameter.declaration as pd
import robcore.view.labels as labels


# -- List users ----------------------------------------------------------------

@click.command(name='users')
@click.pass_context
def list(ctx):
    """List all registered users."""
    url = ctx.obj['URLS'].list_users()
    headers = ctx.obj['HEADERS']
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            table = ResultTable(['Name', 'ID'], [pd.DT_STRING, pd.DT_STRING])
            for user in body[labels.USERS]:
                table.add([user[labels.USERNAME], user[labels.ID]])
            for line in table.format():
                click.echo(line)
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Login ---------------------------------------------------------------------

@click.command()
@click.pass_context
@click.option(
    '-u', '--username',
    required=True,
    prompt=True,
    help='User name'
)
@click.option(
    '-p', '--password',
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help='User password'
)
def login(ctx, username, password):
    """Login to to obtain access token."""
    url = ctx.obj['URLS'].login()
    headers = ctx.obj['HEADERS']
    data = {labels.USERNAME: username, labels.PASSWORD: password}
    try:
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            token = body[labels.ACCESS_TOKEN]
            click.echo('export {}={}'.format(config.ROB_ACCESS_TOKEN, token))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Logout --------------------------------------------------------------------

@click.command()
@click.pass_context
def logout(ctx):
    """Logout from current user session."""
    # Get user info using the access token
    url = ctx.obj['URLS'].logout()
    headers = ctx.obj['HEADERS']
    try:
        r = requests.post(url, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            click.echo('See ya mate!')
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Register ------------------------------------------------------------------

@click.command()
@click.pass_context
@click.option(
    '-u', '--username',
    required=True,
    prompt=True,
    help='User name'
)
@click.option(
    '-p', '--password',
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help='User password'
)
def register(ctx, username, password):
    """Register a new user."""
    url = ctx.obj['URLS'].register_user()
    headers = ctx.obj['HEADERS']
    data = {
        labels.USERNAME: username,
        labels.PASSWORD: password,
        labels.VERIFY_USER: False
    }
    try:
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            user_id = body[labels.ID]
            user_name = body[labels.USERNAME]
            click.echo('Registered {} with ID {}.'.format(user_name, user_id))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Reset Password ------------------------------------------------------------

@click.command(name='pwd')
@click.pass_context
@click.option(
    '-u', '--username',
    required=True,
    prompt=True,
    help='User name'
)
@click.option(
    '-p', '--password',
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help='New user password'
)
def reset_password(ctx, username, password):
    """Reset user password."""
    url = ctx.obj['URLS'].request_password_reset()
    headers = ctx.obj['HEADERS']
    data = {labels.USERNAME: username}
    try:
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
        body = r.json()
        reqest_id = body[labels.REQUEST_ID]
        url = ctx.obj['URLS'].reset_password()
        data = {labels.REQUEST_ID: reqest_id, labels.PASSWORD: password}
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            click.echo('Password reset.')
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))


# -- Who am I ------------------------------------------------------------------

@click.command()
@click.pass_context
def whoami(ctx):
    """Print name of current user."""
    # Get user info using the access token
    try:
        r = requests.get(ctx.obj['URLS'].whoami(), headers=ctx.obj['HEADERS'])
        r.raise_for_status()
        body = r.json()
        if ctx.obj['RAW']:
            click.echo(json.dumps(body, indent=4))
        else:
            click.echo('Logged in as {}.'.format(body[labels.USERNAME]))
    except (requests.ConnectionError, requests.HTTPError) as ex:
        click.echo('{}'.format(ex))
