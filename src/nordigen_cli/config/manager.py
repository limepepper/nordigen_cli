from typing import Any, Dict, List, Optional

from colorama import Back, Fore, Style
from loguru import logger
from rich.console import Console

from nordigen_cli.config.abstract import (
    ConfigManagerBase,
    ConfigProviderBase,
    ProviderEntry,
    pr_key,
)
from nordigen_cli.config.cache import CacheStrategy, NoCache
from nordigen_cli.config.provider_base import (
    ConfigContext,
    ConfigProvider,
)

console = Console()


class ConfigManager(ConfigManagerBase):
    def __init__(
        self,
        context: Optional[ConfigContext] = None,
        cache_strategy: Optional[CacheStrategy] = None,
    ):
        self.context = context or ConfigContext.create_default()
        self._providers: List[ProviderEntry] = []
        self._cache = cache_strategy or NoCache()

        # Bootstrap with core config (config_dir and active_profile)
        self._bootstrap()

    def _bootstrap(self) -> None:
        """Initialize core configuration"""
        # Start with environment vars for core config
        # bootstrap_provider = BootstrapConfigProvider(self.context)

        # # Update context with any overrides from environment
        # if config_dir := bootstrap_provider.get("config_dir"):
        #     self.context.config_dir = Path(config_dir)
        # if profile := bootstrap_provider.get("active_profile"):
        #     self.context.active_profile = profile

    def register(self, provider: ConfigProvider, priority: int) -> "ConfigManager":
        entry = ProviderEntry(provider=provider, priority=priority)

        # Insert maintaining sort by priority (highest first)
        insert_idx = 0
        for idx, existing in enumerate(self._providers):
            if priority > existing.priority:
                break
            insert_idx = idx + 1
        self._providers.insert(insert_idx, entry)
        return self

    def get(
        self,
        key: str,
        default: Any = None,
        skip_cache: bool = False,
    ) -> Any:
        logger.trace(
            f"Manager {Fore.LIGHTBLUE_EX}getting{Style.RESET_ALL} ({pr_key(key)}"
        )
        value = self._get(key)
        # if not skip_cache:
        #     self._cache.set(key, value)
        logger.trace(
            f"Manager {Fore.LIGHTBLUE_EX}returning{Style.RESET_ALL} {pr_key(key)}={Fore.LIGHTMAGENTA_EX}{value=}{Style.RESET_ALL}"
        )
        return value

    def _get(
        self,
        key: str,
    ) -> Any:
        # try and get profile key first if it's not a dotted key
        cached_value = self._cache.get(key)
        if cached_value is not None:
            return cached_value
        # profile = self.get("active_profile")

        for entry in self._providers:
            if key != "active_profile" and "." not in key:
                if profile_value := self._get_profile_val(entry, key):
                    logger.trace(
                        f"_get returning {Fore.LIGHTMAGENTA_EX}{profile_value}{Style.RESET_ALL} for '{key}' in {Fore.LIGHTRED_EX}{entry.provider.__class__.__name__}{Style.RESET_ALL}"
                    )
                    return profile_value
            if result := self._get_root(entry, key):
                return result
            # finally look for the key in the profile defaults
            if profile_defaults_value := self._get_root(
                entry, f"_profile_defaults.{key}"
            ):
                return profile_defaults_value
        logger.warning(f"Key not found: {key}")
        # raise KeyError(f"Key not found: {key}")

    def _get_profile_val(
        self,
        entry,
        key: str,
    ) -> Any:
        profile_key = f"profiles.{self.get('active_profile')}.{key}"
        logger.trace(
            f"_get_profile looking for {Back.GREEN}{profile_key}{Style.RESET_ALL} in {Fore.LIGHTRED_EX}{entry.provider.__class__.__name__}{Style.RESET_ALL}"
        )
        if entry.provider.has(profile_key):
            logger.trace(
                f"_get_profile Found profile key: {Back.GREEN}{profile_key}{Style.RESET_ALL} in provider: {Fore.LIGHTRED_EX}{entry.provider.__class__.__name__}{Style.RESET_ALL}"
            )
            return entry.provider.get(profile_key)
        logger.trace(
            f"_get_profile didn't find {Back.GREEN}{profile_key}{Style.RESET_ALL} in provider {Fore.LIGHTRED_EX}{entry.provider.__class__.__name__}{Style.RESET_ALL}"
        )

    # @logger_init()
    def _get_root(
        self,
        entry,
        key: str,
    ) -> Any:
        logger.trace(
            f"_get_root looking in {Fore.LIGHTRED_EX}{entry.provider.__class__.__name__}{Style.RESET_ALL} for root ({pr_key(key)})"
        )
        if entry.provider.has(key):
            logger.trace(
                f"_get_root Found key: {pr_key(key)} in provider: {Fore.LIGHTRED_EX}{entry.provider.__class__.__name__}{Style.RESET_ALL}"
            )
            return entry.provider.get(key)
        logger.trace(
            f"_get_root returning{Fore.RED} None:{Style.RESET_ALL} key: {pr_key(key)} for {Fore.LIGHTRED_EX}{entry.provider.__class__.__name__}{Style.RESET_ALL}"
        )

    # def get_all(self, key: str) -> Dict[int, Any]:
    #     """Get all values for a key from each provider that has it"""
    #     return {
    #         entry.priority: entry.provider.get(key)
    #         for entry in self._providers
    #         if entry.provider.has(key)
    #     }

    def as_dict(self) -> Dict[str, Any]:
        """Return all configuration as a dictionary"""
        logger.trace(f"{Fore.RED}calling dict {Fore.RESET}")
        result = {}
        for key in self.get_all_keys():
            logger.trace(f"{Fore.RED}getting key '{Back.GREEN}{key=}{Style.RESET_ALL}'")
            result[key] = self.get(key)
        return result
        # return {key: self.get(key) for key in self.get_all_keys()}

    def get_all_keys(self) -> List[str]:
        """Get all unique keys from all providers"""
        keys = set()
        for entry in self._providers:
            keys.update(entry.provider.get_all_keys())
        logger.debug(f"{Fore.RED}keys: {keys}{Fore.RESET}")
        return sorted(list(keys))

    def get_provider_for_key(self, key: str) -> Optional[ConfigProviderBase]:
        """Find which provider owns a given key"""
        for entry in self._providers:
            if entry.provider.has(key):
                return entry.provider
        return None

    def __rich_repr__(self):
        yield "hash", hash(self)
        yield from self._providers
        yield "all_keys", self.get_all_keys()
        yield "computed", self.as_dict()

    def __getitem__(self, item):
        return self.get(item)

    def __iter__(self):
        return iter(self.get_all_keys())

    def __len__(self):
        return len(self.get_all_keys())

    def keys(self):
        return self.get_all_keys()
