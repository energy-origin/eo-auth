from serpyco import field
from dataclasses import dataclass
from typing import Optional, Any, List
from datetime import datetime, timezone

from energytt_platform.serialize import Serializable


@dataclass
class AuthState(Serializable):
    """
    AuthState is an intermediate token generated when the user requests
    an authorization URL. It encodes to a [JWT] string.

    The token is included in the authorization URL, and is returned by the
    OIDC Identity Provider when the client is redirected back.

    It provides a way to keep this service stateless.
    """
    return_url: str
    created: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc))


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

    @property
    def is_private(self) -> bool:
        """
        TODO
        """
        return True

    @property
    def is_company(self) -> bool:
        """
        TODO
        """
        return True
