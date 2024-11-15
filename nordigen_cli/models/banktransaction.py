from datetime import datetime

from pydantic import BaseModel, PositiveInt

# https://bankaccountdata.gocardless.com/api/v2/swagger.json

class BankTransaction2(BaseModel):
    """A transaction model"""

    id: str
    date: datetime
    amount: float
    currency: str
    description: str
