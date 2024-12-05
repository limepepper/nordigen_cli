from pydantic import BaseModel


class JWTConfig(BaseModel):
    """JWT Configuration Settings"""

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 300
    ISSUER: str = "nordigen-api"
    AUDIENCE: str = "nordigen-clients"
