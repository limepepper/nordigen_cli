import calendar
import time
from typing import List

from apiclient import (
    APIClient,
    HeaderAuthentication,
    JsonResponseHandler,
    JsonRequestFormatter,
)
from apiclient.paginators import paginated
from apiclient_pydantic import serialize_all_methods
from rich import inspect

from nordigen_cli.models.model import BankTransaction
from nordigen_cli.endpoints import Endpoints
from nordigen_cli.errors import MyErrorHandler
from nordigen_cli.models.agreement import Agreement
from nordigen_cli.models.bank import Bank

from nordigen_cli.utils import next_page_by_url

BASE_URL = "https://bankaccountdata.gocardless.com/api/v2"
base = "https://bankaccountdata.gocardless.com/api/v2"


@serialize_all_methods
class NordigenClient(APIClient):
    """Nordigen API client"""

    def __init__(self, **kwargs):
        if "token" in kwargs:
            """if we are the first of the class, we will set the token"""
            token = kwargs.pop("token")
            kwargs.update(
                authentication_method=HeaderAuthentication(
                    token=token,
                ),
                response_handler=JsonResponseHandler,
                error_handler=MyErrorHandler,
                request_formatter=JsonRequestFormatter,
            )
        super().__init__(**kwargs)

    def get_request_timeout(self):
        return 300

    # banks

    def list_banks(self, code) -> List[Bank]:
        return self.get(Endpoints.banks.format(code=code))

    def show_bank(self, bank_id) -> Bank:
        return self.get(Endpoints.bank.format(id=bank_id))

    # agreements

    def create_end_user_agreement(self, bank_id, enduser_id, max_historical_days=90):
        url = "{}/agreements/enduser/".format(base)
        data = {
            "institution_id": bank_id,
            "max_historical_days": max_historical_days,
            "access_scope": [
                "balances",
                "details",
                "transactions",
            ],
        }
        return self.post(url, data=data).json()

    # def list_endusers(self):
    #     url = "{}/agreements/enduser/".format(base)
    #     return self.get(url).json()

    def delete_agreement(self, agreement_id):
        url = "{}/agreements/enduser/{}/".format(base, agreement_id)
        print("deleting agreement with id: {}".format(url, agreement_id))
        return self.delete(url)

    @paginated(by_query_params=next_page_by_url)
    # @inspect_response
    def list_agreements(self, user_id) -> List[Agreement]:
        responses = self.get(Endpoints.agreements)
        result = [item for response in responses for item in response["results"]]
        # inspect(result)
        return result

    def show_agreement(self, agreement_id):
        return self.get(Endpoints.agreement.format(id=agreement_id))

    def accept_agreement(self, agreement_id, user_agent, ip_address):
        url = f"{base}/agreements/enduser/{agreement_id}/accept/"
        data = {"user_agent": user_agent, "ip_address": ip_address}
        return self.put(url, data=data).json()

    # requisitions

    def list_requisitions(self):
        return self.get(Endpoints.requisitions).json()

    def delete_requisitions(self, id):
        url = "{}/requisitions/{}".format(base, id)
        print("deleting requisition with id: {}".format(url, id))
        return self.delete(url)

    def create_requisition(
        self,
        institution_id,
        reference=None,
        /,
        *,
        redirect_url="http://localhost:5000/redirect",
        agreement=None,
        user_language="EN",
    ):
        url = "{}/requisitions/".format(base)
        data = {
            "redirect": redirect_url,
            "institution_id": institution_id,
            "user_language": user_language,
        }
        if not reference:
            reference = "ref_" + str(calendar.timegm(time.gmtime()))
        data["reference"] = reference
        if agreement:
            data["agreement"] = agreement

        inspect(data)

        return self.post(url, data=data)

    def show_requisition(self, requisition_id):
        return self.get(Endpoints.requisition.format(id=requisition_id))

    # accounts

    def show_account_metadata(self, id):
        url = "{}/accounts/{}/".format(base, id)
        return self.get(url)

    def show_account_detail(self, id):
        url = "{}/accounts/{}/details/".format(base, id)
        return self.get(url)

    def show_balance(self, id):
        url = "{}/accounts/{}/balances/".format(base, id)
        return self.get(url)

    # account transactions

    # @inspect_response
    def list_transactions(self, account_id) -> BankTransaction:
        return self.get(Endpoints.transactions.format(id=account_id))
