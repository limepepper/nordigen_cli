from apiclient import (
    endpoint,
)

BASE_URL = "xxxhttps://bankaccountdata.gocardless.com/api/v2"


@endpoint(base_url=BASE_URL)
class Endpoints:
    token_new = "token/new/"  # noqa: S105
    token_refresh = "token/refresh/"  # noqa: S105
    bank = "institutions/{id}/"
    banks = "institutions/?country={code}"
    agreement = "agreements/enduser/{id}/"
    agreements = "agreements/enduser/"
    agreement_accept = "agreements/enduser/{agreement_id}/accept/"
    requisition = "requisitions/{id}/"
    requisitions = "requisitions/"
    transactions = "accounts/{id}/transactions/"
    account_metadata = "accounts/{account_id}/metadata/"
    account_details = "accounts/{account_id}/details/"
    account_balances = "accounts/{account_id}/balances/"


class BaseEndpoints:
    token_new = "token/new/"  # noqa: S105
    token_refresh = "token/refresh/"  # noqa: S105
    bank = "institutions/{id}/"
    banks = "institutions/?country={code}"
    agreement = "agreements/enduser/{id}/"
    agreements = "agreements/enduser/"
    agreement_accept = "agreements/enduser/{id}/accept/"
    requisition = "requisitions/{id}/"
    requisitions = "requisitions/"
    transactions = "accounts/{id}/transactions/"
    # account_metadata = "accounts/{account_id}/metadata/"
    account_metadata = "accounts/{id}/"
    account_details = "accounts/{id}/details/"
    account_balances = "accounts/{id}/balances/"


# # Define endpoints, using the provided decorator.
# @endpoint(base_url=BASE_URL)
# class Endpoints(BaseEndpoints):
#     pass
