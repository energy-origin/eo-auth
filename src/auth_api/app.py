from energytt_platform.api import Application

from .config import TOKEN_SECRET
from .endpoints import (
    ForwardAuth,
    OpenIdAuthenticate,
    OpenIdAuthenticateCallback,
    GrantMeteringPointDelegate,
    RevokeMeteringPointDelegate,
)


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """
    return Application.create(
        name='Auth API',
        secret=TOKEN_SECRET,
        health_check_path='/health',
        endpoints=(
            ('GET', '/auth', ForwardAuth()),
            ('GET', '/oidc/auth', OpenIdAuthenticate()),
            ('GET', '/oidc/callback', OpenIdAuthenticateCallback()),

            ('POST', '/delegates/meteringpoints/grant',
                GrantMeteringPointDelegate()),

            ('POST', '/delegates/meteringpoints/revoke',
                RevokeMeteringPointDelegate()),
        )
    )
