from typing import Optional

from apiclient.authentication_methods import BaseAuthenticationMethod
from apiclient.utils.typing import OptionalStr
from limepepper_utils.jwt.client import JWTValidator

from nordigen_cli.models.token import AccessToken


class RefreshableHeaderAuthentication(BaseAuthenticationMethod):
    def __init__(
        self,
        token: AccessToken = None,
        parameter: str = "Authorization",
        scheme: OptionalStr = "Bearer",
        extra: Optional[dict[str, str]] = None,
    ):
        self._token = token
        self._parameter = parameter
        self._scheme = scheme
        self._extra = extra

    def get_headers(self) -> dict[str, str]:
        if self._scheme:
            headers = {self._parameter: f"{self._scheme} {self.get_token().token}"}
        else:
            headers = {self._parameter: self.get_token().token}
        if self._extra:
            headers.update(self._extra)
        return headers

    def get_token(self) -> AccessToken:
        return self._token

    def set_token(self, token: AccessToken):
        if not token:
            raise ValueError("token is required")
        self._token = token

    def __rich_repr__(self):
        yield "token", self._token
        yield "token_expiration", JWTValidator.expiry(self._token.token)
        yield "payload", JWTValidator.decode(self._token.token)
