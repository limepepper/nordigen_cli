from typing import Any
from uuid import UUID

import pytest
from limepepper_utils.yaml_importing import yaml

test_format_data = [
    {
        "input": "xxx",
        "format": "yaml",
    },
    {
        "input": {
            "someval": "grgreg",
            "uuid": UUID("19454afd-0118-4a5d-a1b8-f60b1b4203f9"),
        },
        "format": "yaml",
    },
]


class TestUserLoginEndpoint:
    @pytest.mark.parametrize(
        "input,format",
        [tuple(d.values()) for d in test_format_data],
    )
    def test_param_logins(
        self,
        input: Any,
        format: str,
    ):
        """test we can output yaml from dicts with UUID values"""
        _ = yaml.safe_dump(
            input,
            sort_keys=False,
        )
