from pydantic import BaseModel, Extra


class BaseMixin(BaseModel):
    id: str

    class Config:
        extra = "forbid"
