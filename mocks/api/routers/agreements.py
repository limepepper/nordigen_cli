from typing import Annotated, Any, Optional, Union
from uuid import UUID, uuid4

from factories import (
    EndUserAgreementFactory,
    PaginatedEndUserAgreementListFactory,
)
from fastapi import APIRouter, Depends
from pydantic import conint

from api.auth import get_user_by_token
from api.models.user import User
from nordigen_cli.models.model import (
    EnduserAcceptanceDetailsRequest,
    EndUserAgreement,
    EndUserAgreementRequest,
    ErrorResponse,
    PaginatedEndUserAgreementList,
)

router = APIRouter()


# noinspection PyUnusedLocal
@router.get(
    "/enduser/",
    response_model=PaginatedEndUserAgreementList,
    responses={
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def retrieve_all_euas_for_an_end_user(
    user: Annotated[User, Depends(get_user_by_token)],
    limit: Optional[conint(ge=1)] = 100,
    offset: Optional[conint(ge=0)] = 0,
    pretty: bool = False,
) -> Union[PaginatedEndUserAgreementList, ErrorResponse, Any]:
    return PaginatedEndUserAgreementListFactory.create(
        base_url="http://127.0.0.1:8000/api/v2/agreements/enduser/",
    )


# noinspection PyUnusedLocal
@router.get(
    "/enduser/{agreement_id}/",
    response_model=EndUserAgreement,
    responses={
        "404": {"model": ErrorResponse},
        "400": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def retrieve_eua_by_id(
    user: Annotated[User, Depends(get_user_by_token)],
    agreement_id: UUID,
) -> Union[EndUserAgreement, ErrorResponse]:
    result = EndUserAgreementFactory.create()
    return result


# noinspection PyUnusedLocal
@router.post(
    "/enduser/",
    response_model=None,
    responses={
        "201": {"model": EndUserAgreement},
        "400": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "402": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def create__e_u_a(
    user: Annotated[User, Depends(get_user_by_token)],
    body: EndUserAgreementRequest,
) -> Union[EndUserAgreement, ErrorResponse]:
    return EndUserAgreementFactory.create()


# noinspection PyUnusedLocal
@router.delete(
    "/enduser/{agreement_id}/",
    response_model=None,
    responses={
        "400": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def delete_eua_by_id(
    user: Annotated[User, Depends(get_user_by_token)],
    agreement_id: UUID,
) -> Optional[ErrorResponse]:
    random_uuid = uuid4()
    return ErrorResponse(
        summary="Agreement deleted",
        status_code=200,
        detail=f"Agreement {random_uuid} deleted",
    )


# noinspection PyUnusedLocal
@router.put(
    "/enduser/{agreement_id}/accept/",
    response_model=EndUserAgreement,
    responses={
        "405": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "400": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
    },
)
def accept__e_u_a(
    user: Annotated[User, Depends(get_user_by_token)],
    agreement_id: UUID,
    body: EnduserAcceptanceDetailsRequest = ...,
) -> Union[EndUserAgreement, ErrorResponse]:
    return EndUserAgreementFactory.create()
