import json
from pathlib import Path

import pytest
import typer
from api.auth import create_jwt_pair_for_uuid
from limepepper_utils.jwt.client import JWTValidationError
from loguru import logger
from rich.console import Console
from typer.testing import CliRunner

from nordigen_cli import nordigen_cli
from nordigen_cli.apiclient.client import NordigenClient
from nordigen_cli.exception_handler import setup_exception_handling
from nordigen_cli.models.token import BaseToken

console = Console()

token_test_data = [
    {
        "description": "Test correct token string",
        "valid": True,
        "token_string": """
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwidXVpZCI6IjZjYmIyNGE2LTI4YjktNDQxZS05MTg0LTNlOTNkNjQ5NzU5NCIsImV4cCI6MTczMjc3NTMyNSwianRpIjoiMzRkNDJjY2YtY2NlNi00NzAwLTljMGItY2Y1NTRiNzQzMWFhIn0.5tSIh0EF9Vu4gZIO2wefkZKlBggiuxIVnS9jsIf-6ro",
    "expires_str": 60,
    "expires_at": "2024-11-28T06:28:45.718048"
}
        """,
        "exceptions": (),
    },
    {
        "description": "Test truncated token string",
        "valid": False,
        "token_string": """
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwidXVpZCI6IjZjYmIyNGE2LTI4YjktNDQxZS05MTg0LTNlOTNkNjQ5NzU5NCIsImV4cCI6MTczMjc3NTMyNSwianRpIjoiMzRkNDJjY2YtY2NlNi00NzAwLTljMGItY2Y1NTRiNzQzMWFhIn0.5tSIh0EF9Vu4gZIO2wefkZKlBggiuxIVn",
    "expires_str": 60,
    "expires_at": "2024-11-28T06:28:45.718048"
}
        """,
        "exceptions": JWTValidationError,
    },
    {
        "description": "missing expiry, but still valid",
        "valid": True,
        "token_string": """
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwidXVpZCI6IjZjYmIyNGE2LTI4YjktNDQxZS05MTg0LTNlOTNkNjQ5NzU5NCIsImV4cCI6MTczMjc3NTMyNSwianRpIjoiMzRkNDJjY2YtY2NlNi00NzAwLTljMGItY2Y1NTRiNzQzMWFhIn0.5tSIh0EF9Vu4gZIO2wefkZKlBggiuxIVnS9jsIf-6ro"
}
        """,
        "exceptions": (json.decoder.JSONDecodeError,),
    },
    {
        "description": "bad json - only opening bracket",
        "valid": False,
        "token_string": """
{
        """,
        "exceptions": (json.decoder.JSONDecodeError,),
    },
    {
        "description": "bad json - empty string",
        "valid": False,
        "token_string": """
        """,
        "exceptions": (json.decoder.JSONDecodeError,),
    },
    {
        "description": "bad json - empty string",
        "valid": False,
        "token_string": """
        """,
        "exceptions": (json.decoder.JSONDecodeError,),
    },
    {
        "description": "bad json - empty dict",
        "valid": False,
        "token_string": """
{}
        """,
        "exceptions": (KeyError,),
    },
]


class TestLoadingTokenStrings:
    @pytest.mark.parametrize(
        "description,valid,token_string,exceptions",
        [tuple(d.values()) for d in token_test_data],
    )
    def test_token_serialized_strings(
        self,
        description,
        token_string,
        valid,
        exceptions,
    ):
        if valid:
            new_token = BaseToken.from_json(token_string)
            logger.trace(f"new_token: {new_token}")
            assert new_token is not None
        else:
            with pytest.raises(exceptions):
                new_token = BaseToken.from_json(token_string)
                logger.trace(f"token_string : {token_string}")
                logger.trace(f"new_token : {new_token}")
                console.print(new_token)

    def test_client_with_wrong_token_type(
        self,
        test_server,
        test_data,
    ):
        user = test_data["good_user"]
        access_token, refresh_token = create_jwt_pair_for_uuid(uuid=user.id)

        client = NordigenClient(
            id=user.id,
            key=user.key,
            api=f"{test_server}/api/v2",
        )

        with pytest.raises(ValueError):
            client.set_refresh_token(access_token)

        with pytest.raises(ValueError):
            client.set_access_token(refresh_token)

    def test_cli_with_wrong_token_type(
        self,
        test_server,
        test_data,
        tmp_path,
        mocker,
    ):
        user = test_data["good_user"]
        access_token, refresh_token = create_jwt_pair_for_uuid(uuid=user.id)

        # patch retrieval of the apps' config dir
        mocker.patch(
            "limepepper_utils.xdg.XDGBasedir.get_app_dir",
            return_value=Path(tmp_path),
        )

        tmp_profile_dir = tmp_path / "default"
        tmp_refresh_file = tmp_profile_dir / "refresh.json"

        Path(tmp_profile_dir).mkdir(parents=True, exist_ok=True)

        Path(tmp_refresh_file).write_text(access_token.model_dump_json(indent=4))

        print(f"typer.get_app_dir: {typer.get_app_dir("xxx")}")

        runner = CliRunner(
            mix_stderr=False,
        )

        app = nordigen_cli.create_app()
        setup_exception_handling(app)
        result = runner.invoke(
            app,
            [
                "--id",
                user.id,
                "--key",
                user.key,
                "--api",
                f"{test_server}/api/v2",
                "bank",
                "list",
                "GB",
            ],
            color=True,
            env={"REQUESTS_DEBUGGER": "1"},
        )
        # rinspect(app)
        console.print(result.stdout)
        console.print(result.stderr)
        assert result.exit_code == 65
