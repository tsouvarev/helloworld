import click

from lib.config import VENDORS
from lib.parse import parse
from lib.render import render


@click.group()
def cmd():
    pass


@cmd.command(name='all')
def all_():
    parse()
    render()


cmd.command()(
    click.option(
        '--vendor',
        '-v',
        multiple=True,
        type=click.Choice(VENDORS),
        required=False,
    )(parse)
)
cmd.command()(render)

if __name__ == '__main__':
    cmd()
