"""Module containing all the models."""
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

from pydantic import BaseModel, validator


class ExampleDataClass(BaseModel):
    # TODO: this should be deleted as it is just an example

    name: str

    @classmethod
    @validator("name")
    def check_name(cls, name: str) -> str:
        """Checks if the account is in our stg env or prd."""
        assert name == "adriaan"
        return name

    @classmethod
    def from_json_file(cls, config_location: str) -> "GlueJob":
        """Instantiator from file, then calling"""
        cfg = Path(config_location).read_text()
        return cls.parse_obj(json.loads(cfg))
