from typing import Any, Dict, List, Optional

from nordigen_cli.config.abstract import ConfigManagerBase
from nordigen_cli.config.provider_base import ConfigProvider


class DictConfigProvider(ConfigProvider):
    def __init__(self, manager: ConfigManagerBase, data: Dict[str, Any]):
        super().__init__(manager)
        self.data = data

    def _get_raw(self, key: str) -> Optional[Any]:
        return self.data.get(key)

    def get_all_keys(self) -> List[str]:
        return list(self.data.keys())

    def has(self, key: str) -> bool:
        return key in self.data
