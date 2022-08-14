import click

from functools import partial

debug = click.secho
info = partial(click.secho, color='white', bold=True)
warn = partial(click.secho, fg='yellow')
error = partial(click.secho, fg='red', err=True, bold=True)
