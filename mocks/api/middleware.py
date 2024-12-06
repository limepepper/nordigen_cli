import typing

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel, ValidationError
from starlette.middleware.base import BaseHTTPMiddleware


class PSD2ErrorResponse(BaseModel):
    """Standardized PSD2 error response format"""

    summary: str
    detail: str
    status_code: int
    type: typing.Optional[str] = None


class PSD2ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Map different exception types to appropriate PSD2 error responses
            if isinstance(exc, ValidationError):
                return JSONResponse(
                    status_code=400,
                    content=PSD2ErrorResponse(
                        summary="Validation Error",
                        detail=str(exc),
                        status_code=400,
                        type="validation_error",
                    ).model_dump(),
                )
            elif isinstance(exc, HTTPException):
                # Handle FastAPI's built-in HTTPException
                return JSONResponse(
                    status_code=exc.status_code,
                    content=PSD2ErrorResponse(
                        summary=str(exc.detail),
                        detail=str(exc.detail),
                        status_code=exc.status_code,
                    ).model_dump(),
                )
            elif isinstance(exc, ExpiredSignatureError):
                return JSONResponse(
                    status_code=401,
                    content=PSD2ErrorResponse(
                        summary="Token Expired",
                        detail="The provided token has expired",
                        status_code=401,
                        type="token_expired",
                    ).model_dump(),
                )
            elif isinstance(exc, InvalidTokenError):
                return JSONResponse(
                    status_code=401,
                    content=PSD2ErrorResponse(
                        summary="Invalid Token",
                        detail="The provided token is invalid",
                        status_code=401,
                        type="invalid_token",
                    ).model_dump(),
                )
            else:
                # Log unexpected errors here if needed
                return JSONResponse(
                    status_code=500,
                    content=PSD2ErrorResponse(
                        summary="Internal Server Error",
                        detail=str(exc),
                        status_code=500,
                        type="internal_error",
                    ).model_dump(),
                )


# Update your FastAPI app to use the middleware
def configure_error_handling(app: FastAPI) -> None:
    """Configure PSD2 error handling for the FastAPI application"""
    app.add_middleware(PSD2ErrorHandlerMiddleware)
