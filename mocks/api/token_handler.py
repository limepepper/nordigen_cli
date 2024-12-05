import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from fastapi import HTTPException
from jwt.exceptions import (
    InvalidTokenError,
)
from loguru import logger

from api.models.tokens import JWTConfig


@dataclass
class TokenBlacklist:
    """Simple in-memory blacklist for testing"""

    def __init__(self):
        self.blacklisted_jtis: set[str] = set()

    def is_blacklisted(self, jti: str) -> bool:
        return jti in self.blacklisted_jtis

    def blacklist(self, jti: str, ttl: 0) -> None:
        self.blacklisted_jtis.add(jti)


# class RedisTokenBlacklist:
#     """Redis-based token blacklist for production use"""
#
#     def __init__(self, redis_url: str):
#         self.redis = redis.from_url(redis_url)
#
#     def is_blacklisted(self, jti: str) -> bool:
#         return bool(self.redis.exists(f"blacklist:{jti}"))
#
#     def blacklist(self, jti: str, expire_in: int) -> None:
#         """Blacklist a token with expiry time in seconds"""
#         self.redis.setex(f"blacklist:{jti}", expire_in, "1")


class JWTHandler:
    """Server-side JWT handler with comprehensive validation"""

    def __init__(
        self,
        config: JWTConfig,
        blacklist: Optional[TokenBlacklist] = None,
    ):
        self.config = config
        # self.security = HTTPBearer()
        self.blacklist = blacklist or TokenBlacklist()

    def decode_token_simple(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.config.SECRET_KEY,
            algorithms=[self.config.ALGORITHM],
        )

    # jwt.get_unverified_header(encoded)

    def decode_token(self, token: str) -> dict:
        """Decode a JWT token without validation"""
        return jwt.decode(
            token,
            self.config.SECRET_KEY,
            algorithms=[self.config.ALGORITHM],
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_nbf": False,
                "verify_iat": False,
                "verify_iss": False,
                "verify_aud": False,
            },
        )

    def verify_token(self, token: str) -> dict:
        """Verify and validate JWT token"""

        payload = jwt.decode(
            token,
            self.config.SECRET_KEY,
            algorithms=[self.config.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": False,
                "verify_iss": False,
                "verify_aud": False,
                "require": ["exp", "uuid", "jti", "token_type"],
            },
            issuer=self.config.ISSUER,
            audience=self.config.AUDIENCE,
        )

        # Additional custom validations
        self._validate_token_type(payload)
        self._validate_custom_claims(payload)

        if "jti" not in payload:
            raise HTTPException(status_code=401, detail="Token missing JTI claim")

        # Check if token has been blacklisted
        if self.blacklist.is_blacklisted(payload["jti"]):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        return payload

    def _validate_token_type(self, payload: dict[str, Any]) -> None:
        """Validate token type (access vs refresh)"""
        token_type = payload.get("token_type")
        if not token_type or token_type not in ["access", "refresh"]:
            raise InvalidTokenError("Invalid token type")

    @staticmethod
    def _validate_custom_claims(payload: dict[str, Any]) -> None:
        """Validate any custom claims specific to your application"""
        # Example: validate user permissions
        if "permissions" in payload:
            if not isinstance(payload["permissions"], list):
                raise InvalidTokenError("Invalid permissions format")

    def revoke_token(self, token: str) -> None:
        """Revoke a token by adding its JTI to the blacklist"""
        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=["HS256"],
            )
            jti = payload["jti"]

            # Calculate remaining time until token expiry
            exp = datetime.fromtimestamp(payload["exp"], timezone.utc)
            now = datetime.now(timezone.utc)
            ttl = int((exp - now).total_seconds())

            if ttl > 0:
                self.blacklist.blacklist(jti, ttl)

        except jwt.InvalidTokenError:
            # If token is invalid, no need to blacklist it
            pass

    def _create_token(self, /, *, data, expires_delta: int) -> str:
        to_encode = data.copy()
        if expires_delta:
            logger.trace(f"expires_delta: {expires_delta}")
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        logger.trace(f"expire: {expire}")
        to_encode.update(
            {
                "exp": expire,
                "jti": str(uuid.uuid4()),
            }
        )
        return jwt.encode(
            to_encode,
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM,
        )


# # Token generation (for reference):
# def create_access_token(subject: str, permissions: list) -> str:
#     now = datetime.now(timezone.utc)
#
#     payload = {
#         "sub": subject,
#         "iat": now.timestamp(),
#         "exp": (now + timedelta(minutes=30)).timestamp(),
#         "nbf": now.timestamp(),
#         "iss": "nordigen-api",
#         "aud": "nordigen-clients",
#         "type": "access",
#         "permissions": permissions,
#     }
#
#     return jwt.encode(
#         payload, jwt_handler.config.SECRET_KEY, algorithm=jwt_handler.config.ALGORITHM
#     )
