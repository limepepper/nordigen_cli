
from apiclient import APIClient, HeaderAuthentication
import time
import calendar
from datetime import date

base = "https://ob.nordigen.com/api"


class NordigenClient(APIClient):

    # banks

    def list_banks(self, code):
        url = "{}/aspsps/?country={}".format(base, code)
        return self.get(url).json()

    def show_bank(self, id):
        url = "{}/aspsps/{}/".format(base, id)
        return self.get(url).json()

    # requisitions

    def list_requisitions(self):
        url = "{}/requisitions/".format(base)
        return self.get(url).json()

    def delete_requisitions(self, id):
        url = "{}/requisitions/{}".format(base, id)
        print("deleting requisition with id: {}".format(url, id))
        return self.delete(url)

    def create_requisition(self,
                           user_id,
                           redirect="http://localhost:5000/redirect",
                           agreements=[],
                           reference="ref_"+str(calendar.timegm(time.gmtime())),
                           user_language='EN'):
        url = "{}/requisitions/".format(base)
        data = {
            "redirect": "http://localhost:5000/redirect",
            "agreements": agreements,
            "reference": reference,
            "enduser_id": user_id,
            "user_language": user_language
        }
        return self.post(url, data=data).json()

    def show_requisition(self, id):
        url = "{}/requisitions/{}/".format(base, id)
        return self.get(url).json()

    def show_requisition_links(self, requisition_id, bank_id):
        url = "{}/requisitions/{}/links/".format(base, requisition_id)
        data = {
            "aspsp_id": bank_id
        }
        return self.post(url, data=data).json()


#  "https://ob.nordigen.com/api/requisitions/${id}/links/" \

    # agreements

    def list_endusers(self):
        url = "{}/agreements/enduser/".format(base)
        return self.get(url).json()

    def delete_agreement(self, agreement_id):
        url = "{}/agreements/enduser/{}/".format(base, agreement_id)
        print("deleting agreement with id: {}".format(url, agreement_id))
        return self.delete(url)

    def list_agreements(self, user_id):
        url = "{}/agreements/enduser/?enduser_id={}".format(base, user_id)
        return self.get(url).json()

    def create_end_user_agreement(self, bank_id, enduser_id):
        url = "{}/agreements/enduser/".format(base)
        data = {
            "max_historical_days": "90",
            "access_scope": [
                "balances",
                "details",
                "transactions"
            ],
            "enduser_id": enduser_id,
            "aspsp_id": bank_id
        }
        return self.post(url, data=data).json()

    # transactions

    def list_transactions(self, id):
        url = "{}/accounts/{}/transactions/".format(base, id)
        return self.get(url).json()

    # accounts

    def show_balance(self, id):
        url = "{}/accounts/{}/balances/".format(base, id)
        return self.get(url)

    def show_account_detail(self, id):
        url = "{}/accounts/{}/details/".format(base, id)
        return self.get(url)
