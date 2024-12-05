from pathlib import Path

from limepepper_utils.file.utility import backup_file
from limepepper_utils.inspect.inspect import logger_init
from loguru import logger
from pydantic import ValidationError

from nordigen_cli.apiclient.base import ClientState, NordigenClientBase
from nordigen_cli.apiclient.client import NordigenClient
from nordigen_cli.models.token import BaseToken

alias_args = {"no_args_is_help": True, "hidden": True}


def init_dirs(settings):
    for dir_path in [
        settings.access_token_file,
        settings.refresh_token_file,
    ]:
        if not dir_path.parent.exists():
            logger.info(f"Creating local config directory: {dir_path.parent}")
            dir_path.parent.mkdir(exist_ok=True)


@logger_init()
def get_client(settings):
    init_dirs(settings)

    def retrieve_callback(client: NordigenClientBase):
        try:
            a_from_file = BaseToken.from_json(
                Path(settings.access_token_file).read_text()
            )
            client.set_access_token(a_from_file)
            client.state = ClientState.ACCESS_TOKEN_ACTIVE
            logger.debug(f"Loaded access token from {settings.access_token_file}")
        except FileNotFoundError as e:
            logger.debug(f"No access token found: {e}")
        except ValidationError as e:
            logger.error(f"ValidationError loading access token: {e}")

        try:
            r_from_file = BaseToken.from_json(
                Path(settings.refresh_token_file).read_text()
            )
            client.set_refresh_token(r_from_file)
            logger.debug(f"Loaded request token from {settings.refresh_token_file}")
        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError loading request token: {e}")
        except ValidationError as e:
            logger.error(f"ValidationError loading request token: {e}")

    def signon_callback(client: NordigenClientBase):
        try:
            backup_file(settings.access_token_file)
            Path(settings.access_token_file).write_text(
                client.get_access_token().model_dump_json(indent=4)
            )
            logger.debug(f"Saved access token to {settings.access_token_file}")
        except Exception as e:
            logger.error(f"Error saving access token: {e}")

        try:
            backup_file(settings.refresh_token_file)
            Path(settings.refresh_token_file).write_text(
                client.get_refresh_token().model_dump_json(indent=4)
            )
            logger.debug(f"Saved request token to {settings.refresh_token_file}")
        except Exception as e:
            logger.error(f"Error saving request token: {e}")

    def refresh_callback(client: NordigenClientBase):
        try:
            backup_file(settings.access_token_file)
            Path(settings.access_token_file).write_text(
                client.get_access_token().model_dump_json(indent=4)
            )
            logger.debug(
                f"Saved access token to {settings.access_token_file} due to refresh"
            )
        except Exception as e:
            logger.error(f"Error saving access token: {e}")

    return NordigenClient(
        api=settings.api,
        id=settings.secret_id,
        key=settings.secret_key,
        retrieve_callback=retrieve_callback,
        signon_callback=signon_callback,
        refresh_callback=refresh_callback,
    )
