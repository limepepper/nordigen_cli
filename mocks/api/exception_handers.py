from fastapi import status
from starlette.responses import JSONResponse

from nordigen_cli.models.model import ErrorResponse


async def token_expired(request, exc):
    # inspect(request)
    # inspect(exc)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"X-Error": "ExpiredSignatureError"},
        content=ErrorResponse(
            detail="Token is invalid or expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
            summary="Invalid token",
        ).model_dump(),
    )


async def sig_verif_failed(request, exc):
    # inspect(request)
    # inspect(exc)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"X-Error": "InvalidSignatureError"},
        content=ErrorResponse(
            detail="Token is invalid or expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
            summary="Invalid token",
        ).model_dump(),
    )


def user_unknown(request, exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"X-Error": "UnknownUserError"},
        content=ErrorResponse(
            detail="No active account found with the given credentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
            summary="Authentication failed",
        ).model_dump(),
    )


def incorrect_credentials(request, exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"X-Error": "IncorrectAccessCredentials"},
        content=ErrorResponse(
            detail="No active account found with the given credentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
            summary="Authentication failed",
        ).model_dump(),
    )


def hash_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"X-Error": f"passlib. exc. UnknownHashError: {exc}"},
        content=ErrorResponse(
            detail="No active account found with the given credentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
            summary="Authentication failed",
        ).model_dump(),
    )


def user_disabled(request, exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"X-Error": "UserDisabled - login suceeded but user is disabled"},
        content=ErrorResponse(
            detail="Login failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
            summary="Authentication failed",
        ).model_dump(),
    )
