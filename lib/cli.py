import click

from lib.config import VENDORS
from lib.parse import parse
from lib.render import render


@click.group()
def cli():
    pass


cli.command()(
    click.option(
        '--vendor',
        '-v',
        multiple=True,
        type=click.Choice(VENDORS),
        required=False,
    )(parse)
)
cli.command()(render)

if __name__ == '__main__':
    cli()
