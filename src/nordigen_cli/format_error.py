from loguru import logger

from nordigen_cli import console

# import pprint


# import pprint


def show_config_report(config) -> None:
    """
    show the configuration error

    """
    logger.debug("showing configuration report")
    console.print("here2")
    console.print(config)

    config.is_valid()

    # if config.is_valid and config.validation_errors == []:
    #     print("config is [bold green]valid![/] All settings are correct")
    # elif config.is_valid:
    #     print("config is [bold yellow]valid![/] But there are some warnings. see below")
    # else:
    #     print("config is [bold red]invalid![/bold red] See below for details")
    #
    #
    # #
    # print("Settings")
    # console.print(Pretty(config.settings))
    #
    # for error in config.validation_errors:
    #     if isinstance(error, ValidationError):
    #         print("Validation Errors")
    #         for e in error.errors():
    #             pprint(e)
    #         # console.print(error)
    #     else:
    #         inspect(error)
