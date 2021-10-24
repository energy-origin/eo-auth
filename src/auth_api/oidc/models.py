from typing import Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

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

    # @classmethod
    # def create(cls, **kwargs) -> 'AuthState':
    #     """
    #     Creates a new instance of AuthState.
    #     """
    #     return cls(created=datetime.now(tz=timezone.utc), **kwargs)


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
