import asyncio
import json
from os.path import expanduser

import click
import httpx
from opentelemetry.sdk.trace.export import SpanExporter

from . import tracing
from .tfcloud import TerraformCloud


def validate_tracing(
    ctx: click.Context, param: click.Parameter, value: str
) -> SpanExporter:
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
def cli(trace_exporter: SpanExporter) -> None:
    tracing.global_setup(trace_exporter)


@cli.command()
@click.argument("org_name")
@click.option("--token", help="The Terraform Cloud authentication token")
@click.option("--include", help="Tags to include", multiple=True)
@click.option("--exclude", help="Tags to exclude", multiple=True)
def terraform_cloud_trigger_all(
    org_name: str,
    include: list[str],
    exclude: list[str],
    token: str,
) -> None:
    """Start new runs in the workspaces of a Terraform Cloud organization.

    ORG_NAME is the name (not the ID) of the Terraform Cloud organization.
    """

    if token is None:
        with open(expanduser("~/.terraform.d/credentials.tfrc.json")) as fp:
            data = json.load(fp)

        token = data["credentials"]["app.terraform.io"]["token"]

    http = httpx.AsyncClient()
    tfcloud = TerraformCloud(http, token)
    task = tfcloud.trigger_all(org_name, include, exclude)

    asyncio.run(task)


def main() -> None:
    cli()
