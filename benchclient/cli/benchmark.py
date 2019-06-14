"""Command line interface to interact with benchmarks."""

import click
import json

from benchclient.io import ResultTable

import benchclient.config as config
import benchengine.api.serialize.labels as labels
import benchengine.error as err
import benchtmpl.error as errtmpl
import benchtmpl.workflow.parameter.declaration as pd
import benchtmpl.workflow.parameter.util as para
import benchtmpl.workflow.template.util as tmpl


@click.group(name='benchmark')
def benchmarks():
    """Add and remove benchmarks."""
    pass


# ------------------------------------------------------------------------------
# Add benchmark
# ------------------------------------------------------------------------------

@click.command(name='create')
@click.option(
    '-n', '--name',
    required=True,
    help='Unique benchmark name'
)
@click.option(
    '-d', '--description',
    required=False,
    help='Short description'
)
@click.option(
    '-i', '--instructions',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
    help='Instructions for participants'
)
@click.option(
    '-s', '--src',
    type=click.Path(exists=True, file_okay=False, readable=True),
    required=False,
    help='Benchmark template directory'
)
@click.option(
    '-u', '--url',
    required=False,
    help='Benchmark template Git repository URL'
)
@click.option(
    '-f', '--specfile',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
    help='Optional path to benchmark specification file'
)
@click.pass_context
def add_benchmark(
    ctx, name, description=None, instructions=None, src=None, url=None,
    specfile=None
):
    """Add a new benchmark."""
    # Read instructions from file if given
    instruction_text = None
    if not instructions is None:
        with open(instructions, 'r') as f:
            instruction_text = f.read()
    # Add benchmark template to repository
    try:
        # Get the benchmark repository instance from the engine API
        repo = ctx.obj['ENGINE'].benchmarks().repository
        benchmark = repo.add_benchmark(
            name=name,
            description=description,
            instructions=instruction_text,
            src_dir=src,
            src_repo_url=url,
            template_spec_file=specfile
        )
        click.echo('export {}={}'.format(config.ENV_BENCHMARK, benchmark.identifier))
    except ValueError as ex:
        click.echo(str(ex))
    except (err.EngineError, errtmpl.TemplateError) as ex:
        click.echo(ex.message)


# ------------------------------------------------------------------------------
# Show benchmark information
# ------------------------------------------------------------------------------
@click.command(name='show')
@click.pass_context
@click.option('-b', '--id', required=False, help='Default benchmark identifier')
def get_benchmark(ctx, id):
    """Show benchmark information."""
    b_id = config.benchmark_identifier(default_value=id)
    if b_id is None:
        click.echo('no benchmark specified')
        return
    try:
        response = ctx.obj['ENGINE'].benchmarks().get_benchmark(b_id)
        if ctx.obj['RAW']:
            click.echo(json.dumps(response, indent=4))
        else:
            click.echo('Identifier  : {}'.format(response[labels.ID]))
            click.echo('Name        : {}'.format(response[labels.NAME]))
            if labels.DESCRIPTION in response:
                click.echo('Description : {}'.format(response[labels.DESCRIPTION]))
            if labels.INSTRUCTIONS in response:
                click.echo('\nInstructions:')
                click.echo(response[labels.INSTRUCTIONS])
            parameters = para.create_parameter_index(response[labels.PARAMETERS])
            click.echo('\nParameters:')
            for p in para.sort_parameters(parameters.values()):
                click.echo('  {} ({})'.format(p.name, p.data_type))
    except err.EngineError as ex:
        click.echo(ex.message)


# ------------------------------------------------------------------------------
# List competitions
# ------------------------------------------------------------------------------
@click.command(name='list')
@click.pass_context
def list_benchmarks(ctx):
    """List all benchmarks."""
    response = ctx.obj['ENGINE'].benchmarks().list_benchmarks()
    if ctx.obj['RAW']:
        click.echo(json.dumps(response, indent=4))
    else:
        for b in response[labels.BENCHMARKS]:
            click.echo('{}\t{}'.format(b[labels.ID], b[labels.NAME]))


# ------------------------------------------------------------------------------
# Get benchmark leaderboard
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Run benchmark
# ------------------------------------------------------------------------------
@click.command(name='run')
@click.pass_context
@click.option('-b', '--id', required=False, help='Default benchmark identifier')
def run_benchmark(ctx, id):
    """Run benchmark."""
    b_id = config.benchmark_identifier(default_value=id)
    if b_id is None:
        click.echo('no benchmark specified')
        return
    token = config.access_token()
    if token is None:
        click.echo('no logged in')
        return
    try:
        engine = ctx.obj['ENGINE']
        response = engine.benchmarks().get_benchmark(b_id)
        parameters = para.create_parameter_index(response[labels.PARAMETERS])
        arguments = tmpl.read(para.sort_parameters(parameters.values()))
        response = engine.benchmarks().run_benchmark(
            benchmark_id=b_id,
            arguments=arguments,
            access_token=token
        )
        if ctx.obj['RAW']:
            click.echo(json.dumps(response, indent=4))
        else:
            click.echo(response[labels.STATE])
    except (IOError, OSError) as ex:
        click.echo(str(ex))
    except err.EngineError as ex:
        click.echo(ex.message)


benchmarks.add_command(add_benchmark)
benchmarks.add_command(get_benchmark)
benchmarks.add_command(list_benchmarks)
benchmarks.add_command(get_leaderboard)
benchmarks.add_command(run_benchmark)
