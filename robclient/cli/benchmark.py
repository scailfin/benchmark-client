"""Command line interface to interact with benchmarks."""

import click
import json
import requests

from robclient.io import ResultTable

import robclient.config as config
import robcore.model.template.parameter.declaration as pd
import robcore.view.labels as labels


@click.group(name='benchmark')
def benchmarks():
    """Add and remove benchmarks."""
    pass


# -- Get benchmark handle ------------------------------------------------------

@click.command(name='show')
@click.pass_context
@click.option('-b', '--id', required=False, help='Default benchmark identifier')
def get_benchmark(ctx, id):
    """Show benchmark information."""
    b_id = config.BENCHMARK_ID(default_value=id)
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
            table = ResultTable(['ID', 'Name', 'Description'], [pd.DT_STRING] * 3)
            for b in body[labels.BENCHMARKS]:
                table.add([b[labels.ID], b[labels.NAME], b[labels.DESCRIPTION]])
            for line in table.format():
                click.echo(line)
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
@click.option('-b', '--id', required=False, help='Default benchmark identifier')
@click.option(
    '-a', '--all',
    is_flag=True,
    default=False,
    help='Show all run results'
)
@click.pass_context
def get_leaderboard(ctx, id, all):
    """Show benchmark leaderboard."""
    b_id = config.benchmark_identifier(default_value=id)
    if b_id is None:
        click.echo('no benchmark specified')
        return
    try:
        engine = ctx.obj['ENGINE']
        response = engine.benchmarks().get_leaderboard(b_id, all_entries=all)
        if ctx.obj['RAW']:
            click.echo(json.dumps(response, indent=4))
        else:
            headline = ['Rank', 'User']
            types = [pd.DT_INTEGER, pd.DT_STRING]
            for col in response[labels.SCHEMA]:
                headline.append(col[labels.NAME])
                types.append(col[labels.DATA_TYPE])
            table = ResultTable(headline=headline, types=types)
            rank = 1
            for run in response[labels.RUNS]:
                row  = [str(rank), run[labels.USERNAME]]
                result = dict()
                for val in run[labels.RESULTS]:
                    result[val[labels.ID]] = val[labels.VALUE]
                for col in response[labels.SCHEMA]:
                    col_id = col[labels.ID]
                    row.append(str(result[col_id]))
                table.add(row)
                rank += 1
            for line in table.format():
                click.echo(line)
    except err.EngineError as ex:
        click.echo(ex.message)


benchmarks.add_command(get_benchmark)
benchmarks.add_command(list_benchmarks)
benchmarks.add_command(get_leaderboard)
