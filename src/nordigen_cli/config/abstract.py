import functools
import inspect as std_inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional

from colorama import Back, Fore, Style


def pr_key(key):
    if "config_dir" in key:
        return f"{Back.LIGHTGREEN_EX}{key}{Style.RESET_ALL}"
    elif "active_profile" in key:
        return f"{Back.LIGHTBLACK_EX}{key}{Style.RESET_ALL}"
    else:
        return f"{Back.LIGHTCYAN_EX}{key}{Style.RESET_ALL}"


def pr_debug(key):
    caller_frame = std_inspect.stack()[1]
    caller_file = caller_frame.filename
    caller_lineno = caller_frame.lineno
    caller_function = caller_frame.function
    print(f"{caller_function}, line {caller_lineno}")


def logger_init(*args, **kwargs):
    def wrapper(func):
        name = func.__qualname__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            provider = None
            key = None
            for arg in args:
                if isinstance(arg, ConfigProviderBase):
                    provider = arg
                if isinstance(arg, str):
                    key = arg
            print(
                f"Entry: "
                f"func: {Fore.LIGHTMAGENTA_EX}{func}{Style.RESET_ALL} "
                f"provider: {Fore.GREEN}{provider}{Style.RESET_ALL} ",
            )
            result = func(*args, **kwargs)
            print(
                f"Exit: "
                f"func: {Fore.LIGHTMAGENTA_EX}{func}{Style.RESET_ALL} "
                f"result: {Fore.LIGHTCYAN_EX}{result}{Style.RESET_ALL} "
                f"key: {Fore.LIGHTCYAN_EX}{key}{Style.RESET_ALL} "
                f"provider: {Fore.GREEN}{provider}{Style.RESET_ALL} ",
            )
            return result

        return wrapped

    return wrapper


class ConfigProviderBase(ABC):
    """Base class for all configuration providers."""

    def __init__(self, manager: "ConfigManagerBase"):
        self._manager = manager

    @abstractmethod
    def get(
        self,
        key: str,
    ) -> Optional[Any]:
        pass

    @abstractmethod
    def get_all_keys(self) -> List[str]:
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        pass

    def __getattribute__(self, name):
        if name == "__dict__":
            d = super().__getattribute__("__dict__")
            return {k: v for k, v in d.items() if k != "_manager"}
        return super().__getattribute__(name)


class ConfigManagerBase(ABC):
    _providers: List["ProviderEntry"]

    def register(
        self, provider: ConfigProviderBase, priority: int
    ) -> "ConfigManagerBase":
        pass

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        pass


@dataclass
class ProviderEntry:
    provider: ConfigProviderBase
    priority: int

    def __rich_repr__(self):
        """
        Returns a rich representation of this object.
        """
        yield "priority", self.priority
        yield "provider", self.provider
