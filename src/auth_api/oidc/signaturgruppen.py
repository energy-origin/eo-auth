import requests
from serpyco import field
from authlib.jose import jwt
from dataclasses import dataclass
from typing import Optional, List, Any
from datetime import datetime, timezone
from authlib.integrations.requests_client import \
    OAuth2Session as OAuth2Session_

from energytt_platform.serialize import simple_serializer

from auth_api.config import (
    DEBUG,
    OIDC_CLIENT_ID,
    OIDC_CLIENT_SECRET,
    OIDC_LOGIN_URL,
    OIDC_TOKEN_URL,
    OIDC_JWKS_URL,
    OIDC_LOGOUT_URL,
)


# -- Data models -------------------------------------------------------------


@dataclass
class IdToken:
    """
    OpenID Connect ID token
    """
    amr: Optional[Any] = field(default=None)
    at_hash: Optional[Any] = field(default=None)
    aud: Optional[Any] = field(default=None)
    auth_time: Optional[Any] = field(default=None)
    exp: Optional[int] = field(default=None)
    iat: Optional[int] = field(default=None)
    identity_type: Optional[Any] = field(default=None)
    idp: Optional[Any] = field(default=None)
    iss: Optional[Any] = field(default=None)
    nbf: Optional[Any] = field(default=None)
    neb_sid: Optional[Any] = field(default=None)
    session_expiry: Optional[Any] = field(default=None)
    transaction_id: Optional[Any] = field(default=None)
    sub: Optional[int] = field(default=None)
    acr: Optional[Any] = field(default=None)
    loa: Optional[Any] = field(default=None)
    idp_environment: Optional[Any] = field(default=None)


@dataclass
class UserInfoToken:
    """
    OpenID Connect UserInfo token
    """
    acr: Optional[Any] = field(default=None)
    amr: Optional[Any] = field(default=None)
    aud: Optional[Any] = field(default=None)
    auth_time: Optional[Any] = field(default=None)
    exp: Optional[int] = field(default=None)
    iat: Optional[int] = field(default=None)
    identity_type: Optional[Any] = field(default=None)
    idp: Optional[Any] = field(default=None)
    iss: Optional[Any] = field(default=None)
    loa: Optional[Any] = field(default=None)
    nbf: Optional[Any] = field(default=None)
    sub: Optional[str] = field(default=None)
    transaction_id: Optional[Any] = field(default=None)
    mitid_age: Optional[Any] = field(dict_key='mitid.age', default=None)
    mitid_date_of_birth: Optional[Any] = field(dict_key='mitid.date_of_birth', default=None)
    mitid_identity_name: Optional[Any] = field(dict_key='mitid.identity_name', default=None)
    mitid_uuid: Optional[Any] = field(dict_key='mitid.uuid', default=None)
    cpr: Optional[str] = field(dict_key='dk.cpr', default=None)


@dataclass
class OpenIDConnectToken:
    """
    OpenID Connect ID token
    """
    expires_at: int
    id_token: IdToken
    id_token_raw: str
    userinfo_token: Optional[UserInfoToken] = field(default=None)
    scope: List[str] = field(default_factory=list)
    access_token: Optional[str] = field(default=None)

    @property
    def issued(self) -> Optional[datetime]:
        """
        TODO
        """
        if self.id_token:
            return datetime.fromtimestamp(self.id_token.iat, tz=timezone.utc)

    @property
    def expires(self) -> Optional[datetime]:
        """
        TODO
        """
        if self.id_token:
            return datetime.fromtimestamp(self.id_token.exp, tz=timezone.utc)

    @property
    def subject(self) -> Optional[str]:
        """
        TODO
        """
        if self.id_token:
            return self.id_token.sub

    @property
    def identity_provider(self) -> Optional[str]:
        """
        TODO
        """
        if self.id_token:
            return self.id_token.idp

    @property
    def ssn(self) -> Optional[str]:
        """
        TODO
        """
        if self.userinfo_token:
            return self.userinfo_token.cpr


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


class SignaturgruppenBackend(object):
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
        )

    def create_authorization_url(
            self,
            state: str,
            callback_uri: str,
            validate_ssn: bool,
    ) -> str:
        """
        Creates and returns an absolute URL to initiate an OpenID Connect
        authorization flow at the Identity Provider.

        :param state: An arbitrary string passed to the callback endpoint
        :param callback_uri: URL to callback endpoint to return client to
            after completing or interrupting the flow
        :param validate_ssn: Whether or not to validate social security
            number as part of the flow
        :returns: Absolute URL @ Identity Provider
        """
        if validate_ssn:
            # scope = ('openid', 'mitid', 'nemid', 'ssn', 'userinfo_token')
            scope = ('openid', 'mitid', 'nemid', 'ssn', 'userinfo_token')
            # raise Exception('asd')
        else:
            # scope = ('openid', 'mitid', 'nemid', 'ssn', 'ssn_store', 'userinfo_token')
            scope = ('openid', 'mitid', 'nemid')

        url, _ = self.session.create_authorization_url(
            url=OIDC_LOGIN_URL,
            redirect_uri=callback_uri,
            state=state,
            scope=scope,
        )

        return url

    def create_logout_url(self):
        """
        Returns the url do redirect the user to, to complete the logout.
        :rtype: str
        """

        return OIDC_LOGOUT_URL

    def fetch_token(self, code: str, state: str, redirect_uri: str) -> OpenIDConnectToken:
        """
        TODO
        """
        token_raw = self.session.fetch_token(
            url=OIDC_TOKEN_URL,
            grant_type='authorization_code',
            code=code,
            state=state,
            redirect_uri=redirect_uri,
            verify=not DEBUG,
        )

        # TODO Test these:
        scope = [s for s in token_raw.get('scope', '').split(' ') if s]

        id_token = self.parse_id_token(token_raw['id_token'])

        token = OpenIDConnectToken(
            scope=scope,
            expires_at=token_raw['expires_at'],
            id_token=id_token,
            id_token_raw=token_raw['id_token'],
        )

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
            validate=False,
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
            validate=False,
        )


# -- Singletons --------------------------------------------------------------


oidc = SignaturgruppenBackend()
