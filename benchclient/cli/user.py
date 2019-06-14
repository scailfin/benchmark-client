"""Command line interface to register users."""

import click
import json
import os

import benchclient.config as config
import benchengine.api.serialize.labels as labels
import benchengine.error as err


@click.group()
def user():
    """Register new users and manage login credentials."""
    pass


# ------------------------------------------------------------------------------
# Info
# ------------------------------------------------------------------------------

@click.command()
@click.pass_context
def whoami(ctx):
    """Print name of current user."""
    # Get user info using the access token
    users = ctx.obj['ENGINE'].users()
    try:
        response = users.whoami(access_token=config.access_token())
        if ctx.obj['RAW']:
            click.echo(json.dumps(response, indent=4))
        else:
            click.echo('Logged in as user {}.'.format(response[labels.USERNAME]))
    except err.UnauthenticatedAccessError:
        click.echo('Not logged in.')

# ------------------------------------------------------------------------------
# List users
# ------------------------------------------------------------------------------
@click.command()
@click.pass_context
def list(ctx):
    """List all registered users."""
    # There is currently no API call to get a listing of all registered users.
    # Here we use the UserManager instaed
    users = ctx.obj['ENGINE'].users().manager
    for user in users.list_user():
        click.echo('{} ({})'.format(user.username, user.is_logged_in()))


# ------------------------------------------------------------------------------
# Login
# ------------------------------------------------------------------------------

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
    users = ctx.obj['ENGINE'].users()
    try:
        response = users.login(username=username, password=password)
        if ctx.obj['RAW']:
            click.echo(json.dumps(response, indent=4))
        else:
            click.echo('export {}={}'.format(
                config.ENV_ACCESS_TOKEN,
                response[labels.ACCESS_TOKEN]
            ))
    except err.UnknownUserError as ex:
        click.echo(ex.message)


# ------------------------------------------------------------------------------
# Logout
# ------------------------------------------------------------------------------

@click.command()
@click.pass_context
def logout(ctx):
    """Logout from current user session."""
    # Get user info using the access token
    users = ctx.obj['ENGINE'].users()
    response = users.logout(access_token=config.access_token())
    if ctx.obj['RAW']:
        click.echo(json.dumps(response, indent=4))
    else:
        click.echo('Logged out.')


# ------------------------------------------------------------------------------
# Register
# ------------------------------------------------------------------------------

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
    users = ctx.obj['ENGINE'].users()
    try:
        response = users.register(username=username, password=password)
        if ctx.obj['RAW']:
            click.echo(json.dumps(response, indent=4))
        else:
            click.echo('User {} registered.'.format(username))
    except (err.DuplicateUserError, err.ConstraintViolationError) as ex:
        click.echo(ex.message)

# ------------------------------------------------------------------------------
# Reset Password
# ------------------------------------------------------------------------------

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
    help='New user password'
)
def pwd(ctx, username, password):
    """Reset user password."""
    # There is no single password request API method at this point
    users = ctx.obj['ENGINE'].users().manager
    # Need to get a reset request id first
    request_id = users.request_password_reset(username=username)
    # Use request id to reset password
    users.reset_password(request_id=request_id, password=password)
    click.echo('Password reset for user {}.'.format(username))


user.add_command(list)
user.add_command(login)
user.add_command(logout)
user.add_command(pwd)
user.add_command(register)
user.add_command(whoami)
