import os
from typing import Any, Optional

from nordigen_cli.config.provider_base import ConfigContext, ConfigProvider


class EnvironConfigProvider(ConfigProvider):
    def __init__(
        self,
        context: ConfigContext,
        prefix: str = "",
        separator: str = "_",
    ):
        super().__init__(context)

        self.prefix = prefix
        self.separator = separator
        self.env = os.environ

    def _env_to_key(self, env_key: str) -> str:
        """Convert environment variable name to config key"""
        if self.prefix and env_key.startswith(self.prefix):
            env_key = env_key[len(self.prefix) :]
        return env_key.lower().replace(self.separator, ".")

    def _key_to_env(self, key: str) -> str:
        """Convert config key to environment variable name"""
        env_key = key.upper().replace(".", self.separator)
        if self.prefix:
            env_key = f"{self.prefix}{env_key}"
        return env_key

    def get(self, key: str) -> Optional[Any]:
        env_key = self._key_to_env(key)
        return self.env.get(env_key)

    def has(self, key: str) -> bool:
        env_key = self._key_to_env(key)
        return env_key in self.env
