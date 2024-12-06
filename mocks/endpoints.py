#
#
#


class CustomMeta(type):
    __base_url__ = "http://example.dev"

    def __getattribute__(cls, name):
        attribute = super().__getattribute__(name)
        if (
            callable(attribute)
            or not isinstance(attribute, str)
            or name.startswith("__")
        ):
            return attribute
        return f"{super().__getattribute__("__base_url__")}/{attribute}"


# @endpoint(base_url=BASE_URL)
class MyBaseEndpoint(metaclass=CustomMeta):
    token_new = "token/new/"  # noqa: S105
    token_refresh = "token/refresh/"  # noqa: S105
    token_show = "token/show/"  # noqa: S105
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
