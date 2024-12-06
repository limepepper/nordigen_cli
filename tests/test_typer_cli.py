import json
from pathlib import Path

import pytest
from limepepper_utils.xdg import XDGBasedir
from typer.testing import CliRunner

from nordigen_cli import BootstrapConfigProvider, console, nordigen_cli

runner = CliRunner(
    mix_stderr=False,
)


test_cli_data = [
    {
        "description": "Show config dump command",
        "valid": True,  # should the command succeed
        "args": [
            "config",
            "dump",
        ],
        "expected": {
            "exit_code": 0,
            "stdout_strings": ["All settings are correct"],
        },
    },
    {
        "description": "Try use non-existing profile",
        "valid": False,
        "args": [
            "-p",
            "not-exists-profile",
            "config",
            "dump",
        ],
        "expected": {
            "exit_code": 78,
            "stdout_strings": ["Profile not found"],
        },
    },
]


class TestTyperCli:
    @pytest.mark.parametrize(
        "description,valid,args,expected",
        [tuple(d.values()) for d in test_cli_data],
    )
    def test_running_nordctl_typer_with_commands(
        self,
        test_server,
        test_data,
        tmpdir,
        mocker,
        description,
        valid,
        args,
        expected,
    ):
        XDGBasedir.get_xdg_config_home = lambda: Path(tmpdir)
        mocker.patch(
            "limepepper_utils.xdg.XDGBasedir.get_app_dir", return_value=str(tmpdir)
        )

        user = test_data["a_n_user"]
        tmp_settings = {
            **BootstrapConfigProvider.get_default_config(),
            **{
                "api": f"{test_server}/api/v2",
                "secret_id": user.id,
                "secret_key": user.key,
            },
        }

        console.print(tmp_settings)

        tmp_config_file = Path(tmpdir) / "config.json"

        with open(tmp_config_file, "w") as f:
            f.write(json.dumps(tmp_settings))

        app = nordigen_cli.create_app()

        result = runner.invoke(
            app,
            [
                "-q",
                "--id",
                user.id,
                "--key",
                user.key,
                "--api",
                f"{test_server}/api/v2",
                "--config-dir",
                tmpdir,
                *args,
            ],
            # color=True,
            env={"REQUESTS_DEBUGGER": "1"},
        )

        console.print(result.stdout)
        console.print(result.stderr)
        assert result.exit_code == expected["exit_code"]
        for s in expected["stdout_strings"]:
            assert s in result.stdout
