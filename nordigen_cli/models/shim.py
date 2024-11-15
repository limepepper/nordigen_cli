from pydantic import BaseModel
from typing import List, Optional

from nordigen_cli.models.model import BankTransaction

class BankTransactionResponse(BaseModel):
    transactions: BankTransaction
