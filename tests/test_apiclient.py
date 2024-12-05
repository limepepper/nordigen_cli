from pathlib import Path

from api.auth import create_jwt_pair_for_uuid
from limepepper_utils.jwt.client import JWTValidator
from loguru import logger
from rich.console import Console

from nordigen_cli.apiclient.base import ClientState, NordigenClientBase
from nordigen_cli.apiclient.client import NordigenClient
from nordigen_cli.models.model import Account, Integration

console = Console()


class TestApiClient:
    """Test the NordigenClient class

    This class tests the NordigenClient class and its methods.

    """

    def test_api_test_clean_path(self, test_server, test_data):
        """test with good user, no token cached"""
        user = test_data["good_user"]
        api = NordigenClient(
            do_init=False,
        )
        assert api.state is ClientState.INITIAL
        api._post_init(
            secret_id=user.id,
            secret_key=user.key,
            api=f"{test_server}/api/v2",
        )
        assert api.state is ClientState.NO_TOKENS
        banks = api.list_banks("GB")
        assert len(banks) > 0
        assert api.state is ClientState.ACCESS_TOKEN_ACTIVE
        bank = banks[0]
        assert Integration.model_validate(bank)
        assert isinstance(bank, Integration)
        assert api.r_client.is_valid_token()
        old_token = api.r_client.get_authentication_method().get_token().token
        # print(f"account token : {old_token}")
        api.do_token_refresh()
        new_token = api.r_client.get_authentication_method().get_token().token
        # print(f"account token : {new_token}")
        assert old_token != new_token
        # send a request with a mock override
        banks = api.show_bank("some-bank-id")
        assert (
            JWTValidator.decode(new_token)["exp"]
            >= JWTValidator.decode(old_token)["exp"]
        )

    def test_api_test_cached_expired_token(self, test_server, test_data):
        """test with good user, token cached but expired"""
        user = test_data["good_user"]
        api_token = NordigenClient(
            id=user.id,
            key=user.key,
            api=f"{test_server}/api/v2",
        )
        # not_expired_pair = api_token.t_client.get_token_new()
        # assert not JWTValidator.is_expired(not_expired_pair.access)
        # assert not JWTValidator.is_expired(not_expired_pair.refresh)
        # assert api_token.state is ClientState.NO_TOKENS

        expired_pair = api_token.t_client.get_tokens(expiry_delta_sec=-1000)
        assert JWTValidator.is_expired(expired_pair[0])
        assert JWTValidator.is_expired(expired_pair[1])
        assert api_token.state is ClientState.NO_TOKENS

        def retrieve_callback(client):
            client.set_access_token(expired_pair[0])
            client.set_refresh_token(expired_pair[1])
            client.state = ClientState.ACCESS_TOKEN_ACTIVE

        api_cached = NordigenClient(
            id=user.id,
            key=user.key,
            api=f"{test_server}/api/v2",
            retrieve_callback=retrieve_callback,
        )

        # print(
        #     f"JWTValidator.expiry(expired_pair[0]): {JWTValidator.expiry(expired_pair[0].token)}"
        # )

        assert api_cached.state is ClientState.ACCESS_TOKEN_ACTIVE
        banks = api_cached.list_banks("GB")
        assert len(banks) > 0

    def test_api_disabled_login_good_cache(
        self,
        test_server,
        test_data,
        access_token_file,
        refresh_token_file,
    ):
        user = test_data["good_user"]
        access_token, refresh_token = create_jwt_pair_for_uuid(uuid=user.id)

        # signon_refresh_token = client.get_refresh_token()
        # console.print(signon_access_token)
        # console.print(signon_refresh_token)

        def retrieve_callback(client: NordigenClientBase):
            client.set_access_token(access_token)
            client.set_refresh_token(refresh_token)
            client.state = ClientState.ACCESS_TOKEN_ACTIVE

        def signon_callback(client: NordigenClientBase):
            Path(access_token_file).write_text(
                client.get_access_token().model_dump_json()
            )
            Path(refresh_token_file).write_text(
                client.get_refresh_token().model_dump_json()
            )

        api = NordigenClient(
            id=user.id,
            key=user.key,
            api=f"{test_server}/api/v2",
            # retrieve_callback=retrieve_callback,
            signon_callback=signon_callback,
        )
        banks = api.show_bank("some-bank-id")
        assert banks is not None

        an_account = api.get(f"{test_server}/api/v2/accounts/xxx/")
        assert Account.model_validate(an_account)

        api.do_signon_request()

    def test_api_cache_and_load(
        self,
        test_server,
        test_data,
        access_token_file,
        refresh_token_file,
    ):
        good_user_disabled = test_data["good_user_disabled"]
        access_token, refresh_token = create_jwt_pair_for_uuid(
            uuid=good_user_disabled.id
        )
        logger.trace(access_token)
        logger.trace(refresh_token)

        def signon_callback(client: NordigenClientBase):
            Path(access_token_file).write_text(
                client.get_access_token().model_dump_json()
            )
            Path(refresh_token_file).write_text(
                client.get_refresh_token().model_dump_json()
            )

        api = NordigenClient(
            id=good_user_disabled.id,
            key=good_user_disabled.key,
            api=f"{test_server}/api/v2",
            # retrieve_callback=retrieve_callback,
            signon_callback=signon_callback,
        )
        bank = api.show_bank("some-bank-id")
        assert bank.id is not None

        api.do_signon_request()
