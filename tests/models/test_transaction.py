from rich.console import Console

from nordigen_cli.models.model import AccountTransactions, BankTransaction

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

console = Console(force_terminal=True)


class TestTransaction:
    def test_from_json(self):
        transactions = AccountTransactions.model_validate_json(
            example_data
        ).transactions
        assert isinstance(transactions, BankTransaction)
        # pprint(transactions)
        # print(f"{transactions!r}")
        # console.print(transactions)
        # for name, field_repr in transactions.__repr_args__():
        #     console.print(name, field_repr)
        # rprint(transactions)
        # inspect(transactions, all=True)
