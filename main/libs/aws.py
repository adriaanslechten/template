"""AWS helpers."""
from typing import Any, List

import boto3
from botocore import client

from libs.fun import flatten


def get_all_aws_entries(
    aws_client: client, operation: str, root_element: str, **kwargs: str
) -> List[Any]:
    """Gets all the AWS entries for a given paginator and operation"""
    paginator = aws_client.get_paginator(operation)
    return list(
        flatten([page[root_element] for page in paginator.paginate(**kwargs)])
    )


def get_client(service: str, region: str) -> client:
    """Get's a boto3 client."""
    return boto3.client(service, region_name=region)
