import jwt
from typing import Optional
from urllib.parse import urlencode
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from energytt_platform.auth import OpaqueToken
from energytt_platform.serialize import json_serializer
from energytt_platform.api import Endpoint, Unauthorized

from auth_api.token import (
    CallbackToken,
    encode_auth_token,
    decode_auth_token,
)

from auth_api.config import (
    OIDC_CLIENT_ID,
    OIDC_PROVIDER_URL,
    OIDC_LOGIN_REDIRECT_ENDPOINT,
    SYSTEM_SECRET,
)


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

        callback_token = self.create_callback_token(
            redirect_uri=request.redirect_uri,
        )

        callback_url = '%s?%s' % (
            OIDC_LOGIN_REDIRECT_ENDPOINT,
            callback_token,
        )

        query = {
            'client_id': OIDC_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': callback_url,
            'scope': ' '.join(('openid', 'mitid', 'ssn')),
            'state': '',
            'nonce': '',
            'idp_values': 'mitid',
        }

        redirect_uri = '%s?%s' % (
            OIDC_PROVIDER_URL,
            urlencode(query),
        )

        return self.Response(
            success=True,
            url=redirect_uri,
        )

    def create_callback_token(self, **kwargs) -> str:
        """
        Creates an encoded AuthToken.
        """
        return encode_auth_token(CallbackToken(**kwargs))


class OpenIdAuthenticateCallback(Endpoint):
    """
    Callback: Client is redirected to this endpoint from Identity Provider
    after completing authentication flow.
    """

    @dataclass
    class Request:
        token: str
        scope: Optional[str] = field(default=None)
        code: Optional[str] = field(default=None)
        state: Optional[str] = field(default=None)
        error: Optional[str] = field(default=None)
        error_hint: Optional[str] = field(default=None)
        error_description: Optional[str] = field(default=None)

    @dataclass
    class Response:
        success: bool
        token: Optional[str] = field(default=None)

    def handle_request(self, request: Request) -> Response:
        """
        Handle HTTP request.
        """

        callback_token = self.parse_callback_token(request.token)

        # TODO Read query parameter "code"
        # TODO Request ID- and Access token from Identity Provide
        # TODO Get subject etc. from ID token

        subject = ''

        return self.Response(
            success=True,
            token=self.create_opaque_token(subject),
        )

    def parse_callback_token(self, encoded_jwt: str) -> CallbackToken:
        """
        Parses AuthToken
        """
        return decode_auth_token(encoded_jwt)

    def get_tokens(self):
        """
        Fetches ID- and Access token from Identity Provider.
        """
        pass

    def create_opaque_token(self, subject: str) -> str:
        """
        TODO
        """
        token = OpaqueToken(
            subject=subject,
            on_behalf_of=subject,
            issued=datetime.now(),
            expires=datetime.now() + timedelta(days=30),
        )

        return jwt.encode(
            payload=json_serializer.serialize(token),
            key=SYSTEM_SECRET,
            algorithm='HS256',
        )
