from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: str = Field(..., primary_key=True)
    description: str = ""
    key: str | None = None
    disabled: bool | None = None


class UserInDB(BaseModel):
    id: str
    description: str = ""
    key: str | None = None
    disabled: bool | None = None
    hashed_password: str


class UnknownUserError(Exception):
    user: str

    def __init__(self, user: str):
        self.user = user
        super().__init__(f"User {user} not found")


class IncorrectAccessCredentialsError(Exception):
    user: str

    def __init__(self, user: str):
        self.user = user
        super().__init__(f"User {user} password is incorrect")


class UserDisabledError(Exception):
    user: str

    def __init__(self, user: str):
        self.user = user
        super().__init__(f"User {user} is disabled")
