from energytt_platform.api import Application

from .config import (
    INTERNAL_TOKEN_SECRET,
    OIDC_LOGIN_CALLBACK_PATH,
    OIDC_SSN_VALIDATE_CALLBACK_PATH,
    OIDC_LOGOUT_CALLBACK_PATH,
)
from .endpoints import (
    ForwardAuth,
    InspectToken,
    CreateTestToken,
    OpenIdLogin,
    # OpenIdLoginRedirect,
    OpenIDLoginCallback,
    OpenIDSsnCallback,
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

    # app.add_endpoint(
    #     method='GET',
    #     path='/oidc/login/redirect',
    #     endpoint=OpenIdLoginRedirect(),
    # )

    app.add_endpoint(
        method='GET',
        path=OIDC_LOGIN_CALLBACK_PATH,
        endpoint=OpenIDLoginCallback(),
    )

    app.add_endpoint(
        method='GET',
        path=OIDC_SSN_VALIDATE_CALLBACK_PATH,
        endpoint=OpenIDSsnCallback(),
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
        path=OIDC_LOGOUT_CALLBACK_PATH,
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
