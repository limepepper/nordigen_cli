
import json


class Formatter():

    def pr_account(self):
        pass

    def pr_banks(self, banks, format):

        for bank in banks:
            if(format == "text"):
                print("name: {:35}  id: {}".format(bank['name'], bank['id']))
                # print("")
            elif(format == "json"):
                print(json.dumps(banks, indent=4))

    """
    {
    "bankTransactionCode": "PMNT",
    "bookingDate": "2021-06-28",
    "remittanceInformationUnstructured": "PAYMENT Alderaan Coffe",
    "transactionAmount": {
        "amount": "-15.00",
        "currency": "EUR"
    },
    "transactionId": "2021062802749502-1",
    "valueDate": "2021-06-28"
    }
    """

    def pr_transactions(self, transactions, format):

        if(format == "text"):
            for tx in transactions["transactions"]["booked"]:
                # if(format == "text"):
                print("{}: {:>7} {} : {} {}".format(
                    tx['valueDate'],
                    tx["transactionAmount"]["amount"],
                    tx["transactionAmount"]["currency"],
                    tx['transactionId'],
                    tx["remittanceInformationUnstructured"]
                ))

                    # print("remit infos: \"{}\"".format(
                    # )
                #     # print("")
                # elif(format == "json"):
        elif(format == "json"):
            print(json.dumps(transactions["transactions"], indent=4))


formatter = Formatter()
