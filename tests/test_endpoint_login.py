import importlib.util

import pytest
import requests

from nordigen_cli.models.model import JWTObtainPairRequest

post_request_data = [
    {
        "endpoint": "/token/new/",
        "headers": {"X-Test": "failed login - no user"},
        "json": JWTObtainPairRequest(
            secret_id="test",
            secret_key="test",
        ).model_dump(),
        "valid": False,
        "exceptions": {
            "verify_password": None,
            "validate": None,
        },
        "status_code": 401,
    },
    {
        "endpoint": "/token/new/",
        "headers": {"X-Test": "failed login - bad hash"},
        "json": JWTObtainPairRequest(
            secret_id="716642b2-977f-4ca9-a723-f36b84676c89",
            secret_key="test",
        ).model_dump(),
        "valid": False,
        "exceptions": {
            "verify_password": None,
            "validate": None,
        },
        "status_code": 401,
    },
    {
        "endpoint": "/token/new/",
        "headers": {"X-Test": "failed login - user disabled"},
        "json": JWTObtainPairRequest(
            secret_id="fcc71b93-ac1c-4dda-81ac-4402ca9a455e",
            secret_key="9be0ecad2f17e59d9f8f548549bb03c6cf145388ece13159ce9a6c4fa1e1304c309a7094926c0874ebe8c75d0dfecb630d73be1c33b76978895e49cafc08d52a",
        ).model_dump(),
        "valid": False,
        "exceptions": {
            "verify_password": None,
            "validate": None,
        },
        "status_code": 401,
    },
    {
        "endpoint": "/token/new/",
        "headers": {"X-Test": "failed login - user disabled"},
        "json": JWTObtainPairRequest(
            secret_id="7946d2f5-f7d2-4f25-8d01-f1a9434e0b6f",
            secret_key="fa3316421e8d3574f3e3b2bd7e8849622dba0340cb77763259ddb15e9362973e90b39ce50dc8313c893eae2613f3298c57430f770d48e246d971a8643365c67d",
        ).model_dump(),
        "valid": True,
        "exceptions": {
            "verify_password": None,
            "validate": None,
        },
        "status_code": 200,
    },
]


class TestUserLoginEndpoint:
    @pytest.mark.parametrize(
        "endpoint,headers,json,valid,exceptions,status_code",
        [tuple(d.values()) for d in post_request_data],
    )
    def test_param_logins(
        self,
        test_server,
        endpoint,
        headers,
        json,
        valid,
        exceptions,
        status_code: int,
    ):
        importlib.import_module("requests_debugger")
        api_prefix = "/api/v2"
        response = requests.post(
            f"{test_server}{api_prefix}{endpoint}",
            headers=headers,
            json=json,
            timeout=10,
        )
        # if response.headers.get("Content-Type") == "application/json":
        try:
            _ = response.json()
        except Exception:
            _ = response.text
        assert response.status_code == status_code
