import click

from lib.parse import parse
from lib.render import render


@click.group()
def cmd():
    pass


@cmd.command(name='all')
def all_():
    parse()
    render()


cmd.command()(parse)
cmd.command()(render)

if __name__ == '__main__':
    cmd()
