import click

from pyp2rpm_analyzer import settings
from pyp2rpm_analyzer.runner import run_pyp2rpm
from pyp2rpm_analyzer.builds_push import create_builds
from pyp2rpm_analyzer.analyzer import analyse_builds

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(CONTEXT_SETTINGS)
@click.option('--run / --no-run',
              help='Generate SRPMs for given test set.',
              default=True)
@click.option('--build / --no-build',
              help='Push builds of SRPMs to Copr project specified in settings',
              default=True)
@click.option('--analyse / --no-analyse',
              help='Run builds analysis of Copr project specified in settings.',
              default=True)
@click.option('-f',
              help='File containing test set (each package on a new line.',
              metavar='TEST_SET_FILE',
              default=None)
@click.option('-md',
              help="Number of packages from most downloaded pacakges on PyPI",
              metavar='NUM',
              default=0)
@click.option('-rand',
              help="Number of packages from most downloaded pacakges on PyPI",
              metavar='NUM',
              default=0)
def main(run, build, analyse, f, md, rand):
    if not settings.SAVE_PATH.endswith('/'):
        settings.SAVE_PATH += '/'

    if run:
        run_pyp2rpm(filename=f, md=md, rand=rand)
    if build:
        create_builds()
    if analyse:
        analyse_builds()
