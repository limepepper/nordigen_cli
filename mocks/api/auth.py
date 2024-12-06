from typing import Annotated

import jwt
from config import Config
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from loguru import logger
from sqlmodel import Session

from api.db import SessionDep
from api.models.user import (
    IncorrectAccessCredentialsError,
    UnknownUserError,
    User,
    UserDisabledError,
)
from api.token_handler import JWTHandler
from api.user_database import UserDb
from nordigen_cli.models.model import (
    JWTObtainPairRequest,
    JWTRefreshRequest,
)
from nordigen_cli.models.token import AccessToken, RefreshToken

# # SECRET_KEY = (
#     "9d05ca96de47dd8ffbf310829d64616b3927f27133247367569728eb49a142d9"  # noqa: S105
# )

# Available authorizations
# jwtAuth  (http, Bearer)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="",
    tokenUrl="",
    scheme_name="jwtAuth",
)


jwt_handler = JWTHandler(
    Config.get_handler(),
)


def get_current_token(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
):
    return jwt_handler.decode_token(token)


def get_user_by_token(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
) -> User:
    decode = jwt_handler.decode_token(token)
    header = jwt.get_unverified_header(token)
    logger.trace(f"decoded token: {decode} header: {header}")
    payload = jwt_handler.verify_token(token)
    username: str = payload.get("uuid")
    return UserDb.get_user(username)


def get_user_by_id_key(
    credentials: JWTObtainPairRequest,
    session: SessionDep,
):
    user = authenticate_user(session, credentials)
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_user_by_token)],
):
    if current_user.disabled:
        raise UserDisabledError(current_user.username)
    return current_user
    # if not hero:
    #     raise HTTPException(status_code=404, detail="Hero not found")


def is_user(
    user_id: str,
) -> User | bool:
    try:
        return UserDb.get_user(user_id)
    except UnknownUserError:
        return False


def is_user_active(
    user_id: str,
) -> bool:
    if user := is_user(user_id):
        return not user.disabled
    return False


def authenticate_user(
    session: Session,
    request: JWTObtainPairRequest,
):
    logger.trace(f"authenticate_user: request: {request}")
    user = UserDb.get_user(request.secret_id)
    logger.trace(f"authenticate_user: user {user}")
    if not UserDb.verify_password(request.secret_key, user.hashed_password):
        raise IncorrectAccessCredentialsError(f"incorrect credentials {user}")
    if user.disabled:
        raise UserDisabledError(f" user disbled {user}")
    return user


def create_jwt_pair(
    user: User,
    expiry_delta_sec: int | None = None,
) -> dict:
    """
    from creds create a pair of JWT tokens
    """

    access_token, refresh_token = create_jwt_pair_for_uuid(user.id, expiry_delta_sec)

    result = {
        "access": access_token.token,
        "access_expires": jwt_handler.config.ACCESS_TOKEN_EXPIRE_SECONDS,
        "refresh": refresh_token.token,
        "refresh_expires": jwt_handler.config.REFRESH_TOKEN_EXPIRE_SECONDS,
    }

    return result


def create_jwt_token(
    uuid: str,
    expiry_delta_sec: int | None = None,
    token_type: str = "access",  # noqa: S107
):
    logger.trace(f"expiry_delta_sec: {expiry_delta_sec}")
    token = jwt_handler._create_token(
        data={
            "token_type": token_type,
            "uuid": uuid,
        },
        expires_delta=expiry_delta_sec,
    )
    return token


def create_jwt_pair_for_uuid(
    uuid: str,
    expiry_delta_sec: int | None = None,
    refresh_expiry_delta_sec: int | None = None,
) -> tuple[AccessToken, RefreshToken]:
    """
    from creds create a pair of JWT tokens
    """
    logger.trace(f"expiry_delta_sec: {expiry_delta_sec}")
    access = create_jwt_token(
        uuid=uuid,
        expiry_delta_sec=(
            expiry_delta_sec
            if expiry_delta_sec
            else jwt_handler.config.ACCESS_TOKEN_EXPIRE_SECONDS
        ),
    )
    logger.trace(f"create_jwt_pair: for {uuid} here is the access token: {access}")

    refresh = create_jwt_token(
        uuid=uuid,
        expiry_delta_sec=(
            refresh_expiry_delta_sec
            if refresh_expiry_delta_sec
            else (
                expiry_delta_sec
                if expiry_delta_sec
                else jwt_handler.config.REFRESH_TOKEN_EXPIRE_SECONDS
            )
        ),
        token_type="refresh",  # noqa: S106
    )

    access_token = AccessToken(
        token=access,
        expires_str=jwt_handler.config.ACCESS_TOKEN_EXPIRE_SECONDS,
    )
    refresh_token = RefreshToken(
        token=refresh,
        expires_str=jwt_handler.config.REFRESH_TOKEN_EXPIRE_SECONDS,
    )
    return access_token, refresh_token


def refresh_access(
    refresh_request: JWTRefreshRequest,
    expiry_delta_sec: int | None = None,
) -> dict:
    token = refresh_request.refresh
    logger.trace(f"refreshing: here is the refresh token: {token}")
    decode = jwt_handler.decode_token(token)
    header = jwt.get_unverified_header(token)
    logger.trace(f"refresh: decoded token: {decode} header: {header}")
    payload = jwt_handler.verify_token(token)
    username: str = payload.get("uuid")
    if is_user_active(username):
        return do_refresh_access(refresh_request, expiry_delta_sec)
    raise UserDisabledError(username)


def do_refresh_access(
    refresh_request: JWTRefreshRequest,
    expiry_delta_sec: int | None = None,
) -> dict:
    token = refresh_request.refresh
    logger.trace(f"refreshing: here is the refresh token: {token}")
    decode = jwt_handler.decode_token(token)
    header = jwt.get_unverified_header(token)
    logger.trace(f"refresh: decoded token: {decode} header: {header}")
    jwt_handler.verify_token(token)

    access = jwt_handler._create_token(
        data={
            "token_type": "access",
            "uuid": decode["uuid"],
        },
        expires_delta=(
            expiry_delta_sec
            if expiry_delta_sec
            else jwt_handler.config.ACCESS_TOKEN_EXPIRE_SECONDS
        ),
    )
    logger.trace(f"refreshing: token from handler: {access}")
    result = {
        "access": access,
        "access_expires": (jwt_handler.config.ACCESS_TOKEN_EXPIRE_SECONDS),
    }
    logger.trace(f"refreshing: result dict: {result}")
    return result
