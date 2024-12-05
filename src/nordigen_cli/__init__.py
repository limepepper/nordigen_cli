import importlib.metadata
import os
import sys

from loguru import logger
from rich.console import Console

__app_name__ = "nordigen_cli"
__version__ = importlib.metadata.version(__app_name__)

from nordigen_cli.config.manager import ConfigManager
from nordigen_cli.config.provider_defaults import BootstrapConfigProvider

# os.environ.setdefault("NO_HANDLE_EXCEPTIONS", "1")

console = Console()

filter_dict = {
    "": "DEBUG",
    "django": "INFO",
    # "nordigen_cli.apiclient.base": "TRACE",
}

esc = "\033]8;;http://hello.com\e\\link\033]8;;\e\\"
text = "Click here"
url = "https://example.com"
link = f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def custom_formatter(record):
    link = f"\033]8;;file://{record['file'].path}:{record['line']}\033\\{record['file'].name}:{record['line']}\033]8;;\033\\"
    # print(link)
    # print(record)
    # record["extra"].update({"link": link})
    return (
        "<green>{time:HH:mm:ss}</green>|"
        "<level>{level:<5.5}</level>|"
        # for some loguru reason the space or pipe after the link
        # has to be there, or it throws an error
        f"<magenta>{link}|</magenta>"
        "{message}\n"
    )


# inspect(logger, methods=True)
logger.remove()
logger.add(
    sys.stderr,
    filter=filter_dict,
    level="TRACE",
    format=custom_formatter,
)
