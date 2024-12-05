import os
import signal
import sys
from pathlib import Path
from typing import Annotated, Optional, cast

import pycountry
import typer
from fast_api.config import FormatChoices
from limepepper_utils.inspect import rinspect
from limepepper_utils.typer import debug
from loguru import logger
from pycountry.db import Country
from rich.console import Console

from nordigen_cli import (
    BootstrapConfigProvider,
    ConfigManager,
    __app_name__,
    __version__,
)
from nordigen_cli.commands import config
from nordigen_cli.commands.accounts import accounts
from nordigen_cli.commands.agreements import agreements
from nordigen_cli.commands.approvals import approvals
from nordigen_cli.commands.banks import bank
from nordigen_cli.commands.callbacks import (
    _callback_profile,
    _version_callback,
    id_callback,
    key_callback,
)
from nordigen_cli.commands.requisitions import requisitions
from nordigen_cli.config.provider_dict import DictConfigProvider
from nordigen_cli.config.provider_file import FileConfigProvider
from nordigen_cli.exception_handler import setup_exception_handling
from nordigen_cli.format_output import FormattingManager
from nordigen_cli.settings import SettingsRuntime

APP_NAME = "nordigen-cli"

console = Console()


def signal_handler(sig, frame):
    logger.warning("You pressed Ctrl+C!")
    raise typer.Exit(code=130)


