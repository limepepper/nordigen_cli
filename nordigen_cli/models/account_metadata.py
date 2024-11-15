from datetime import datetime

from pydantic import BaseModel


"""
Account details will be returned in Berlin Group PSD2 format.
"""

class AccountMetadata(BaseModel):
    id: str

    created: datetime
    last_accessed: datetime

    iban: str
    bban: str
    status: str
    institution_id: str
    owner_name: str
