"""Command line interface for the RENATA API."""

import click
import json

from benchclient.cli.benchmark import benchmarks
from benchengine.api.base import EngineApi
from benchengine.db import DatabaseDriver

import benchclient.cli.user as user
import benchengine.api.serialize.labels as labels


@click.group()
@click.option(
    '--raw',
    is_flag=True,
    default=False,
    help='Show raw (JSON) response'
)
@click.pass_context
def cli(ctx, raw):
    """Command Line Interface for Reproducible Benchmarks for Data Analysis API.
    """
    # Ensure that ctx.obj exists and is a dict. Based on
    # https://click.palletsprojects.com/en/7.x/commands/#nested-handling-and-contexts
    ctx.ensure_object(dict)
    # Set the raw output flag and initialize the EngineApi in the context
    # object.
    ctx.obj['RAW'] = raw
    ctx.obj['ENGINE'] = EngineApi()


@cli.command()
@click.option(
    '-s', '--schema',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help='File containing statements to create empty database'
)
def init(schema=None):
    """Initialize database for the reproducible benchmark engine API.
    """
    DatabaseDriver.init_db(schema_file=schema)
    click.echo('Database created.')


@cli.command()
@click.pass_context
def info(ctx):
    """Print API name and version."""
    service = ctx.obj['ENGINE'].service_descriptor()
    if ctx.obj['RAW']:
        click.echo(json.dumps(service, indent=4))
    else:
        click.echo('Engine API')
        click.echo('  Name   : {}'.format(service[labels.NAME]))
        click.echo('  Version: {}'.format(service[labels.VERSION]))
        click.echo('\nDatabase')
        click.echo(DatabaseDriver.info(indent='  '))


#cli.add_command(competition)
#cli.add_command(team)
# User commands
cli.add_command(user.login)
cli.add_command(user.logout)
cli.add_command(user.register)
cli.add_command(user.whoami)
# Benchmarks
cli.add_command(benchmarks)
