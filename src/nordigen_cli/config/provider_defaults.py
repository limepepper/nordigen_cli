import contextvars
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from limepepper_utils.merge import recursive_merge
from limepepper_utils.xdg import XDGBasedir
from loguru import logger
from rich.console import Console

from nordigen_cli import __app_name__
from nordigen_cli.config.abstract import ConfigManagerBase
from nordigen_cli.config.provider_base import ConfigProvider

console = Console()


no_recurse_mode = contextvars.ContextVar("no_recurse_mode", default=False)


class BootstrapConfigProvider(ConfigProvider):
    def __init__(
        self,
        manager: "ConfigManagerBase",
        defaults: Dict[str, Any] = None,
    ):
        super().__init__(manager)
        # build up from defaults, allowing overriding at each stage

        self.data = recursive_merge(
            self._get_necessary_vals(),
            self.get_default_config(),
            defaults or {},
        )
        with self.no_recurse(True):
            self.data = recursive_merge(
                self.data,
                self._get_config(),
            )
        # logger.debug(f"====> bootstrap data {self.data}")

    @staticmethod
    def _get_necessary_vals() -> Optional[Any]:
        """values that are required for minimal operation of the app"""
        return {
            "config_dir": XDGBasedir.get_app_dir(__app_name__),
            "active_profile": "default",
        }

    def _get_raw(self, key: str) -> Optional[Any]:
        # do again, to allow paths to be resolved

        self.data = recursive_merge(
            self.data,
            self._get_config(),
        )
        # logger.debug(f"====> getting key {key} from {self.data}")
        # logger.debug("")

        result = self.data.get(key)

        return result

    @contextmanager
    def no_recurse(self, no_recurse: bool = False):
        token = no_recurse_mode.set(no_recurse)
        try:
            yield self
        finally:
            no_recurse_mode.reset(token)

    def _get_config(self):
        """further values that are required for minimal operation of the app"""
        if no_recurse_mode.get():
            logger.trace("in no recurse mode for config_dir")
            config_dir: Path = Path(self.data.get("config_dir"))
        else:
            logger.trace("in recursing mode for config_dir")
            with self.no_recurse(True):
                config_dir: Path = Path(self._manager.get("config_dir"))
        if no_recurse_mode.get():
            logger.trace("in no recurse mode for active_profile")
            active_profile = self.data.get("active_profile")
        else:
            logger.trace("in recursing mode for active_profile")
            with self.no_recurse(True):
                active_profile: str = self._manager.get("active_profile")
        result = {
            "config_dir": config_dir,
            "config_file": config_dir / "config.json",
            "_profile_defaults": {
                "access_token_file": config_dir / active_profile / "access.json",
                "refresh_token_file": config_dir / active_profile / "refresh.json",
            },
        }
        return result

    @staticmethod
    def get_default_config():
        """values that get written to the default config file"""
        return {
            "verbose": 1,
            "output_format": "rich",
            "active_profile": "default",
            "profiles": {
                "default": {
                    "api": "https://bankaccountdata.gocardless.xcom/api/v2",
                    "secret_id": "<your-id-here>",
                    "secret_key": "<your-key-here",
                }
            },
        }

    def get_all_keys(self) -> List[str]:
        """merge the root keys with the profile keys"""
        return list(self.data.keys())

    def __rich_repr__(self):
        """
        Returns a rich representation of this object.
        """
        # yield "hash", hash(self)
        yield "config", self.as_dict()
        yield "default_config", self.get_default_config()
