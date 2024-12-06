from typing import Annotated, Union

from fastapi import APIRouter, Depends

from api.auth import (
    create_jwt_pair,
    get_current_token,
    get_user_by_id_key,
    refresh_access,
)
from api.models.user import User
from nordigen_cli.models.model import (
    ErrorResponse,
    JWTRefreshRequest,
    SpectacularJWTObtain,
    SpectacularJWTRefresh,
)

router = APIRouter()


@router.post(
    "/new/",
    response_model=SpectacularJWTObtain,
    responses={
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
    },
)
def obtain_new_access_and_refresh_token_pair(
    user: Annotated[User, Depends(get_user_by_id_key)],
    expiry_delta_sec: int | None = None,
) -> Union[SpectacularJWTObtain, ErrorResponse]:
    # user = authenticate_user(credentials)
    return SpectacularJWTObtain(**create_jwt_pair(user, expiry_delta_sec))


@router.post(
    "/refresh/",
    response_model=SpectacularJWTRefresh,
    responses={
        "403": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
    },
)
def get_a_new_access_token(
    refresh_request: JWTRefreshRequest,
    expiry_delta_sec: int | None = None,
) -> Union[SpectacularJWTRefresh, ErrorResponse]:
    return SpectacularJWTRefresh(
        **refresh_access(refresh_request, expiry_delta_sec),
    )


@router.get("/show/")
async def show_token(
    token: Annotated[str, Depends(get_current_token)],
    # payload: Dict[str, Any] = Depends(jwt_handler.verify_token)
):
    # Token is valid if we get here
    # payload contains the decoded token claims
    # inspect(token)
    return {"stuff": "Access granted", "user": token}
