from datetime import UTC, datetime, timedelta

import pytest

from nordigen_cli.models.model import SpectacularJWTObtain

example_token = """
{
    "access": "string",
    "access_expires": 86400,
    "refresh": "string",
    "refresh_expires": 2592000
}
"""


class TestToken:
    def test_token_creation(self):
        access_token = "access_token_123"
        refresh_token = "refresh_token_456"
        access_expires = int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp())
        refresh_expires = int((datetime.now(tz=UTC) + timedelta(days=30)).timestamp())

        token = SpectacularJWTObtain(
            access=access_token,
            access_expires=access_expires,
            refresh=refresh_token,
            refresh_expires=refresh_expires,
        )

        assert token.access == access_token
        assert token.refresh == refresh_token
        assert token.access_expires == access_expires
        assert token.refresh_expires == refresh_expires

    def test_token_creation_with_invalid_access_token(self):
        with pytest.raises(ValueError):
            SpectacularJWTObtain(
                access=123,  # Invalid type
                access_expires=int(datetime.now(tz=UTC).timestamp()),  # Corrected
                refresh="valid_refresh",
                refresh_expires=int(datetime.now(tz=UTC).timestamp()),  # Corrected
            )

    def test_token_creation_with_invalid_refresh_token(self):
        with pytest.raises(ValueError):
            SpectacularJWTObtain(
                access="valid_access",
                access_expires=int(datetime.now(tz=UTC).timestamp()),  # Corrected
                refresh=456,  # Invalid type
                refresh_expires=int(datetime.now(tz=UTC).timestamp()),  # Corrected
            )

    def test_token_creation_with_invalid_access_expires(self):
        with pytest.raises(ValueError):
            SpectacularJWTObtain(
                access="valid_access",
                access_expires="invalid",  # Invalid type
                refresh="valid_refresh",
                refresh_expires=int(datetime.now(tz=UTC).timestamp()),
            )

    def test_token_creation_with_invalid_refresh_expires(self):
        with pytest.raises(ValueError):
            SpectacularJWTObtain(
                access="valid_access",
                access_expires=int(datetime.now(tz=UTC).timestamp()),
                refresh="valid_refresh",
                refresh_expires="invalid",  # Invalid type
            )
