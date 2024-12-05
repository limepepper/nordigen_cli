import uuid

import pytest
import requests
from endpoints import CustomMeta, MyBaseEndpoint
from pydantic import ValidationError
from request_test_cases import Dat

import nordigen_cli
from nordigen_cli.apiclient.client import NordigenClient
from nordigen_cli.apiclient.errors import (
    NordigenClientError,
)
from nordigen_cli.models.model import Integration, JWTObtainPairRequest
from nordigen_cli.models.token import AccessToken

request_data = [
    {
        "endpoint": "api/v2/token/new/",
        "headers": {},
        "json": JWTObtainPairRequest(
            secret_id="test",
            secret_key="test",
        ).model_dump(),
    },
    # {
    #     "endpoint": "api/v2/token/refresh/",
    #     "headers": {},
    #     "json": JWTRefreshRequest(
    #         refresh="test",
    #     ).model_dump(),
    # },
]


class TestMockApi:
    @pytest.mark.parametrize(
        "endpoint,headers,json",
        [tuple(d.values()) for d in request_data],
    )
    def test_get_token(self, test_server, endpoint, headers, json):
        response = requests.post(
            f"{test_server}/{endpoint}",
            headers=headers,
            json=json,
            timeout=10,
        )
        _ = response.json()

    @pytest.mark.parametrize(
        "endpoint,headers,json",
        [tuple(d.values()) for d in request_data],
    )
    def test_with_api_client(self, test_server, endpoint, headers, json):
        # response = requests.post(
        #     f"{test_server}/{endpoint}", headers=headers, json=json
        # )
        # _ = response.json()
        CustomMeta.__base_url__ = f"{test_server}/api/v2"
        # inspect(MyBaseEndpoint)
        api = NordigenClient(
            id="rjeiogjrigojreiogjreiogjreo",
            key="erhgurehgiuerhgiuhrgiuhrgiurughiuerhguierhgiurhegi",
            endpoints=MyBaseEndpoint,
        )
        with pytest.raises(NordigenClientError) as exc_info:
            _ = api.do_signon_request()
        assert exc_info.value.status_code == 401

    def test_get_banks(
        self,
        test_server,
    ):
        CustomMeta.__base_url__ = f"{test_server}/api/v2"
        # inspect(MyBaseEndpoint)
        api = NordigenClient(
            id="rjeiogjrigojreiogjreiogjreo",
            key="erhgurehgiuerhgiuhrgiuhrgiurughiuerhguierhgiurhegi",
            endpoints=MyBaseEndpoint,
        )
        api.set_access_token(
            AccessToken.from_jwt_str(Dat.expired_token),
        )
        with pytest.raises(nordigen_cli.apiclient.errors.AuthenticationFailedError):
            _ = api.list_banks("gb", headers={"X-Test": f"Bearer {Dat.expired_token}"})

        api.set_access_token(
            AccessToken.from_jwt_str(Dat.bad_short_token),
        )

        with pytest.raises(ValueError):
            api.list_banks("gb")

        with pytest.raises(nordigen_cli.apiclient.errors.AuthenticationFailedError):
            jwt = api.do_signon_request()
            api.set_access_token(AccessToken.from_jwt_str(jwt.access))

        # with pytest.raises(nordigen_cli.apiclient.errors.AuthenticationFailedError):
        #     response = api.list_banks("gb")

    def test_show_token(self, test_server):
        CustomMeta.__base_url__ = f"{test_server}/api/v2"
        api = NordigenClient(
            id="rjeiogjrigojreiogjreiogjreo",
            key="erhgurehgiuerhgiuhrgiuhrgiurughiuerhguierhgiurhegi",
            endpoints=MyBaseEndpoint,
        )

        # with pytest.raises(nordigen_cli.apiclient.errors.AuthenticationFailedError):
        api.set_access_token(
            AccessToken.from_jwt_str(Dat.expired_token),
        )

        with pytest.raises(nordigen_cli.apiclient.errors.AuthenticationFailedError):
            api.get(MyBaseEndpoint.token_show)

    def test_get_banks_2(self, test_server):
        CustomMeta.__base_url__ = f"{test_server}/api/v2"
        api = NordigenClient(
            id="rjeiogjrigojreiogjreiogjreo",
            key="erhgurehgiuerhgiuhrgiuhrgiurughiuerhguierhgiurhegi",
            endpoints=MyBaseEndpoint,
        )

        with pytest.raises(nordigen_cli.apiclient.errors.AuthenticationFailedError):
            api.set_access_token(AccessToken.from_jwt_str(Dat.expired_token))
            response = api.list_banks(
                "gb", headers={"X-Test": "token expired and invalid"}
            )
            assert response is not None
            assert isinstance(response, list)

    def test_uuid_endpoint(self, test_server, good_user_and_tokens):
        user, access_token, refresh_token = good_user_and_tokens
        client = NordigenClient(
            id=user.id,
            key=user.key,
            api=f"{test_server}/api/v2",
        )
        banks = client.list_banks("GB")
        assert len(banks) > 0
        assert isinstance(banks, list)
        assert all(isinstance(bank, Integration) for bank in banks)

        with pytest.raises(ValidationError):
            client.show_agreement("xxx")

        with pytest.raises(ValidationError):
            client.show_account_metadata("xxx")

        client.show_agreement(uuid.uuid4())
