from apiclient import (
    endpoint,
)

BASE_URL = "https://bankaccountdata.gocardless.com/api/v2"


# Define endpoints, using the provided decorator.
@endpoint(base_url=BASE_URL)
class Endpoints:
    bank = "institutions/{id}/"
    banks = "institutions/?country={code}"
    agreement = "agreements/enduser/{id}/"
    agreements = "agreements/enduser/"
    requisition = "requisitions/{id}/"
    requisitions = "requisitions/"
    transactions = "accounts/{id}/transactions/"
