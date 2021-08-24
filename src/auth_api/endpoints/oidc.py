from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from energytt_platform.api import Endpoint
from energytt_platform.tokens import TokenEncoder
from energytt_platform.serialize import Serializable
from energytt_platform.bus import topics as t, messages as m
from energytt_platform.auth import OpaqueToken, encode_opaque_token

from auth_api.bus import broker
from auth_api.backend import auth_backend
from auth_api.config import SYSTEM_SECRET


# -- State -------------------------------------------------------------------


@dataclass
class AuthState(Serializable):
    redirect_uri: str


auth_state_encoder = TokenEncoder(
    cls_=AuthState,
    secret=SYSTEM_SECRET,
)


# -- Endpoints ---------------------------------------------------------------


class OpenIdAuthenticate(Endpoint):
    """
    Redirects client to Identity Provider.
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
        # TODO Redirect client to identity provider
        # TODO Provide parameters: client_id, response_type, redirect_uri, scope, state, ???
        # TODO Example URL:
        # https://netsbroker.mitid.dk/op/connect/authorize?client_id=<client_id>&response_type=code
        # &redirect_uri=<redirect_uri>&scope=openid mitid
        # ssn&state=<state>&nonce=<nonce>&idp_values=mitid

        state = AuthState(
            redirect_uri=request.redirect_uri,
        )

        url, state = auth_backend.create_authorization_url(
            state=auth_state_encoder.encode(state),
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

    def handle_request(self, request: Request) -> Response:
        """
        Handle HTTP request.
        """
        # TODO Read query parameter "code"
        # TODO Request ID- and Access token from Identity Provide
        # TODO Get subject etc. from ID token

        try:
            state_decoded = auth_state_encoder.decode(request.state)
        except auth_state_encoder.DecodeError:
            # TODO Handle...
            raise

        token = auth_backend.fetch_token(
            code=request.code,
            state=request.state,
        )

        # id_token:
        # iss - Issuer
        # sub - Subject
        # aud - Audience
        # exp - Expiration
        # nbf - Not Before
        # iat - Issued At
        # jti - JWT ID
        id_token = auth_backend.get_id_token(
            token=token,
        )

        subject = id_token['sub']

        opaque_token = OpaqueToken(
            issued=datetime.now(),
            expires=datetime.now() + timedelta(days=30),
            subject=subject,
            scope=request.scope.split(' '),
            on_behalf_of=subject,
        )

        encoded_opaque_token = encode_opaque_token(
            token=opaque_token,
        )

        broker.publish(
            topic=t.AUTH,
            msg=m.UserOnboarded(
                subject=subject,
                name=f'User {subject}',
            ),
        )

        return self.Response(
            success=True,
            url=state_decoded.redirect_uri,
            token=encoded_opaque_token,
        )
