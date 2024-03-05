import asyncio
import json
from os.path import expanduser

import click
import httpx

from . import tracing
from .tfcloud import TerraformCloud


def validate_tracing(ctx, param, value):
    try:
        return tracing.build_exporter(value)
    except ValueError as exc:
        raise click.BadParameter(str(exc))


@click.group()
@click.option(
    "--trace-exporter",
    help="Trace exporter to configure",
    default="",
    callback=validate_tracing,
)
def cli(trace_exporter):
    tracing.setup(trace_exporter)


@cli.command()
@click.option("--token", help="The Terraform Cloud authentication token,")
@click.option("--organization", help="The Terraform Cloud organization", required=True)
@click.option("--include", help="Tags to include", multiple=True)
@click.option("--exclude", help="Tags to exclude", multiple=True)
def terraform_cloud_trigger_all(organization, include, exclude, token):
    if token is None:
        with open(expanduser("~/.terraform.d/credentials.tfrc.json")) as fp:
            data = json.load(fp)

        token = data["credentials"]["app.terraform.io"]["token"]

    http = httpx.AsyncClient()
    tfcloud = TerraformCloud(http, token)
    task = tfcloud.trigger_all(organization, include, exclude)

    asyncio.run(task)


def main():
    cli()
