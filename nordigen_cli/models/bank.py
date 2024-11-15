from datetime import datetime

from pydantic import BaseModel, PositiveInt


class Bank(BaseModel):
    """a bank """

    id: str
    name: str
    bic: str
    transaction_total_days: PositiveInt
    countries: list[str]
    logo: str
    max_access_valid_for_days: PositiveInt
