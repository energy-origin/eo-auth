from abc import abstractmethod
from uuid import uuid4
from typing import Optional, List, Any
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
)

from ..oidc import oidc, OpenIDConnectToken


# -- State -------------------------------------------------------------------


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
    redirect_uri: str


# # -- Encoders ----------------------------------------------------------------
#
#
# state_encoder = TokenEncoder(
#     schema=AuthState,
#     secret=INTERNAL_TOKEN_SECRET,
# )
#
# internal_token_encoder = TokenEncoder(
#     schema=InternalToken,
#     secret=INTERNAL_TOKEN_SECRET,
# )


# -- Helpers -----------------------------------------------------------------


class OpenIdConnectEndpoint(Endpoint):
    """
    Returns a login URL which initiates a login flow @ the
    OpenID Connect Identity Provider.
    """

    state_encoder = TokenEncoder(
        schema=AuthState,
        secret=INTERNAL_TOKEN_SECRET,
    )

    internal_token_encoder = TokenEncoder(
        schema=InternalToken,
        secret=INTERNAL_TOKEN_SECRET,
    )

    def encode_state(self, state: AuthState) -> str:
        """
        TODO
        """
        return self.state_encoder.encode(obj=state)

    def decode_state(self, state_encoded: str) -> AuthState:
        """
        TODO
        """
        return self.state_encoder.decode(state_encoded)

    def build_auth_url(
            self,
            callback_uri: str,
            redirect_uri: str,
            validate_cpr: bool,
    ) -> str:
        """
        TODO
        """
        if validate_cpr:
            scope = ('openid', 'mitid', 'nemid', 'ssn', 'userinfo_token')
        else:
            scope = ('openid', 'mitid', 'nemid')

        state = AuthState(
            created=datetime.now(tz=timezone.utc),
            redirect_uri=redirect_uri,
        )

        state_encoded = self.encode_state(state)

        return oidc.create_authorization_url(
            state=state_encoded,
            scope=scope,
        )

    def redirect_to_auth(self, **kwargs: Any) -> TemporaryRedirect:
        """
        TODO
        """
        return TemporaryRedirect(
            url=self.build_auth_url(**kwargs),
        )


# def build_auth_url(redirect_uri: str) -> str:
#     """
#     TODO
#     """
#     state = AuthState(
#         created=datetime.now(tz=timezone.utc),
#         redirect_uri=redirect_uri,
#     )
#
#     state_encoded = state_encoder.encode(obj=state)
#
#     url, _ = oidc.create_authorization_url(state=state_encoded)
#
#     return url


# -- Login Endpoints ---------------------------------------------------------


