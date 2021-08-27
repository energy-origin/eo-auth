from uuid import uuid4
from typing import Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field

from energytt_platform.api import Endpoint
from energytt_platform.tokens import TokenEncoder
from energytt_platform.serialize import Serializable
from energytt_platform.models.auth import InternalToken
from energytt_platform.bus import topics as t, messages as m

from ..db import db
from ..bus import broker
from ..backend import oidc
from ..models import DbToken
from ..config import TOKEN_SECRET
from ..controller import controller


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


# -- Encoders ----------------------------------------------------------------


state_encoder = TokenEncoder(
    schema=AuthState,
    secret=TOKEN_SECRET,
)

token_encoder = TokenEncoder(
    schema=InternalToken,
    secret=TOKEN_SECRET,
)


# -- Endpoints ---------------------------------------------------------------


class OpenIdAuthenticate(Endpoint):
    """
    TODO
    """

    @dataclass
    class Request:
        redirect_uri: str

    @dataclass
    class Response:
        success: bool
        url: Optional[str] = field(default=None)

    def handle_request(self, request: Request) -> Response:
        """
        Handle HTTP request.
        """
        state = AuthState(
            created=datetime.now(tz=timezone.utc),
            redirect_uri=request.redirect_uri,
        )

        state_encoded = state_encoder.encode(
            obj=state,
        )

        url, _ = oidc.create_authorization_url(
            state=state_encoded,
        )

        return self.Response(
            success=True,
            url=url,
        )


class OpenIdAuthenticateCallback(Endpoint):
    """
    Callback: Client is redirected to this endpoint from Identity Provider
    after completing authentication flow.
    """

    @dataclass
    class Request:
        code: Optional[str] = field(default=None)
        scope: Optional[str] = field(default=None)
        state: Optional[str] = field(default=None)
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
    ) -> Response:
        """
        Handle request.

        TODO Handle errors from Identity Provider...

        :param request:
        :param session:
        :return:
        """

        try:
            state_decoded = state_encoder.decode(request.state)
        except state_encoder.DecodeError:
            # TODO Handle...
            raise

        # -- OIDC ------------------------------------------------------------

        # id_token:
        #     iss - Issuer
        #     sub - Subject
        #     aud - Audience
        #     exp - Expiration
        #     nbf - Not Before
        #     iat - Issued At
        #     jti - JWT ID

        # Fetch token(s)
        token = oidc.fetch_token(code=request.code, state=request.state)
        id_token = oidc.get_id_token(token=token)

        # Token properties
        subject = id_token['sub']
        scope = request.scope.split(' ')
        issued = datetime.now(tz=timezone.utc)
        expires = datetime \
            .fromtimestamp(token['expires_at']) \
            .replace(tzinfo=timezone.utc)

        # -- User ------------------------------------------------------------

        # Get user from database
        user = controller.get_or_create_user(
            session=session,
            subject=subject,
        )

        # New user - first time logging in?
        if not user.has_logged_in:
            broker.publish(
                topic=t.AUTH,
                msg=m.UserOnboarded(subject=subject),
            )

        # Update user last login timestamp
        user.update_last_login()

        # -- Token -----------------------------------------------------------

        opaque_token = self.create_token(
            session=session,
            subject=subject,
            scope=scope,
            issued=issued,
            expires=expires,
        )

        # -- Response --------------------------------------------------------

        return self.Response(
            success=True,
            url=state_decoded.redirect_uri,
            token=opaque_token,
        )

    def create_token(
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
            subject=subject,
            scope=scope,
        )

        internal_token_encoded = token_encoder.encode(
            obj=internal_token,
        )

        # opaque_token = str(uuid4())
        opaque_token = internal_token_encoded

        session.add(DbToken(
            subject=subject,
            opaque_token=opaque_token,
            internal_token=internal_token_encoded,
            issued=issued,
            expires=expires,
        ))

        return opaque_token
