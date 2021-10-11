import requests
from serpyco import field
from authlib.jose import jwt
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List, Any, Tuple
from authlib.integrations.requests_client import \
    OAuth2Session as OAuth2Session_

from energytt_platform.serialize import simple_serializer

from .config import (
    DEBUG,
    OIDC_CLIENT_ID,
    OIDC_CLIENT_SECRET,
    # OIDC_WANTED_SCOPES,
    OIDC_LOGIN_URL,
    OIDC_TOKEN_URL,
    OIDC_JWKS_URL,
    OIDC_LOGIN_REDIRECT_URL,
    OIDC_LOGOUT_URL,
)


# -- Data models -------------------------------------------------------------


@dataclass
class IdToken:
    """
    OpenID Connect ID token
    """
    acr: Any
    amr: Any
    at_hash: Any
    aud: Any
    auth_time: Any
    exp: int
    iat: int
    identity_type: Any
    idp: Any
    iss: Any
    loa: Any
    nbf: Any
    neb_sid: Any
    session_expiry: Any
    transaction_id: Any
    sub: str

    @property
    def subject(self) -> str:
        """
        TODO
        """
        return self.sub

    @property
    def issued(self) -> datetime:
        """
        TODO
        """
        return datetime.fromtimestamp(self.iat, tz=timezone.utc)

    @property
    def expires(self) -> datetime:
        """
        TODO
        """
        return datetime.fromtimestamp(self.exp, tz=timezone.utc)


@dataclass
class UserInfoToken:
    """
    OpenID Connect UserInfo token
    """
    acr: Any
    amr: Any
    aud: Any
    auth_time: Any
    exp: int
    iat: int
    identity_type: Any
    idp: Any
    iss: Any
    loa: Any
    nbf: Any
    sub: Any
    transaction_id: Any
    mitid_age: Any = field(dict_key='mitid.age')
    mitid_date_of_birth: Any = field(dict_key='mitid.date_of_birth')
    mitid_identity_name: Any = field(dict_key='mitid.identity_name')
    mitid_uuid: Any = field(dict_key='mitid.uuid')
    cpr: str = field(dict_key='dk.cpr')

    @property
    def subject(self) -> str:
        """
        TODO
        """
        return self.sub

    @property
    def issued(self) -> datetime:
        """
        TODO
        """
        return datetime.fromtimestamp(self.iat, tz=timezone.utc)

    @property
    def expires(self) -> datetime:
        """
        TODO
        """
        return datetime.fromtimestamp(self.exp, tz=timezone.utc)


@dataclass
class OpenIDConnectToken:
    """
    OpenID Connect ID token
    """
    expires_at: int
    id_token: IdToken
    userinfo_token: Optional[UserInfoToken] = field(default=None)
    scope: List[str] = field(default_factory=list)
    access_token: Optional[str] = field(default=None)

    @property
    def expires(self) -> datetime:
        """
        TODO
        """
        return datetime.fromtimestamp(self.expires_at, tz=timezone.utc)

    @property
    def subject(self) -> Optional[str]:
        """
        TODO
        """
        if self.id_token:
            return self.id_token.subject


# -- OpenID Connect ----------------------------------------------------------


class OAuth2Session(OAuth2Session_):
    """
    Abstracting low-level OAuth2 actions to simplify testing.
    """
    def get_jwk(self) -> str:
        """
        TODO Cache result in a period
        """
        jwks_response = requests.get(
            url=OIDC_JWKS_URL,
            verify=not DEBUG,
        )

        return jwks_response.content.decode()


class OidcBackend(object):
    """
    TODO
    """

    def __init__(self):
        """
        TODO
        """
        self.session = OAuth2Session(
            client_id=OIDC_CLIENT_ID,
            client_secret=OIDC_CLIENT_SECRET,
            # scope=OIDC_WANTED_SCOPES,
        )

    def create_authorization_url(self, state: str, scope: Tuple[str, ...]) -> str:
        """
        :rtype: (str, str)
        :returns: Tuple of (login_url, state)
        """
        url, _ = self.session.create_authorization_url(
            url=OIDC_LOGIN_URL,
            state=state,
            redirect_uri=OIDC_LOGIN_REDIRECT_URL,
            scope=scope,
        )

        return url

    def create_logout_url(self):
        """
        Returns the url do redirect the user to, to complete the logout.
        :rtype: str
        """

        return OIDC_LOGOUT_URL

    def fetch_token(self, code: str, state: str) -> OpenIDConnectToken:
        """
        TODO
        """
        token_raw = self.session.fetch_token(
            url=OIDC_TOKEN_URL,
            grant_type='authorization_code',
            code=code,
            state=state,
            redirect_uri=OIDC_LOGIN_REDIRECT_URL,
            verify=not DEBUG,
        )

        # TODO Test these:
        scope = [s for s in token_raw.get('scope', '').split(' ') if s]

        token = OpenIDConnectToken(
            scope=scope,
            expires_at=token_raw['expires_at'],
            id_token=self.parse_id_token(token_raw['id_token']),
        )

        # if token_raw.get('id_token'):
        #     # Parse ID Token
        #     token.id_token = \
        #         self.parse_id_token(token_raw['id_token'])

        if token_raw.get('userinfo_token'):
            # Parse UserInfo Token
            token.userinfo_token = \
                self.parse_userinfo_token(token_raw['userinfo_token'])

        return token

    def parse_id_token(self, id_token: str) -> IdToken:
        """
        TODO
        """
        raw_token = jwt.decode(
            s=id_token,
            key=self.session.get_jwk(),
        )

        return simple_serializer.deserialize(
            schema=IdToken,
            data=dict(raw_token),
        )

    def parse_userinfo_token(self, userinfo_token: str) -> UserInfoToken:
        """
        TODO
        """
        raw_token = jwt.decode(
            s=userinfo_token,
            key=self.session.get_jwk(),
        )

        return simple_serializer.deserialize(
            schema=UserInfoToken,
            data=dict(raw_token),
        )


# -- Singletons --------------------------------------------------------------


oidc = OidcBackend()
