import logging
from datetime import datetime
from typing import Callable, cast

import vcr
from apiclient import (
    APIClient,
    JsonRequestFormatter,
    JsonResponseHandler,
    NoAuthentication,
    endpoint,
)
from limepepper_utils.jwt.client import TokenManager
from loguru import logger

from nordigen_cli.apiclient.authentication import (
    RefreshableHeaderAuthentication,
)
from nordigen_cli.apiclient.endpoints import BaseEndpoints, Endpoints
from nordigen_cli.apiclient.errors import (
    AuthenticationFailedError,
    InvalidTokenError,
    PageNotFoundError,
    ResourceErrorHandler,
    SignonErrorHandler,
    TokenExpiryError,
)
from nordigen_cli.apiclient.mixn import ClientState, NordigenClientBaseMixin
from nordigen_cli.models.model import (
    JWTObtainPairRequest,
    SpectacularJWTObtain,
    SpectacularJWTRefresh,
)
from nordigen_cli.models.token import AccessToken, RefreshToken


def before_record_cb(request):
    # if request and "token" in request.path:
    #     return None
    # return request
    return None


dt = datetime.now().strftime("%Y-%m-%dT%H")

logging.basicConfig()
vcr_log = logging.getLogger("vcr")
vcr_log.setLevel(logging.WARNING)

my_vcr = vcr.VCR(
    serializer="json",
    cassette_library_dir=f"fixtures/cassettes/{dt}",
    record_mode="all",
    # match_on=["uri", "method"],
    before_record_request=before_record_cb,
)


