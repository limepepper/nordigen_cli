#
#
#
from enum import Enum, auto

from nordigen_cli.apiclient.errors import TokenFormatError
from nordigen_cli.models.token import AccessToken, RefreshToken


class ClientState(Enum):
    INITIAL = auto()
    """state after initialization"""
    TOKENS_CACHED = auto()
    """initial inspection provided both tokens with valid expiry"""
    NO_TOKENS = auto()
    """no tokens initially provided"""
    ACCESS_TOKEN_ACTIVE = auto()
    """client appears to have a valid access token. will request resources"""
    ACCESS_TOKEN_INVALID = auto()
    """a resource request failed with an invalid access token"""
    TOKEN_REFRESH_REQUEST_FAILED = auto()
    """refresh token request failed"""
    REFRESH_TOKEN_EXPIRED = auto()
    """token has, or is about to expire"""
    TOKEN_PAIR_REQUEST_FAILED = auto()
    """token pair request failed"""


class NordigenClientBaseMixin:
    state: ClientState = ClientState.INITIAL
    r_client: "ResourceClient" = None  # the resource client
    t_client: "TokenClient" = None  # the auth token client

    def set_access_token(self, token: AccessToken):
        if not isinstance(token, AccessToken):
            raise TokenFormatError(
                f"token must be an instance of AccessToken, got {type(token)}"
            )
        self.r_client.get_authentication_method().set_token(token)

    def get_access_token(self) -> AccessToken:
        return self.r_client.get_authentication_method().get_token()

    @property
    def access_token(self) -> AccessToken:
        return self.get_access_token()

    def set_refresh_token(self, token: RefreshToken):
        if not isinstance(token, RefreshToken):
            raise TokenFormatError(
                f"token must be an instance of RefreshToken, got {type(token)}"
            )
        self.t_client.refresh_token = token

    def get_refresh_token(self) -> RefreshToken:
        return self.t_client.refresh_token

    @property
    def refresh_token(self) -> RefreshToken:
        return self.get_refresh_token()

    def set_tokens(self, access_token: AccessToken, refresh_token: RefreshToken):
        self.set_access_token(access_token)
        self.set_refresh_token(refresh_token)
        self.state = ClientState.TOKENS_CACHED
