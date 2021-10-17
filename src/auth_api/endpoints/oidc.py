from uuid import uuid4
from typing import Optional, List, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field

from energytt_platform.tokens import TokenEncoder
from energytt_platform.serialize import Serializable
from energytt_platform.models.auth import InternalToken
from energytt_platform.tools import append_query_parameters
from energytt_platform.api import \
    Endpoint, Cookie, BadRequest, TemporaryRedirect

from auth_api.db import db
from auth_api.queries import UserQuery
from auth_api.models import DbToken, DbLoginRecord, DbUser
from auth_api.config import (
    INTERNAL_TOKEN_SECRET,
    TOKEN_COOKIE_NAME,
    TOKEN_COOKIE_DOMAIN,
    TOKEN_DEFAULT_SCOPES,
    OIDC_LOGIN_CALLBACK_URL,
    OIDC_SSN_VALIDATE_CALLBACK_URL,
)

from ..oidc import oidc, OpenIDConnectToken


# -- Error codes -------------------------------------------------------------


# Errors from Identity Provider translates into these errors codes
# as an internal abstraction over OpenID Connect errors.

ERROR_CODES = {
    'E0': 'Unknown error from Identity Provider',
    'E1': 'User interrupted',
    'E3': 'User failed to verify SSN',
    'E500': 'Internal Server Error',
    'E501': 'Internal Server Error at Identity Provider',
}

# /callback?error_code=E501&error=Internal Serviver


# -- Models ------------------------------------------------------------------


@dataclass
class AuthState(Serializable):
    """
    AuthState is an intermediate token generated when the user requests
    an authorization URL. It encodes to a [JWT] string.

    The token is included in the authorization URL, and is returned by the
    OIDC Identity Provider when the client is redirected back.

    It provides a way to keep this service stateless.
    """
    created: datetime
    return_url: str

    @classmethod
    def create(cls, **kwargs) -> 'AuthState':
        """
        Creates a new instance of AuthState.
        """
        return cls(created=datetime.now(tz=timezone.utc), **kwargs)


@dataclass
class OidcCallbackParams:
    """
    Parameters provided by the Identity Provider when redirecting
    clients back to callback endpoints.

    TODO Describe each field separately
    """
    state: Optional[str] = field(default=None)
    iss: Optional[str] = field(default=None)
    code: Optional[str] = field(default=None)
    scope: Optional[str] = field(default=None)
    error: Optional[str] = field(default=None)
    error_hint: Optional[str] = field(default=None)
    error_description: Optional[str] = field(default=None)


# -- Encoders ----------------------------------------------------------------


state_encoder = TokenEncoder(
    schema=AuthState,
    secret=INTERNAL_TOKEN_SECRET,
)

internal_token_encoder = TokenEncoder(
    schema=InternalToken,
    secret=INTERNAL_TOKEN_SECRET,
)


# -- Login Endpoints ---------------------------------------------------------


class OpenIdLogin(Endpoint):
    """
    Creates a URL which initiates a login flow @ the OpenID Connect
    Identity Provider. If the 'redirect' parameter is provided,
    the endpoint 307 redirects the client, otherwise it returns the
    URL as JSON body.
    """

    @dataclass
    class Request:
        return_url: str
        redirect: Optional[str] = field(default=None)

    @dataclass
    class Response:
        url: Optional[str] = field(default=None)

    def handle_request(
            self,
            request: Request,
    ) -> Union[Response, TemporaryRedirect]:
        """
        Handle HTTP request.
        """
        state = AuthState.create(
            return_url=request.return_url,
        )

        url = oidc.create_authorization_url(
            state=state_encoder.encode(state),
            callback_uri=OIDC_LOGIN_CALLBACK_URL,
            validate_ssn=False,
        )

        if request.redirect:
            return TemporaryRedirect(url=url)
        else:
            return self.Response(url=url)


# -- Login Callback Endpoints ------------------------------------------------