class NordigenClientBase(NordigenClientBaseMixin):
    # callables for injecting and receiving cached tokens
    signon_callback: Callable = None
    refresh_callback: Callable = None
    retrieve_callback: Callable = None
    endpoints: type[BaseEndpoints] = Endpoints
    do_init: bool = True
    base_url: str = ""

    def __init__(self, *, id=None, key=None, api=None, **kwargs):
        logger.trace(f"initializing NordigenClient with kwargs: {kwargs}")
        self.do_init = kwargs.pop("do_init", self.do_init)
        self.signon_callback = kwargs.pop("signon_callback", self.signon_callback)
        self.retrieve_callback = kwargs.pop("retrieve_callback", self.retrieve_callback)
        self.refresh_callback = kwargs.pop("refresh_callback", self.refresh_callback)

        if self.do_init:
            self._post_init(id, key, api, **kwargs)

    def _post_init(
        self,
        secret_id,
        secret_key,
        api,
        **kwargs,
    ):
        self.base_url = api

        if api and not kwargs.get("endpoints"):

            @endpoint(base_url=api)
            class NewEndpoints(BaseEndpoints):
                pass

            self.endpoints = NewEndpoints
        else:
            self.endpoints = kwargs.get("endpoints", self.endpoints)

        self.t_client = TokenClient(
            secret_id=secret_id,
            secret_key=secret_key,
            endpoints=self.endpoints,
        )
        self.r_client = ResourceClient(
            api=api,
            endpoints=self.endpoints,
        )
        self.state = ClientState.NO_TOKENS

        if self.retrieve_callback:
            self.retrieve_callback(self)

    def do_signon(self, method, url, depth: int = 0, **kwargs):
        try:
            self.do_signon_request()
            return self.prerequest(method, url, depth, **kwargs)
        except AuthenticationFailedError as error:
            self.state = ClientState.TOKEN_PAIR_REQUEST_FAILED
            raise error

    def do_signon_request(self, **kwargs):
        access_token, refresh_token = self.t_client.get_tokens(**kwargs)
        self.set_access_token(access_token)
        self.set_refresh_token(refresh_token)
        self.state = ClientState.ACCESS_TOKEN_ACTIVE
        if self.signon_callback:
            self.signon_callback(self)
        return access_token

    def do_refresh(self, method: str, endpoint: str, depth: int = 0, /, **kwargs):
        # if self.state == ClientState.TOKEN_ACTIVE:
        logger.debug("refreshing token")
        try:
            self.do_token_refresh(**kwargs)
            return self.prerequest(method, endpoint, depth, **kwargs)
        except AuthenticationFailedError:
            self.state = ClientState.TOKEN_REFRESH_REQUEST_FAILED
            return self.prerequest(method, endpoint, depth, **kwargs)
        except TokenExpiryError:
            self.state = ClientState.REFRESH_TOKEN_EXPIRED
            return self.prerequest(method, endpoint, depth, **kwargs)

    def do_token_refresh(self, **params):
        self.should_signon()
        access_token = self.t_client.do_post_token_refresh(**params)
        self.set_access_token(access_token)
        self.state = ClientState.ACCESS_TOKEN_ACTIVE
        if self.refresh_callback:
            self.refresh_callback(self)
        return access_token

    def get(self, url: str, params: dict = None, **kwargs):
        return self.prerequest("GET", url, params=params, **kwargs)

    def post(self, url: str, data: dict, params: dict = None, **kwargs):
        return self.prerequest("POST", url, data=data, params=params, **kwargs)

    def delete(self, url: str, params: dict = None, **kwargs):
        return self.prerequest("DELETE", url, params=params, **kwargs)

    def put(self, url: str, data: dict, params: dict = None, **kwargs):
        return self.prerequest("PUT", url, data=data, params=params, **kwargs)

    def prerequest(self, method: str, url: str, depth: int = 0, /, **kwargs):
        """Handle request based on the current state of the client.

        deferring to the appropriate method
        The client has states that can be recovered from such as refreshing or before any tokens have been obtained.
        """
        logger.trace(
            "handling pre-request at depth {depth} {method} {url}",
            depth=depth,
            method=method,
            url=url,
        )
        if depth > 3:
            raise ValueError(
                f"too many recursive calls - depth {depth} args: {kwargs} method: {method} url: {url}"
            )
        if self.state == ClientState.ACCESS_TOKEN_INVALID:
            return self.do_refresh(method, url, depth + 1, **kwargs)
        elif self.state in {
            ClientState.NO_TOKENS,
            ClientState.TOKEN_REFRESH_REQUEST_FAILED,
            ClientState.REFRESH_TOKEN_EXPIRED,
        }:
            return self.do_signon(method, url, depth + 1, **kwargs)
        elif self.state in {
            ClientState.ACCESS_TOKEN_ACTIVE,
            ClientState.TOKENS_CACHED,
        }:
            return self.request(method, url, depth + 1, **kwargs)
        else:
            raise ValueError(
                
                    f"state '{self.state}' not supported. "
                    "This usually happens when something caught an exception "
                    "but didn't reset the token state and re-tried the request "
                    "with the same arguments."
                
            )

    def request(self, method: str, endpoint: str, depth: int, /, **kwargs):
        """represents a request to a protected resource"""
        with my_vcr.use_cassette("test.json"):
            try:
                return self._request(method, endpoint, depth, **kwargs)
            except (InvalidTokenError, TokenExpiryError):
                self.state = ClientState.ACCESS_TOKEN_INVALID
                return self.prerequest(method, endpoint, depth, **kwargs)
            except PageNotFoundError as error:
                logger.warning("page not found: %s", error)
                raise error
            except Exception as error:
                logger.warning("error was not handled by client: %s", error)
                raise error

    def _request(self, method: str, endpoint: str, depth: int, /, **kwargs):
        self.should_refresh()
        if method == "GET":
            response = self.r_client.get(endpoint, **kwargs)
        elif method == "POST":
            response = self.r_client.post(endpoint, **kwargs)
        elif method == "PUT":
            response = self.r_client.put(endpoint, **kwargs)
        elif method == "DELETE":
            response = self.r_client.delete(endpoint, **kwargs)
        else:
            raise ValueError(f"method '{method}' not supported")
        return response

    def should_refresh(self) -> bool:
        """avoid API calls if we know access token is expired"""
        if self.access_token.should_refresh():
            logger.debug(
                "access token should be refreshed - {expires_at}",
                expires_at=self.access_token.expires_at,
            )
            raise TokenExpiryError(
                f"access token expired or expiring - {self.access_token.expires_at}"
            )
        return False

    def should_signon(self):
        """avoid API calls if we know refresh token is expired"""
        if not self.get_refresh_token():
            raise TokenExpiryError("token could not be loaded")
        if self.get_refresh_token().should_refresh():
            logger.debug("refresh token should be refreshed")
            raise TokenExpiryError("refresh token expired or expiring")
        return False