class OpenIdLogin(OpenIdConnectEndpoint):
    """
    Returns a login URL which initiates a login flow @ the
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
        url = self.build_auth_url(
            redirect_uri=request.redirect_uri,
            validate_cpr=False,
        )

        return self.Response(url=url)


class OpenIdLoginRedirect(OpenIdConnectEndpoint):
    """
    Redirects client to login URL which initiates a login flow @ the
    OpenID Connect Identity Provider.
    """

    @dataclass
    class Request:
        redirect_uri: str

    def handle_request(self, request: Request) -> TemporaryRedirect:
        """
        Handle HTTP request.
        """
        # return self.redirect_to_auth(
        #     redirect_uri=request.redirect_uri,
        #     validate_cpr=False,
        # )
        url = self.build_auth_url(
            redirect_uri=request.redirect_uri,
            validate_cpr=False,
        )

        return TemporaryRedirect(url=url)


class OpenIdLoginCallback(OpenIdConnectEndpoint):
    """
    Callback: Client is redirected to this endpoint from Identity Provider
    after completing authentication flow.

    TODO Cookie: HttpOnly, Secure, SameSite
    TODO Cookie SKAL have timeout
    """

    @dataclass
    class Request:
        state: Optional[str] = field(default=None)
        iss: Optional[str] = field(default=None)
        code: Optional[str] = field(default=None)
        scope: Optional[str] = field(default=None)
        error: Optional[str] = field(default=None)
        error_hint: Optional[str] = field(default=None)
        error_description: Optional[str] = field(default=None)

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
        """
        Handle request.

        TODO Handle errors from Identity Provider...
        """

        success = not any((
            request.error,
            request.error_hint,
            request.error_description,
        ))

        if not success:
            # Client failed to login via OpenID Connect
            return self._handle_failed_login(
                redirect_uri=state_decoded.redirect_uri,
            )

        try:
            state_decoded = self.decode_state(request.state)
        except self.state_encoder.DecodeError:
            # TODO Handle...
            raise BadRequest()

        # TODO Handle if this fails:
        oidc_token = oidc.fetch_token(
            code=request.code,
            state=request.state,
        )

        user = UserQuery(session) \
            .has_external_subject(oidc_token.subject) \
            .one_or_none()

        if user is None and not oidc_token.userinfo_token:
            # User is unknown to the system, and CPR is unavailable (no userinfo_token).
            # Redirect client to Identity Provider to initiate CPR validation flow.
            return TemporaryRedirect(
                url=self.build_auth_url(
                    redirect_uri=state_decoded.redirect_uri,
                    validate_cpr=True,
                )
            )
        elif user is None:
            # User is unknown to the system, but CPR is available (via userinfo_token).
            # Create user in database
            user = DbUser(
                internal_subject=str(uuid4()),
                external_subject=oidc_token.subject,
                cpr=oidc_token.userinfo_token.cpr,
                created=datetime.now(tz=timezone.utc),
            )

            session.add(user)

        return self._handle_successful_login(
            # request=request,
            session=session,
            state=state_decoded,
            oidc_token=oidc_token,
            subject=user.internal_subject,
        )

        # if success:
        #     return self._handle_successful_login(
        #         request=request,
        #         session=session,
        #         state=state_decoded,
        #     )
        # else:
        #     return self._handle_failed_login(
        #         state=state_decoded,
        #     )

    def _handle_successful_login(
            self,
            # request: Request,
            session: db.Session,
            state: AuthState,
            oidc_token: OpenIDConnectToken,
            subject: str,
    ) -> TemporaryRedirect:
        """
        TODO
        """

        # -- OIDC ------------------------------------------------------------

        # # TODO Handle if this fails:
        #
        # oidc_token = oidc.fetch_token(
        #     code=request.code,
        #     state=request.state,
        # )
        #
        # print(oidc_token)

        # -- User ------------------------------------------------------------

        self._register_user_login(
            session=session,
            subject=subject,
        )

        # -- Token -----------------------------------------------------------

        opaque_token = self._create_token(
            session=session,
            issued=oidc_token.id_token.issued,
            expires=oidc_token.id_token.expires,
            subject=subject,
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
            url=state.redirect_uri,
            query_extra={'success': '1'},
        )

        return TemporaryRedirect(
            url=actual_redirect_url,
            cookies=(cookie,),
        )

    def _handle_failed_login(self, redirect_uri: str) -> TemporaryRedirect:
        """
        TODO
        """
        actual_redirect_url = append_query_parameters(
            url=redirect_uri,
            query_extra={'success': '0'},
        )

        return TemporaryRedirect(
            url=actual_redirect_url,
        )

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

        internal_token_encoded = self.internal_token_encoder \
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

    def _register_user_login(self, session: db.Session, subject: str):
        """
        TODO
        """
        session.add(DbLoginRecord(
            subject=subject,
            created=datetime.now(tz=timezone.utc),
        ))


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

    @dataclass
    class Request:
        state: Optional[str] = field(default=None)
        iss: Optional[str] = field(default=None)
        code: Optional[str] = field(default=None)
        scope: Optional[str] = field(default=None)
        error: Optional[str] = field(default=None)
        error_hint: Optional[str] = field(default=None)
        error_description: Optional[str] = field(default=None)

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


###############################################################


class OpenIdCallbackEndpoint(OpenIdConnectEndpoint):
    """
    An abstract callback endpoint for handling when a client is returned
    from the Identity Provider after either completing or interrupting
    an OpenID Connect authorization flow.

    Inherited classes must implement methods on_oidc_flow_failed()
    and on_oidc_flow_succeeded(), which are invoked depending on the
    result of the flow.
    """

    @dataclass
    class Request:
        state: str
        iss: Optional[str] = field(default=None)
        code: Optional[str] = field(default=None)
        scope: Optional[str] = field(default=None)
        error: Optional[str] = field(default=None)
        error_hint: Optional[str] = field(default=None)
        error_description: Optional[str] = field(default=None)

    def handle_request(self, request: Request) -> Any:
        """
        Handle request.

        TODO Handle errors from Identity Provider...
        """
        try:
            state_decoded = self.decode_state(request.state)
        except self.state_encoder.DecodeError:
            # TODO Handle...
            raise BadRequest()

        failed = any((
            request.error,
            request.error_hint,
            request.error_description,
        ))

        if failed:
            # OpenID Connect flow failed
            return self.on_oidc_flow_failed(state_decoded)

        # TODO Handle if this fails:
        oidc_token = oidc.fetch_token(
            code=request.code,
            state=request.state,
        )

        return self.on_oidc_flow_succeeded(
            state=state_decoded,
            token=oidc_token,
        )

    @abstractmethod
    def on_oidc_flow_failed(
            self,
            state: AuthState,
    ) -> Any:
        """
        Invoked when OpenID Connect flow fails, and the user was
        returned to the callback endpoint.

        :param state: State object
        :returns: Http response
        """
        raise NotImplementedError

    @abstractmethod
    def on_oidc_flow_succeeded(
            self,
            state: AuthState,
            token: OpenIDConnectToken,
    ) -> Any:
        """
        Invoked when OpenID Connect flow succeeds, and the user was
        returned to the callback endpoint.

        # :param session: Database session
        :param state: State object
        :param token: OpenID Connect token fetched from Identity Provider
        :returns: Http response
        """
        raise NotImplementedError

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

        internal_token_encoded = self.internal_token_encoder \
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

    def _successful_redirect(
            self,
            state: AuthState,
            opaque_token: str,
    ) -> TemporaryRedirect:
        """
        TODO
        """
        cookie = Cookie(
            name=TOKEN_COOKIE_NAME,
            value=opaque_token,
            domain=TOKEN_COOKIE_DOMAIN,
            http_only=True,
            same_site=True,
            secure=True,
        )

        actual_redirect_url = append_query_parameters(
            url=state.redirect_uri,
            query_extra={'success': '1'},
        )

        return TemporaryRedirect(
            url=actual_redirect_url,
            cookies=(cookie,),
        )


class OpenIdLoginCallback2(OpenIdCallbackEndpoint):
    """
    TODO
    """

    @db.atomic()
    def on_oidc_flow_succeeded(
            self,
            state: AuthState,
            token: OpenIDConnectToken,
            session: db.Session,
    ) -> Any:
        """

        """

        # -- User ------------------------------------------------------------

        # At this point we don't necessarily know the user (login first time).
        # The Identity Provider can provide multiple subjects for the same
        # user depending on the login method (MitID or NemID).

        user = UserQuery(session) \
            .has_external_subject(token.subject) \
            .one_or_none()

        if user is None:
            # User is unknown to the system, and CPR is unavailable (no userinfo_token).
            # Redirect client to Identity Provider to initiate CPR validation flow.
            return TemporaryRedirect(
                url=self.build_auth_url(
                    callback_uri='',  # TODO
                    redirect_uri=state.redirect_uri,
                    validate_cpr=True,
                )
            )

        # if user is None and not token.userinfo_token:
        #     # User is unknown to the system, and CPR is unavailable (no userinfo_token).
        #     # Redirect client to Identity Provider to initiate CPR validation flow.
        #     return TemporaryRedirect(
        #         url=self.build_auth_url(
        #             callback_uri='',  # TODO
        #             redirect_uri=state.redirect_uri,
        #             validate_cpr=True,
        #         )
        #     )
        # elif user is None:
        #     # User is unknown to the system, but CPR is available (via userinfo_token).
        #     # Create user in database
        #     user = DbUser(
        #         internal_subject=str(uuid4()),
        #         external_subject=token.subject,
        #         cpr=token.userinfo_token.cpr,
        #         created=datetime.now(tz=timezone.utc),
        #     )
        #
        #     session.add(user)

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

        return self._successful_redirect(
            state=state,
            opaque_token=opaque_token,
        )

        # cookie = Cookie(
        #     name=TOKEN_COOKIE_NAME,
        #     value=opaque_token,
        #     domain=TOKEN_COOKIE_DOMAIN,
        #     http_only=True,
        #     same_site=True,
        #     secure=True,
        # )
        #
        # actual_redirect_url = append_query_parameters(
        #     url=state.redirect_uri,
        #     query_extra={'success': '1'},
        # )
        #
        # return TemporaryRedirect(
        #     url=actual_redirect_url,
        #     cookies=(cookie,),
        # )


class OpenIdCprValidationCallback(OpenIdCallbackEndpoint):
    """
    TODO
    """

    @db.atomic()
    def on_oidc_flow_succeeded(
            self,
            state: AuthState,
            token: OpenIDConnectToken,
            session: db.Session,
    ) -> Any:
        """

        """
        user = UserQuery(session) \
            .has_external_subject(token.subject) \
            .one_or_none()

        if user is None and not token.userinfo_token:
            # User is unknown to the system, and CPR is unavailable (no userinfo_token).
            # Redirect client to Identity Provider to initiate CPR validation flow.
            return TemporaryRedirect(
                url=self.build_auth_url(
                    redirect_uri=state.redirect_uri,
                    validate_cpr=True,
                )
            )
        elif user is None:
            # User is unknown to the system, but CPR is available (via userinfo_token).
            # Create user in database
            user = DbUser(
                internal_subject=str(uuid4()),
                external_subject=oidc_token.subject,
                cpr=oidc_token.userinfo_token.cpr,
                created=datetime.now(tz=timezone.utc),
            )

            session.add(user)

        return self._handle_successful_login(
            # request=request,
            session=session,
            state=state_decoded,
            oidc_token=oidc_token,
            subject=user.internal_subject,
        )
