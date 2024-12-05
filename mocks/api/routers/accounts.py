from datetime import date
from typing import Annotated, Optional, Union

from factories import (
    AccountBalanceFactory,
    AccountDetailFactory,
    AccountFactory,
    AccountTransactionsFactory,
)
from fastapi import APIRouter, Depends

from api.auth import get_user_by_token
from api.models.user import User
from nordigen_cli.models.model import (
    Account,
    AccountBalance,
    AccountDetail,
    AccountTransactions,
    ErrorResponse,
)

router = APIRouter()


# noinspection PyUnusedLocal
@router.get(
    "/{account_id}/",
    response_model=Account,
    responses={
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
def retrieve_account_metadata(
    user: Annotated[User, Depends(get_user_by_token)],
    account_id: str,
) -> Union[Account, ErrorResponse]:
    return AccountFactory.create()


# noinspection PyUnusedLocal
@router.get(
    "/{account_id}/balances/",
    response_model=AccountBalance,
    responses={
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "400": {"model": ErrorResponse},
        "500": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "503": {"model": ErrorResponse},
    },
)
def retrieve_account_balances(
    user: Annotated[User, Depends(get_user_by_token)],
    account_id: str,
) -> Union[AccountBalance, ErrorResponse]:
    return AccountBalanceFactory.create()


# noinspection PyUnusedLocal
@router.get(
    "/{account_id}/details/",
    response_model=AccountDetail,
    responses={
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "400": {"model": ErrorResponse},
        "500": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "503": {"model": ErrorResponse},
    },
)
def retrieve_account_detail(
    user: Annotated[User, Depends(get_user_by_token)],
    account_id: str,
) -> Union[AccountDetail, ErrorResponse]:
    """Access account details.

    Account details will be returned in Berlin Group PSD2 format."""
    return AccountDetailFactory.create()


# noinspection PyUnusedLocal
@router.get(
    "/{account_id}/transactions/",
    response_model=AccountTransactions,
    responses={
        "404": {"model": ErrorResponse},
        "429": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "400": {"model": ErrorResponse},
        "500": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "503": {"model": ErrorResponse},
    },
)
def retrieve_account_transactions(
    user: Annotated[User, Depends(get_user_by_token)],
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    account_id: str = ...,
) -> Union[AccountTransactions, ErrorResponse]:
    return AccountTransactionsFactory.create()
