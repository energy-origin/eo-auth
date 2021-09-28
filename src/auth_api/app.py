from energytt_platform.api import Application

from auth_api.config import INTERNAL_TOKEN_SECRET

from .endpoints import (
    ForwardAuth,
    InspectToken,
    CreateTestToken,
    OpenIdLogin,
    OpenIdLoginRedirect,
    OpenIdLoginCallback,
    OpenIdLogout,
    OpenIdLogoutRedirect,
    OpenIdLogoutCallback,
)


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """

    app = Application.create(
        name='Auth API',
        secret=INTERNAL_TOKEN_SECRET,
        health_check_path='/health',
    )

    # -- OpenID Connect Login ------------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/oidc/login',
        endpoint=OpenIdLogin(),
    )

    app.add_endpoint(
        method='GET',
        path='/oidc/login/redirect',
        endpoint=OpenIdLoginRedirect(),
    )

    app.add_endpoint(
        method='GET',
        path='/oidc/login/callback',
        endpoint=OpenIdLoginCallback(),
    )

    # -- OpenID Connect Logout -----------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/oidc/logout',
        endpoint=OpenIdLogout(),
    )

    app.add_endpoint(
        method='GET',
        path='/oidc/logout/redirect',
        endpoint=OpenIdLogoutRedirect(),
    )

    app.add_endpoint(
        method='GET',
        path='/oidc/logout/callback',
        endpoint=OpenIdLogoutCallback(),
    )

    # -- Træfik integration --------------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/token/forward-auth',
        endpoint=ForwardAuth(),
    )

    # -- Testing/misc --------------------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/token/inspect',
        endpoint=InspectToken(),
    )

    app.add_endpoint(
        method='POST',
        path='/token/create-test-token',
        endpoint=CreateTestToken(),
    )

    return app