# @serialize_all_methods
class TokenClient(APIClient):
    secret_id: str = None
    secret_key: str = None
    endpoints: type[BaseEndpoints] = Endpoints
    refresh_token: RefreshToken = None

    def __init__(self, **kwargs):
        logger.trace(f"initializing TokenClient with kwargs: {kwargs}")
        self.secret_id = kwargs.pop("secret_id", self.secret_id)
        self.secret_key = kwargs.pop("secret_key", self.secret_key)
        self.endpoints = kwargs.pop("endpoints", self.endpoints)
        super().__init__(
            authentication_method=NoAuthentication(),
            response_handler=JsonResponseHandler,
            error_handler=SignonErrorHandler,
            request_formatter=JsonRequestFormatter,
            **kwargs,
        )

    # @TODO this should be a do_ method?
    def get_tokens(self, *args, **kwargs) -> tuple[AccessToken, RefreshToken]:
        logger.trace("getting tokens (access+refresh)")
        try:
            spec_jwt_obtain = self.do_get_token_new(*args, **kwargs)
            access_token = AccessToken(
                token=spec_jwt_obtain.access,
                expires_str=spec_jwt_obtain.access_expires,
            )
            refresh_token = RefreshToken(
                token=spec_jwt_obtain.refresh,
                expires_str=spec_jwt_obtain.refresh_expires,
            )
            return access_token, refresh_token
        except Exception as error:
            # can't proceed if we can't get a token
            raise error

    def do_get_token_new(self, *args, **params) -> SpectacularJWTObtain:
        data = JWTObtainPairRequest(
            secret_id=self.secret_id,
            secret_key=self.secret_key,
        )
        response = self.post(
            self.endpoints.token_new,
            data=data.model_dump(),
            params=params,
        )
        logger.trace(f"got new token: {response}")
        return SpectacularJWTObtain.model_validate(response)

    def do_post_token_refresh(self, **params) -> AccessToken:
        data = {
            "refresh": self.refresh_token.token,
        }
        spec_jwt_refresh = SpectacularJWTRefresh.model_validate(
            self.post(
                self.endpoints.token_refresh,
                data=data,
                params=params,
            )
        )
        access_token = AccessToken(
            token=spec_jwt_refresh.access,
            expires_str=spec_jwt_refresh.access_expires,
        )
        AccessToken.model_validate(access_token)
        return access_token


class ResourceClient(APIClient):
    """Nordigen API client implementing Oauth2
    implement oauth2 token refresh flow states"""

    base_url: str = ""
    endpoints: type[Endpoints] = Endpoints
    _do_init: bool = False
    _do_init_endpoints: bool = True

    def get_access_token(self) -> AccessToken:
        return self.get_authentication_method().get_token()

    @property
    def access_token(self) -> AccessToken:
        return self.get_authentication_method().get_token()

    def get_authentication_method(self) -> RefreshableHeaderAuthentication:
        return cast(RefreshableHeaderAuthentication, self._authentication_method)

    def __init__(self, **kwargs):
        logger.trace(f"initializing Resource client with kwargs: {kwargs}")
        self.base_url = kwargs.pop("api", self.base_url)
        self.endpoints = kwargs.pop("endpoints", self.endpoints)
        super().__init__(
            authentication_method=RefreshableHeaderAuthentication(),
            response_handler=JsonResponseHandler,
            error_handler=ResourceErrorHandler,
            request_formatter=JsonRequestFormatter,
            **kwargs,
        )

    def get_request_timeout(self):
        return 30

    def is_valid_token(self) -> bool:
        if not self.get_authentication_method().get_token():
            raise ValueError("access token not found")
        if not TokenManager().is_token_expired(
            self.get_authentication_method().get_token().token
        ):
            raise ValueError("access token is expired")
        return True
