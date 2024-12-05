import json
from datetime import datetime, timedelta, timezone
from typing import Annotated

from limepepper_utils.jwt.client import JWTValidationError, JWTValidator
from loguru import logger
from pydantic import (
    AfterValidator,
    BaseModel,
    field_validator,
    model_validator,
)

"""
example_data = {
    "access": "string",
    "access_expires": 86400,
    "refresh": "string",
    "refresh_expires": 2592000
}
"""


class TokenLoadingError(Exception):
    original_exception: Exception

    def __init__(self, original_exception: Exception):
        self.original_exception = original_exception
        super().__init__(f"Error loading token: {original_exception}")


class BaseToken(BaseModel):
    token: Annotated[str, AfterValidator(JWTValidator.validate_jwt_format)]
    expires_str: int = 86400
    expires_at: datetime = None

    def check_expiry(self):
        if self.should_refresh():
            raise JWTValidationError("Token expired")

    def should_refresh(self, buffer: int = 10) -> bool:
        """refresh if expired or about to expire"""
        expiry_cutoff = datetime.now(timezone.utc) + timedelta(seconds=buffer)
        logger.trace(f"now time  :    '{datetime.now(timezone.utc)}'")
        logger.trace(f"expires_at:    '{self.expires_at}'")
        logger.trace(f"expiry_cutoff: '{expiry_cutoff}'")
        if self.expires_at < expiry_cutoff:
            return True
        return False

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, dt: datetime):
        if dt.tzinfo is None:
            raise JWTValidationError(f"expires_at must be timezone-aware {dt}")
        return dt

    @field_validator("token")
    @classmethod
    def validate_token(cls, value):
        """trivial validation that token looks at least like a jwt"""
        return JWTValidator.validate_jwt_format(value)

    @model_validator(mode="before")
    @classmethod
    def compute_expires_at(cls, values):
        """Compute expires_at from token exp field."""
        if not ("expires_at" in values and values.get("expires_at")):
            values["expires_at"] = JWTValidator.expiry(values["token"])
        if isinstance(values["expires_at"], str):
            values["expires_at"] = datetime.fromisoformat(values["expires_at"])
        if values["expires_at"].tzinfo is None:
            values["expires_at"] = values["expires_at"].replace(tzinfo=timezone.utc)
        return values

    @classmethod
    def from_jwt_str(cls, jwt_str: str):
        decoded = JWTValidator.decode(jwt_str)
        return cls(
            expires_at=datetime.fromtimestamp(decoded["exp"], timezone.utc),
            token=jwt_str,
        )

    @classmethod
    def from_dict(cls, data: dict):
        decoded = JWTValidator.decode(data["token"])
        if decoded["token_type"] == "access":  # noqa: S105
            return AccessToken(**data)
        elif decoded["token_type"] == "refresh":  # noqa: S105
            return RefreshToken(**data)
        raise ValueError(f"Unknown token type: {decoded['token_type']}")

    @classmethod
    def from_json(cls, json_str: str):
        return BaseToken.from_dict(json.loads(json_str))

    def __rich_repr__(self):
        length = 60
        yield from (
            self.token[0 + i : length + i] for i in range(0, len(self.token), length)
        )
        yield (
            "expires_at",
            (
                self.expires_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.expires_at
                else None
            ),
        )
        yield "expires_str", self.expires_str
        yield "payload", JWTValidator.decode(self.token)
        yield "header", JWTValidator.header(self.token)


class AccessToken(BaseToken):
    def as_nord_dict(self):
        return {
            "access": self.token,
            "access_expires": self.expires_str,
        }


class RefreshToken(BaseToken):
    def as_nord_dict(self):
        return {
            "refresh": self.token,
            "refresh_expires": self.expires_str,
        }
