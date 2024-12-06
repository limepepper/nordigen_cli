from pathlib import Path
from typing import Annotated

import typer
from loguru import logger
from rich import inspect
from rich.console import Console

from nordigen_cli.commands.client import get_client
from nordigen_cli.format_output import FormattingManager
from nordigen_cli.models.token import BaseToken
from nordigen_cli.settings import SettingsRuntime

console = Console()

app = typer.Typer(
    no_args_is_help=True,
    name="config",
)


@app.command(
    name="init",
    # help="interact with the config and **settings**",
    # epilog="Made with :heart: in [blue]Venus[/blue]",
)
def config_init(
    ctx: typer.Context,
) -> None:
    """
    create the user initial configuration file

    """
    logger.trace("initializing configuration")
    ctx.obj.init_config()


@app.command(
    name="dump",
    rich_help_panel="Debug and Info",
)
@app.command("show", hidden=True, no_args_is_help=True)
def config_dump(
    ctx: typer.Context,
) -> None:
    """
    dump the **configuration**

    Learn more at the [Typer docs website](https://typer.tiangolo.com)
    """
    logger.debug("dumping configuration")
    config_mgr = ctx.obj

    console.print(config_mgr)
    console.print(config_mgr.get("profiles"))
    console.print(config_mgr.get("active_profile"))

    profile = config_mgr.get("active_profile")
    if profile not in config_mgr.get("profiles"):
        print("Profile not found")
        logger.error(f"Profile not found: {profile}")
        raise typer.Exit(78)

    FormattingManager().format_output(
        ctx.obj,
        config_mgr.get("output_format"),
    )
    print("All settings are correct")
    console.print("here")
    settings = SettingsRuntime.model_validate(
        {k: config_mgr.get(k) for k in SettingsRuntime.model_fields.keys()},
    )
    console.print(settings)


@app.command(
    name="reset",
    # rich_help_panel="Debug and Info",
)
def config_reset(
    confirm: Annotated[
        bool,
        typer.Option(
            prompt="Are you sure you want to reset the configuration?",
        ),
    ],
):
    inspect(confirm)


@app.command(
    name="tokens",
    # rich_help_panel="Debug and Info",
)
def config_show_tokens(
    ctx: typer.Context,
) -> None:
    settings = ctx.obj.settings
    for f in (settings.access_token_file, settings.request_token_file):
        try:
            token = BaseToken.from_json(Path(f).read_text())
            console.print(token)
        except FileNotFoundError as e:
            logger.error(f"Error loading token file: {e}")
            continue


@app.command(
    name="client",
    # help="interact with the config and **settings**",
)
@app.command(
    name="s",
    hidden=True,
)
def client_show(
    ctx: typer.Context,
) -> None:
    """
    show the api client configuration

    """
    logger.trace("show client configuration")
    if not ctx.obj.is_valid:
        logger.trace("config is not valid")
        raise typer.Exit(1)

    api_client = get_client(ctx.obj.settings)

    inspect(ctx.obj.settings)
    inspect(api_client)