def create_app(config_mgr=None) -> typer.Typer:

    cli = typer.Typer(
        # no_args_is_help=True,
        # add_completion=False,
        pretty_exceptions_enable=False,
        rich_markup_mode="rich",
        pretty_exceptions_short=False,
    )

    signal.signal(signal.SIGINT, signal_handler)

    if config_mgr is None:
        config_mgr = ConfigManager()
        config_mgr.register(
            BootstrapConfigProvider(config_mgr),
            10,
        )

    cli.add_typer(approvals)
    cli.add_typer(config.app)
    cli.add_typer(bank)
    cli.add_typer(agreements)
    cli.add_typer(requisitions)
    cli.add_typer(accounts)
    cli.add_typer(debug.app)

    @cli.command("version")
    @cli.command("v", hidden=True)
    def version():
        typer.echo(f"{__app_name__} v{__version__}")

    # noinspection PyUnusedLocal
    @cli.callback(
        invoke_without_command=True,
        # no_args_is_help=True,
    )
    def callback(
        ctx: typer.Context,
        _: Annotated[
            Optional[bool],
            typer.Option(
                "--version",
                callback=_version_callback,
                is_eager=True,
            ),
        ] = None,
        verbose: Annotated[
            Optional[int],
            typer.Option(
                ...,
                "--verbose",
                "--verbosity",
                "-v",
                envvar="NORDIGEN_VERBOSITY",
                count=True,
                help="More is better",
                min=0,
                # max=1000,
                # callback=callback_verbose,
                # hidden=True,
            ),
        ] = None,
        quiet: Annotated[
            Optional[int],
            typer.Option(
                ...,
                "-q",
                envvar="NORDIGEN_QUIET",
                count=True,
                help="More is better",
                min=0,
                # max=1000,
                # callback=callback_verbose,
                hidden=True,
            ),
        ] = None,
        active_profile: Annotated[
            Optional[str],
            typer.Option(
                ...,
                "--profile",
                "-p",
                show_default=config_mgr.get("active_profile"),
                case_sensitive=False,
                # is_eager=True,
                callback=_callback_profile,
                help="override profile settings, select a specific [green]profile[/green]",
            ),
        ] = None,
        secret_id: Annotated[
            str,
            typer.Option(
                ...,
                "--id",
                "--secret-id",
                envvar="NORDIGEN_ID",
                show_default=False,
                show_envvar=False,
                callback=id_callback,
                help="Nordigen API secret ID",
                rich_help_panel="Override config file settings",
            ),
        ] = None,
        secret_key: Annotated[
            str,
            typer.Option(
                ...,
                "--key",
                "--secret-key",
                envvar="NORDIGEN_KEY",
                show_default=False,
                show_envvar=False,
                help="Nordigen API secret Key",
                callback=key_callback,
                rich_help_panel="Override config file settings",
            ),
        ] = None,
        api: Annotated[
            str,
            typer.Option(
                ...,
                "--api",
                "--api-url",
                envvar="NORDIGEN_API",
                show_default=False,
                show_envvar=False,
                help="Nordigen API Url path",
                # callback=key_callback,
                rich_help_panel="Override config file settings",
            ),
        ] = None,
        config_file: Annotated[
            Path,
            typer.Option(
                ...,
                "--config-file",
                "-c",
                envvar="CONFIG_FILE",
                show_envvar=False,
                help="Load configuration from specific file",
                show_default=config_mgr.get("config_file"),
                rich_help_panel="Override config file settings",
            ),
        ] = None,
        config_dir: Annotated[
            Path,
            typer.Option(
                ...,
                "--config-dir",
                "-d",
                envvar="CONFIG_DIR",
                show_envvar=False,
                help="Override default configuration directory",
                show_default=config_mgr.get("config_dir"),
                rich_help_panel="Override config file settings",
                hidden=True,
            ),
        ] = None,
        access_token_file: Annotated[
            Path,
            typer.Option(
                ...,
                "--access-token-file",
                "-a",
                show_default=config_mgr.get("access_token_file"),
                help="Look for initial access token in specific file",
                rich_help_panel="Override config file settings",
                show_envvar=False,
                envvar="ACCESS_TOKEN_FILE",
                # callback=_callback_access_token_file,
                hidden=True,
            ),
        ] = None,
        refresh_token_file: Annotated[
            Path,
            typer.Option(
                ...,
                "--refresh-token-file",
                "-r",
                show_default=config_mgr.get("refresh_token_file"),
                help="Look for initial refresh token in specific file",
                rich_help_panel="Override config file settings",
                show_envvar=False,
                envvar="REFRESH_TOKEN_FILE",
                # callback=_callback_refresh_token_file,
                hidden=True,
            ),
        ] = None,
        output_format: Annotated[
            Optional[FormatChoices],
            typer.Option(
                ...,
                "--output-format",
                "--format",
                "-f",
                case_sensitive=False,
            ),
        ] = None,
    ):
        """Nordigen API client"""
        logger.debug("in the main callback")
        if ctx.params.get("quiet"):
            ctx.params["verbose"] = 0

        if not ctx.obj:
            config_mgr.register(FileConfigProvider(config_mgr), 50)
            config_mgr.register(DictConfigProvider(config_mgr, ctx.params), 100)
            # console.print(config_mgr)

            settings = SettingsRuntime.model_validate(
                {k: config_mgr.get(k) for k in SettingsRuntime.model_fields.keys()},
            )

            ctx.obj = config_mgr
            ctx.obj.settings = settings

        else:
            logger.warning("ctx.obj already set with value")
            rinspect(ctx.obj)
            sys.exit(1)

        # inspect(ctx)
        if ctx.invoked_subcommand is None:
            typer.echo("No subcommand invoked")
            ctx.get_help()

    country_codes = [
        {k: v for (k, v) in dict(cast(Country, c)).items() if k in ["name", "alpha_2"]}
        for c in pycountry.countries
    ]

    @cli.command("list-country-codes")
    def list_country_codes(ctx: typer.Context):
        """list ISO 3166 2-letter country codes"""
        # inspect(ctx.obj)
        display = ctx.obj.display
        data = country_codes
        # print(json.dumps(data))
        FormattingManager().format_output(data, display.output_format)

    return cli


def main():
    """Entry point for CLI"""
    signal.signal(signal.SIGINT, signal_handler)
    app = create_app()

    if not os.getenv("NO_HANDLE_EXCEPTIONS"):
        setup_exception_handling(app)

    app()


if __name__ == "__main__":
    main()
