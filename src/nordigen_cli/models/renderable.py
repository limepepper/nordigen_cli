from typing import Annotated, Optional

from pydantic import Field

from nordigen_cli.models.mixins import ReprAdapter, ReprMgr
from nordigen_cli.models.model import AccountTransactions, TransactionSchema

# @classmethod
# def get_adapter(cls, obj):
#     model_cls = cls.mappings[type(obj)]
#     if isinstance(obj, model_cls):
#         return cls.mappings[model_cls]
#     return None


class ReprTransactionSchema(ReprAdapter):
    """
    A representation of a transaction schema that can be rendered in the CLI.
    """

    valueDateTime: str
    bookingDateTime: str
    transactionId: str
    transactionAmount: str
    transactionCurrency: str
    remittanceInformationUnstructured: str
    creditorName: Annotated[Optional[str], Field(..., alias="creditorName")]

    @classmethod
    def from_model(cls, model: TransactionSchema) -> "ReprTransactionSchema":
        """
        Convert a model to a representation.
        """
        return cls(
            valueDateTime=next(
                (item for item in [model.valueDateTime, model.valueDate] if item),
                None,
            ),
            bookingDateTime=next(
                (item for item in [model.bookingDateTime, model.bookingDate] if item),
                None,
            ),
            transactionId=next(
                (
                    item
                    for item in [
                        model.entryReference,
                        model.transactionId,
                        model.internalTransactionId,
                        model.bankTransactionCode,
                        model.proprietaryBankTransactionCode,
                    ]
                    if item
                ),
                None,
            ),
            transactionAmount=model.transactionAmount.amount,
            transactionCurrency=model.transactionAmount.currency,
            remittanceInformationUnstructured=model.remittanceInformationUnstructured,
            creditorName=model.creditorName,
        )


ReprMgr.register(TransactionSchema, ReprTransactionSchema)


class ReprAccountTransactions(ReprAdapter):
    """
    A representation of a transaction schema that can be rendered in the CLI.
    """

    @classmethod
    def from_model(cls, model: AccountTransactions) -> list["ReprAccountTransactions"]:
        """
        Convert a model to a representation.
        """
        return [
            ReprTransactionSchema.from_model(item) for item in model.transactions.booked
        ]


ReprMgr.register(AccountTransactions, ReprAccountTransactions)
