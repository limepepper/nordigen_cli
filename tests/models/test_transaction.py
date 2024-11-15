from rich import inspect

from nordigen_cli.models.model import BankTransaction
from nordigen_cli.models.shim import BankTransactionResponse

example_data = """
{
  "transactions": {
    "booked": [
      {
        "transactionId": "string",
        "debtorName": "string",
        "debtorAccount": {
          "iban": "string"
        },
        "transactionAmount": {
          "currency": "string",
          "amount": "328.18"
        },
        "bankTransactionCode": "string",
        "bookingDate": "date",
        "valueDate": "date",
        "remittanceInformationUnstructured": "string"
      },
      {
        "transactionId": "string",
        "transactionAmount": {
          "currency": "string",
          "amount": "947.26"
        },
        "bankTransactionCode": "string",
        "bookingDate": "date",
        "valueDate": "date",
        "remittanceInformationUnstructured": "string"
      }
    ],
    "pending": [
      {
        "transactionAmount": {
          "currency": "string",
          "amount": "99.20"
        },
        "valueDate": "date",
        "remittanceInformationUnstructured": "string"
      }
    ]
  }
}
"""
from rich.console import Console
from rich import print as rprint

console = Console(force_terminal=True)
from rich.pretty import pprint


class TestTransaction:

    def test_from_json(self):
        transactions = BankTransactionResponse.model_validate_json(
            example_data
        ).transactions
        pprint(transactions)
        console.print(transactions)
        # rprint(transactions)
        # inspect(transactions, all=True)
