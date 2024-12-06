from fastapi import APIRouter, FastAPI
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

from api.exception_handers import (
    hash_error,
    incorrect_credentials,
    sig_verif_failed,
    token_expired,
    user_disabled,
    user_unknown,
)
from api.models.user import (
    IncorrectAccessCredentialsError,
    UnknownUserError,
    UserDisabledError,
)
from api.routers import accounts, agreements, institutions, requisitions, token
from api.user_database import BadSaltError

tags_metadata = [
    {
        "name": "accounts",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "requisitions",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application"""
    app = FastAPI(
        title="GoCardless Bank Account Data API",
        version="2.0 (v2)",
        # servers=[{"url": "https://bankaccountdata.gocardless.com"}],
        servers=[{"url": "http://0.0.0.0:8000/"}],
        # openapi_tags=tags_metadata,
    )

    # @app.on_event("startup")
    # def on_startup():
    #     logger.info("Creating database and tables")
    #     create_db_and_tables()

    # session.add(hero)
    prefix = APIRouter(
        prefix="/api/v2",
    )
    # configure_error_handling(app)

    # Include routers
    prefix.include_router(
        accounts.router,
        prefix="/accounts",
        tags=["accounts"],
    )
    prefix.include_router(
        agreements.router,
        prefix="/agreements",
        tags=["agreements"],
    )
    prefix.include_router(
        institutions.router,
        prefix="/institutions",
        tags=["institutions"],
    )
    prefix.include_router(
        requisitions.router,
        prefix="/requisitions",
        tags=["requisitions"],
    )
    prefix.include_router(
        token.router,
        prefix="/token",
        tags=["token"],
    )

    app.include_router(prefix)
    app.add_exception_handler(ExpiredSignatureError, token_expired)
    app.add_exception_handler(InvalidSignatureError, sig_verif_failed)
    app.add_exception_handler(UnknownUserError, user_unknown)
    app.add_exception_handler(BadSaltError, hash_error)
    app.add_exception_handler(UserDisabledError, user_disabled)
    app.add_exception_handler(IncorrectAccessCredentialsError, incorrect_credentials)

    return app