class OpenIDCallbackEndpoint(Endpoint):
    """
    Base-class for OpenID Connect callback endpoints that handles when a
    client is returned from the Identity Provider after either completing
    or interrupting an OpenID Connect authorization flow.

    Inherited classes can implement methods on_oidc_flow_failed()
    and on_oidc_flow_succeeded(), which are invoked depending on the
    result of the flow.
    """

    Request = OidcCallbackParams

    @db.atomic()
    def handle_request(
            self,
            request: Request,
            session: db.Session,
    ) -> Any:
        """
        Handle request.

        TODO Handle errors from Identity Provider...
        """
        try:
            state = state_encoder.decode(request.state)
        except state_encoder.DecodeError:
            # TODO Handle...
            raise BadRequest()

        failed = any((
            request.error,
            request.error_hint,
            request.error_description,
        ))

        if failed:
            # OpenID Connect flow failed
            return self.on_oidc_flow_failed(
                state=state,
                params=request,
            )

        # TODO Handle if this fails:
        token = oidc.fetch_token(
            code=request.code,
            state=request.state,
        )

        # User is unknown when logging in for the first time
        user = UserQuery(session) \
            .has_external_subject(token.subject) \
            .one_or_none()

        return self.on_oidc_flow_succeeded(
            session=session,
            state=state,
            token=token,
            user=user,
        )

    def on_oidc_flow_failed(
            self,
            state: AuthState,
            params: OidcCallbackParams,
    ) -> Any:
        """
        Invoked when OpenID Connect flow fails, and the user was
        returned to the callback endpoint.

        Redirects clients back to return_uri with necessary query parameters.

        :param state: State object
        :param params: Callback parameters from Identity Provider
        :returns: Http response
        """

        query = {
            'success': '0',
        }

        # TODO Add error codes to query

        actual_redirect_url = append_query_parameters(
            url=state.return_url,
            query_extra=query,
        )

        return TemporaryRedirect(
            url=actual_redirect_url,
        )

    def on_oidc_flow_succeeded(
            self,
            session: db.Session,
            state: AuthState,
            token: OpenIDConnectToken,
            user: Optional[DbUser],
    ) -> Any:
        """
        Invoked when OpenID Connect flow succeeds, and the client was
        returned to the callback endpoint.

        :param session: Database session
        :param state: OpenID Connect state object
        :param token: OpenID Connect token fetched from Identity Provider
        :param user: The user who just completed the flow, or None if
            the user is not registered in the system
        :returns: HTTP response
        """

        # -- User ------------------------------------------------------------

        self._register_user_login(
            session=session,
            subject=user.internal_subject,
        )

        # -- Token -----------------------------------------------------------

        opaque_token = self._create_token(
            session=session,
            issued=token.id_token.issued,
            expires=token.id_token.expires,
            subject=user.internal_subject,
            scope=TOKEN_DEFAULT_SCOPES,
        )

        # -- Response --------------------------------------------------------

        cookie = Cookie(
            name=TOKEN_COOKIE_NAME,
            value=opaque_token,
            domain=TOKEN_COOKIE_DOMAIN,
            http_only=True,
            same_site=True,
            secure=True,
        )

        actual_redirect_url = append_query_parameters(
            url=state.return_url,
            query_extra={'success': '1'},
        )

        return TemporaryRedirect(
            url=actual_redirect_url,
            cookies=(cookie,),
        )

    def _register_user_login(
            self,
            session: db.Session,
            user: DbUser,
    ):
        """
        Registers a user's successful login.

        :param session: Database session
        :param user: The user who just logged in successfully
        """
        session.add(DbLoginRecord(
            subject=user.internal_subject,
            created=datetime.now(tz=timezone.utc),
        ))

    def _create_token(
            self,
            session: db.Session,
            issued: datetime,
            expires: datetime,
            subject: str,
            scope: List[str],
    ) -> str:
        """
        TODO
        """
        internal_token = InternalToken(
            issued=issued,
            expires=expires,
            actor=subject,
            subject=subject,
            scope=scope,
        )

        internal_token_encoded = internal_token_encoder \
            .encode(internal_token)

        opaque_token = str(uuid4())

        session.add(DbToken(
            subject=subject,
            opaque_token=opaque_token,
            internal_token=internal_token_encoded,
            issued=issued,
            expires=expires,
        ))

        return opaque_token


