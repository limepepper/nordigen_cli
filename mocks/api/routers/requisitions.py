from typing import Annotated, Optional, Union
from uuid import UUID, uuid4

from factories import (
    PaginatedRequisitionListFactory,
    RequisitionFactory,
    SpectacularRequisitionFactory,
)
from fastapi import APIRouter, Depends
from pydantic import conint

from api.auth import get_user_by_token
from api.models.user import User
from nordigen_cli.models.model import (
    ErrorResponse,
    PaginatedRequisitionList,
    Requisition,
    RequisitionRequest,
    SpectacularRequisition,
)

router = APIRouter()


# noinspection PyUnusedLocal
@router.get(
    "/",
    response_model=PaginatedRequisitionList,
    responses={
        "404": {"model": ErrorResponse},
        "400": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def retrieve_all_requisitions(
    user: Annotated[User, Depends(get_user_by_token)],
    limit: Optional[conint(ge=1)] = 100,
    offset: Optional[conint(ge=0)] = 0,
) -> Union[PaginatedRequisitionList, ErrorResponse]:
    return PaginatedRequisitionListFactory.create(
        base_url="http://127.0.0.1:8000/api/v2/requisitions/",
    )


# noinspection PyUnusedLocal
@router.post(
    "/",
    response_model=None,
    responses={
        "201": {"model": SpectacularRequisition},
        "400": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "402": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def create_requisition(
    user: Annotated[User, Depends(get_user_by_token)],
    body: RequisitionRequest,
) -> Optional[Union[SpectacularRequisition, ErrorResponse]]:
    return SpectacularRequisitionFactory.create()


# noinspection PyUnusedLocal
@router.get(
    "/{requisition_id}/",
    response_model=Requisition,
    responses={
        "404": {"model": ErrorResponse},
        "400": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def get_requisition_by_id(
    user: Annotated[User, Depends(get_user_by_token)],
    requisition_id: UUID,
) -> Union[Requisition, ErrorResponse]:
    return RequisitionFactory.create()


# noinspection PyUnusedLocal
@router.delete(
    "/{requisition_id}/",
    # response_model=None,
    responses={
        "400": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def delete_requisition_by_id(
    user: Annotated[User, Depends(get_user_by_token)],
    requisition_id: UUID,
) -> Optional[ErrorResponse]:
    random_uuid = uuid4()
    return ErrorResponse(
        summary="Requisition deleted",
        status_code=200,
        detail=f"Requisition {random_uuid} deleted with all its End User Agreements",
    )
