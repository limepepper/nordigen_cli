from datetime import datetime

from pydantic import BaseModel, PositiveInt


class ResponseError(BaseModel):
    summary: str
    detail: str
    timestamp: datetime
