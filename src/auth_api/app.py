from energytt_platform.api import Application, TokenGuard

from auth_shared.config import TOKEN_SECRET
from .endpoints import (
    ForwardAuth,
    CreateTestToken,
    OpenIdAuthenticate,
    OpenIdAuthenticateCallback,
    GetMeteringPointDelegateList,
    GrantMeteringPointDelegate,
    RevokeMeteringPointDelegate,
)


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """
    app = Application.create(
        name='Auth API',
        secret=TOKEN_SECRET,
        health_check_path='/health',
    )

    # -- Træfik integration --------------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/auth',
        endpoint=ForwardAuth(),
    )

    # -- OpenID Connect ------------------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/oidc/auth',
        endpoint=OpenIdAuthenticate(),
    )

    app.add_endpoint(
        method='GET',
        path='/oidc/callback',
        endpoint=OpenIdAuthenticateCallback(),
    )

    # -- MeteringPoint Delegates ---------------------------------------------

    app.add_endpoint(
        method='POST',
        path='/delegates/meteringpoints/list',
        endpoint=GetMeteringPointDelegateList(),
        guards=[TokenGuard()],
    )

    app.add_endpoint(
        method='POST',
        path='/delegates/meteringpoints/grant',
        endpoint=GrantMeteringPointDelegate(),
        guards=[TokenGuard()],
    )

    app.add_endpoint(
        method='POST',
        path='/delegates/meteringpoints/revoke',
        endpoint=RevokeMeteringPointDelegate(),
        guards=[TokenGuard()],
    )

    # -- Testing/misc --------------------------------------------------------

    app.add_endpoint(
        method='POST',
        path='/create-test-token',
        endpoint=CreateTestToken(),
    )

    return app
