from abc import abstractmethod
from dataclasses import dataclass
from functools import reduce
from operator import getitem
from typing import Any, List, Optional

from colorama import Back, Style
from loguru import logger

from nordigen_cli.config.abstract import ConfigProviderBase


@dataclass
class ConfigContext:
    """Shared context available to all providers"""

    active_profile: str = "default"

    @classmethod
    def create_default(cls) -> "ConfigContext":
        return cls(
            active_profile=cls.active_profile,
        )


class ConfigProvider(ConfigProviderBase):

    @abstractmethod
    def _get_raw(self, key: str) -> Optional[Any]:
        """Get raw value without key splitting - to be implemented by providers"""
        pass

    def get(
        self,
        key: str,
    ) -> Optional[Any]:
        """
        Get value supporting dot notation for nested keys.
        Example: get("database.credentials.username")
        """
        logger.trace(
            f"ProviderBase get( {Back.GREEN}{key}{Style.RESET_ALL} ): in provider {self.__class__.__name__}"
        )
        # First try to get as a direct key
        value = self._get_raw(key)
        if value is not None:
            return value

        # If not found, try to traverse the nested structure
        parts = key.split(".")
        value = self._get_raw(parts[0])

        if value is None:
            return None

        try:
            # For subsequent parts, traverse the dict
            return reduce(getitem, parts[1:], value)

        except (KeyError, TypeError, AttributeError) as exc:
            # KeyError: dict key not found
            # TypeError: value is not subscriptable
            # AttributeError: value doesn't support getitem
            logger.trace(f"Error retrieving key '{key}': {exc}")
            return None

    def has(
        self,
        key: str,
    ) -> bool:
        """Default implementation checks if get() returns not None"""
        return self.get(key) is not None

    def get_all_keys(self) -> List[str]:
        """Optional method to list all available keys"""
        return []

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    def as_dict(self):
        """
        Returns the configuration settings as a dictionary.

        Returns:
            A dictionary containing the configuration settings.
        """
        return {key: self.get(key) for key in self.get_all_keys()}

    def __rich_repr__(self):
        """
        Returns a rich representation of this object.
        """
        # yield "hash", hash(self)
        yield "config", self.as_dict()
