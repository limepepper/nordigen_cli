import json
from pathlib import Path

from rich.console import Console

from nordigen_cli.config.manager import ConfigManager
from nordigen_cli.config.provider_base import ConfigContext
from nordigen_cli.config.provider_defaults import BootstrapConfigProvider
from nordigen_cli.config.provider_dict import DictConfigProvider
from nordigen_cli.config.provider_file import FileConfigProvider

console = Console()

import pytest

test_config_data = [
    {
        "description": "minimal config",
        "cli_args": {
            "output_format": "yaml",
        },
        "user_file": {
            "active_profile": "default",
            "profiles": {
                "default": {
                    "api": "http://localhost",
                    "secret_id": "123",
                    "secret_key": "456",
                },
                "other": {
                    "api": "http://localhost/api/v2",
                    "secret_id": "abc",
                    "secret_key": "def",
                },
            },
            "verbose": 5,
            "output_format": "rich",
        },
        "defaults": {
            "active_profile": "default",
            "config_dir": "/some/config/dir",
            "profiles": {
                "default": {
                    "key": "value",
                },
                "profilex": "what about a random string",
            },
        },
        "computed": {
            "active_profile": "default",
            "verbose": 5,
            "output_format": "yaml",
            "config_dir": Path("/some/config/dir"),
            "secret_id": "123",
            "secret_key": "456",
            "profiles.other.secret_id": "abc",
            "access_token_file": Path("/some/config/dir/default/access.json"),
        },
    },
    {
        "cli_args": {
            "value": 2,
            "secret_key": "xxx",
        },
        "user_file": {
            "active_profile": "default",
            "profiles": {
                "default": {
                    "verbose": 3,
                    "output_format": "rich",
                },
                "not_active": {
                    "verbose": 6,
                    "output_format": "rich",
                },
            },
            "verbose": 5,
            "output_format": "rich",
        },
        "defaults": {
            "active_profile": "default",
            "verbose": 1,
            "output_format": "rich",
            "config_dir": Path.home() / ".config" / "nordigen_cli",
        },
        "computed": {
            "active_profile": "default",
            "verbose": 3,
            "output_format": "rich",
            "secret_key": "xxx",
            "config_dir": Path.home() / ".config" / "nordigen_cli",
        },
    },
    {
        "description": "cli args override config dir, active profile",
        "cli_args": {
            "active_profile": "some_active_profile",
            "secret_key": "xxx",
            "config_dir": "/tmp/xxx",
        },
        "user_file": {
            "active_profile": "default",
            "profiles": {
                "default": {
                    "verbose": 3,
                    "output_format": "rich",
                },
                "not_active": {
                    "verbose": 6,
                    "output_format": "rich",
                },
            },
            "verbose": 5,
            "output_format": "json",
        },
        "defaults": {},
        "computed": {
            "active_profile": "some_active_profile",
            "config_dir": "/tmp/xxx",
            "access_token_file": Path("/tmp/xxx/some_active_profile/access.json"),
            "output_format": "json",
            # "secret_key": "xxx",
            # "config_dir": Path.home() / ".config" / "nordigen_cli",
        },
    },
    {
        "description": "override config dir, should get config file from new dir",
        "cli_args": {
            "active_profile": "some_active_profile",
            "secret_key": "xxx",
            "config_dir": "/tmp/new_config_dir",
        },
        "user_file": {
            "active_profile": "default",
            "profiles": {
                "default": {
                    "verbose": 3,
                    "output_format": "rich",
                },
                "not_active": {
                    "verbose": 6,
                    "output_format": "rich",
                },
                "active_profile": {
                    "verbose": 6,
                    "output_format": "rich",
                },
            },
            "verbose": 5,
            "output_format": "json",
        },
        "defaults": {},
        "computed": {
            "active_profile": "some_active_profile",
            "config_dir": "/tmp/new_config_dir",
            "access_token_file": Path(
                "/tmp/new_config_dir/some_active_profile/access.json"
            ),
            "output_format": "json",
            "refresh_token_file": Path(
                "/tmp/new_config_dir/some_active_profile/refresh.json"
            ),
            # "secret_key": "xxx",
            # "config_dir": Path.home() / ".config" / "nordigen_cli",
        },
    },
]


@pytest.fixture
def config_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("config_dir")


@pytest.fixture
def config_file(tmp_path_factory):
    return tmp_path_factory.mktemp("config_dir") / "config.json"


@pytest.fixture
def generate_config_data(tmp_path_factory):
    def generator():
        yield from test_config_data

    return generator


class TestConfigProvider:
    @pytest.mark.parametrize("config_data", test_config_data)
    def test_with_unreadable_user_config_file(
        self,
        config_data,
        config_file,
        mocker,
    ):
        with open(config_file, "w") as f:
            f.write(json.dumps(test_config_data[0]["user_file"]))

        mocker.patch("builtins.open", side_effect=OSError("Mocked IOError"))

        config_mgr = ConfigManager()
        with pytest.raises(IOError, match="Mocked IOError"):
            config_mgr.register(
                FileConfigProvider(
                    config_mgr.context,
                    config_file=config_file,
                ),
                10,
            )

    @pytest.mark.parametrize("config_data", test_config_data)
    def test_get_config_provider_overrides(
        self,
        config_data,
        mocker,
        config_dir,
        config_file,
    ):
        print("")

        if "user_file" in config_data:
            with open(config_file, "w") as f:
                f.write(json.dumps(config_data["user_file"]))

        mocker.patch(
            "limepepper_utils.xdg.XDGBasedir.get_xdg_config_home",
            return_value=Path(config_dir),
        )

        config_mgr = ConfigManager(
            ConfigContext(
                active_profile="dev",
            )
        )

        config_mgr.register(
            BootstrapConfigProvider(
                config_mgr,
                config_data["defaults"] if "defaults" in config_data else {},
            ),
            10,
        )
        config_mgr.register(
            FileConfigProvider(
                config_mgr,
                config_file=config_file,
            ),
            50,
        )
        config_mgr.register(
            DictConfigProvider(
                config_mgr,
                config_data["cli_args"],
            ),
            100,
        )
        # rinspect(config_mgr)
        # logger.debug("config_mgr: {}", config_mgr=config_mgr)
        # print("got here")
        # console.print("got here1")
        # console.print(config_mgr)

        for key, value in config_data["computed"].items():
            assert config_mgr.get(key) == value
