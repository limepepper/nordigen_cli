import json
import uuid

import jwt
import pytest
import requests
from api.auth import create_jwt_pair_for_uuid
from api.models.tokens import JWTConfig
from api.token_handler import JWTHandler
from endpoints import CustomMeta, MyBaseEndpoint
from rich.console import Console

from nordigen_cli.apiclient.client import NordigenClient

console = Console()


class TestRefreshEndpoint:
    def test_can_refresh_good_token(
        self,
        test_server,
        test_data,
    ):
        user = test_data["good_user"]

        access_token, refresh_token = create_jwt_pair_for_uuid(
            uuid=user.id,
        )

        CustomMeta.__base_url__ = f"{test_server}/api/v2"
        response = requests.post(
            MyBaseEndpoint.token_refresh,
            data=json.dumps(
                {
                    "refresh": refresh_token.token,
                }
            ),
            headers={"content_type": "application/json"},
            timeout=10,
        )
        _ = response.json()

        assert response.status_code == 200

    def test_cant_refresh_token_bad_user(
        self,
        test_server,
        test_data,
    ):
        """generate a token with a non-existing uuid and try to refresh it. mock should check for the uuid and return 401"""

        bad_user_id = "xxx-yyy-xxx"

        access_token, refresh_token = create_jwt_pair_for_uuid(
            uuid=bad_user_id,
        )

        CustomMeta.__base_url__ = f"{test_server}/api/v2"
        response = requests.post(
            MyBaseEndpoint.token_refresh,
            data=json.dumps(
                {
                    "refresh": refresh_token.token,
                }
            ),
            headers={"content_type": "application/json"},
            timeout=10,
        )
        _ = response.json()

        assert response.status_code == 401

    def test_refreshes_when_about_to_expire(
        self,
        test_server,
        test_data,
    ):
        """test that behaviour when refresh and access tokens are about to expire"""

        access_token, refresh_token = create_jwt_pair_for_uuid(
            uuid=test_data["good_user"].id,
            expiry_delta_sec=5,
        )
        call_tracker = []
        client = NordigenClient(
            id=test_data["good_user"].id,
            key=test_data["good_user"].key,
            api=f"{test_server}/api/v2",
            retrieve_callback=lambda c: c.set_tokens(access_token, refresh_token),
            signon_callback=lambda c: call_tracker.append("signon"),
            refresh_callback=lambda c: call_tracker.append("refresh"),
        )
        # rinspect(client)
        assert client.access_token.should_refresh()
        assert client.refresh_token.should_refresh()
        # request triggers check of token expiry
        client.show_account_details(uuid.uuid4())
        assert "signon" in call_tracker
        # set access token to one that is about to expire
        client.set_access_token(access_token)
        client.show_account_details(uuid.uuid4())
        assert "refresh" in call_tracker
        call_tracker.clear()
        access_token, refresh_token = create_jwt_pair_for_uuid(
            uuid=test_data["good_user"].id,
            expiry_delta_sec=15,
        )
        client.set_tokens(access_token, refresh_token)
        assert not client.access_token.should_refresh()
        assert not client.refresh_token.should_refresh()

        client.show_account_details(uuid.uuid4())
        assert "signon" not in call_tracker
        assert "refresh" not in call_tracker

    def test_refused_different_secret(
        self,
        test_server,
        test_data,
    ):
        """test that behaviour when refresh and access tokens are about to expire"""

        handler1 = JWTHandler(
            config=JWTConfig(
                SECRET_KEY="secret1",
                ACCESS_TOKEN_EXPIRE_SECONDS=60,
                REFRESH_TOKEN_EXPIRE_SECONDS=60,
            )
        )

        handler2 = JWTHandler(
            config=JWTConfig(
                SECRET_KEY="secret2",
                ACCESS_TOKEN_EXPIRE_SECONDS=60,
                REFRESH_TOKEN_EXPIRE_SECONDS=60,
            )
        )

        token1 = handler1._create_token(
            data={
                "token_type": "access",
                "uuid": "123",
            },
            expires_delta=60,
        )

        handler1.verify_token(token1)

        with pytest.raises(jwt.exceptions.InvalidSignatureError):
            handler2.verify_token(token1)
