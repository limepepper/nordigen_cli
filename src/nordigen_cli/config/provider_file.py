from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from nordigen_cli.config.abstract import ConfigManagerBase
from nordigen_cli.config.provider_base import ConfigProvider


class FileConfigProvider(ConfigProvider):
    def __init__(
        self,
        manager: ConfigManagerBase,
        config_file: Path = None,
    ):
        super().__init__(manager)
        self.config_file = config_file or manager.get("config_file")
        self.data: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        if self.config_file.exists():
            self.data.update(self._load_file(self.config_file))
        else:
            logger.debug(f"Config file not found: {self.config_file}")

    def _load_file(self, path: Path) -> Dict[str, Any]:
        import json

        with open(path) as f:
            return json.load(f)

    def get_all_keys(self) -> List[str]:
        return list(self.data.keys())

    def _get_raw(self, key: str) -> Optional[Any]:
        return self.data.get(key)
