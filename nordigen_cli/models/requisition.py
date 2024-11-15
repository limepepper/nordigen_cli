from datetime import datetime

from pydantic import BaseModel, PositiveInt


class Requisition(BaseModel):
    id: str
    redirect: str
    status: list[str]
    agreement_id: str
    accounts: list[str]
    reference: str
    user_language: str
    link: str
