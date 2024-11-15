from datetime import datetime

from pydantic import BaseModel, Strict
from pydantic import PositiveInt
from typing_extensions import Annotated


class Agreement(BaseModel):
    id: str
    created: datetime
    institution_id: str
    max_historical_days: PositiveInt
    access_valid_for_days: PositiveInt
    access_scope: Annotated[list[str], Strict()]
    accepted: datetime | None
