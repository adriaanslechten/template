"""Main entry point"""
from pathlib import Path
from typing import List

import click
import structlog
from click import group

from models import ExampleDataClass
from main.libs.aws import get_client

LOG = structlog.get_logger(__file__)


@group()
def main() -> None:
    logs.setup_logging()


@main.command()
@click.option(
    "--name", help="Provide the name please.", required=True,
)
def example_cli_function(name: str,) -> None:
    register_fn("glue_client", get_client(service="glue", region="eu-west-1"))
    my_dataclass = ExampleDataClass(name)
    print(my_dataclass.name)
