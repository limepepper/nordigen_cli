from pydantic import BaseModel

"""
example_data = {
    "access": "string",
    "access_expires": 86400,
    "refresh": "string",
    "refresh_expires": 2592000
}
"""


class Token(BaseModel):
    access: str
    access_expires: int
    refresh: str
    refresh_expires: int
