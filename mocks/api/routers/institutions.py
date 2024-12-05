from typing import Annotated, Optional, Union

from factories import IntegrationFactory, IntegrationRetrieveFactory
from fastapi import APIRouter, Depends

from api.auth import get_user_by_token
from api.models.user import User
from nordigen_cli.models.model import (
    ErrorResponse,
    Integration,
    IntegrationRetrieve,
)

router = APIRouter()


# noinspection PyUnusedLocal
@router.get(
    "/",
    response_model=list[Integration],
    responses={
        "400": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def retrieve_all_institutions_for_country(
    user: Annotated[User, Depends(get_user_by_token)],
    access_scopes_supported: Optional[str] = None,
    account_selection_supported: Optional[str] = None,
    business_accounts_supported: Optional[str] = None,
    card_accounts_supported: Optional[str] = None,
    corporate_accounts_supported: Optional[str] = None,
    country: Optional[str] = None,
    payment_submission_supported: Optional[str] = None,
    payments_enabled: Optional[str] = None,
    pending_transactions_supported: Optional[str] = None,
    private_accounts_supported: Optional[str] = None,
    read_debtor_account_supported: Optional[str] = None,
    read_refund_account_supported: Optional[str] = None,
    ssn_verification_supported: Optional[str] = None,
) -> Union[list[Integration], ErrorResponse]:
    return IntegrationFactory.create_batch(10)


# noinspection PyUnusedLocal
@router.get(
    "/{institution_id}/",
    response_model=IntegrationRetrieve,
    responses={
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def retrieve_institution(
    user: Annotated[User, Depends(get_user_by_token)],
    institution_id: str,
) -> Union[IntegrationRetrieve, ErrorResponse]:
    return IntegrationRetrieveFactory.create()