class OpenIDLoginCallback(OpenIDCallbackEndpoint):
    """
    Client is redirected to this callback endpoint after completing
    or interrupting an OpenID Connect authorization flow.

    The user may not be known to the system in case its the first time
    they login. In this case, we initiate another OpenID Connect flow,
    but this time requesting social security number. After completing this
    second flow, the user is redirected back to OpenIdSsnCallback-endpoint.
    """

    def on_oidc_flow_succeeded(
            self,
            session: db.Session,
            state: AuthState,
            token: OpenIDConnectToken,
            user: Optional[DbUser],
    ) -> Any:
        """
        Invoked when OpenID Connect flow succeeds, and the client was
        returned to the callback endpoint.

        :param session: Database session
        :param state: OpenID Connect state object
        :param token: OpenID Connect token fetched from Identity Provider
        :param user: The user who just completed the flow, or None if
            the user is not registered in the system
        :returns: HTTP response
        """
        if user is None:
            return TemporaryRedirect(
                url=self._create_validate_ssn_flow_url(state),
            )

        return super(OpenIDLoginCallback, self).on_oidc_flow_succeeded(
            session=session,
            state=state,
            token=token,
            user=user,
        )

    def _create_validate_ssn_flow_url(self, state: AuthState) -> str:
        """
        TODO
        """
        return oidc.create_authorization_url(
            state=state_encoder.encode(state),
            callback_uri=OIDC_LOGIN_CALLBACK_URL,
            validate_ssn=True,
        )


class OpenIDSsnCallback(OpenIDCallbackEndpoint):
    """
    Client is redirected to this callback endpoint after completing
    or interrupting an OpenID Connect SSN verification flow.

    The user may not be known to the system in case its the first time
    they login. In this case, we create the user locally.

    Afterwards, the client is redirected back to it's return_uri.
    """

    def on_oidc_flow_succeeded(
            self,
            session: db.Session,
            state: AuthState,
            token: OpenIDConnectToken,
            user: Optional[DbUser],
    ) -> Any:
        """
        Invoked when OpenID Connect flow succeeds, and the client was
        returned to the callback endpoint.

        :param session: Database session
        :param state: OpenID Connect state object
        :param token: OpenID Connect token fetched from Identity Provider
        :param user: The user who just completed the flow, or None if
            the user is not registered in the system
        :returns: HTTP response
        """
        if user is None:
            user = self._create_user(token)
            session.add(user)

        return super(OpenIDSsnCallback, self).on_oidc_flow_succeeded(
            session=session,
            state=state,
            token=token,
            user=user,
        )

    def _create_user(self, token: OpenIDConnectToken) -> DbUser:
        """
        TODO
        """
        return DbUser(
            internal_subject=str(uuid4()),
            external_subject=token.subject,
            cpr=token.userinfo_token.cpr,
            created=datetime.now(tz=timezone.utc),
        )


# -- Logout Endpoints --------------------------------------------------------


class OpenIdLogout(Endpoint):
    """
    Returns a logout URL which initiates a logout flow @ the
    OpenID Connect Identity Provider.
    """

    @dataclass
    class Request:
        redirect_uri: str

    @dataclass
    class Response:
        url: Optional[str] = field(default=None)

    def handle_request(self, request: Request) -> Response:
        """
        Handle HTTP request.
        """
        return self.Response(
            url=oidc.create_logout_url(),
        )


class OpenIdLogoutRedirect(Endpoint):
    """
    Redirects client to logout URL which initiates a logout flow @ the
    OpenID Connect Identity Provider.
    """

    @dataclass
    class Request:
        redirect_uri: str

    def handle_request(self, request: Request) -> TemporaryRedirect:
        """
        Handle HTTP request.
        """
        return TemporaryRedirect(
            url=oidc.create_logout_url(),
        )


class OpenIdLogoutCallback(Endpoint):
    """
    Callback: Client is redirected to this endpoint from Identity Provider
    after completing authentication flow.

    TODO Cookie: HttpOnly, Secure, SameSite
    TODO Cookie SKAL have timeout
    """

    Request = OidcCallbackParams

    @dataclass
    class Response:
        success: bool
        url: str
        token: Optional[str] = field(default=None)

    @db.atomic()
    def handle_request(
            self,
            request: Request,
            session: db.Session,
    ) -> TemporaryRedirect:
        pass
