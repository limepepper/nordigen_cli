import jwt
import pytest
from api.auth import jwt_handler

request_data = [
    {
        "token": "xxx",
        "valid": False,
        "exceptions": {
            "decode": jwt.exceptions.DecodeError,
            "validate": None,
        },
    },
    {
        "token": "xxx.xxx.xxx",
        "valid": False,
        "exceptions": {
            "decode": jwt.exceptions.DecodeError,
            "validate": None,
        },
    },
    {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzb21lIHVzZXIiLCJleHAiOjE3MzI0MzU3OTl9.4Qp-hSlbZHdykzcYv6rD8PnWcK",
        "valid": False,
        "exceptions": {
            "decode": None,
            "validate": jwt.exceptions.InvalidSignatureError,
        },
    },
]


class TestTokenValidation:
    @pytest.mark.parametrize(
        "token,valid,exceptions",
        [tuple(d.values()) for d in request_data],
    )
    def test_get_token(
        self, token: str, valid: bool, exceptions: dict[str, type[Exception]]
    ):
        if exception := exceptions.get("decode"):
            with pytest.raises(exception):
                _ = jwt_handler.decode_token(token)
            return
        if exception := exceptions.get("validate"):
            with pytest.raises(exception):
                _ = jwt_handler.verify_token(token)
            return
        assert jwt_handler.decode_token(token)
        assert jwt_handler.verify_token(token)
