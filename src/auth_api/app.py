from energytt_platform.api import Application, ScopedGuard

from .config import SERVICE_NAME
from .endpoints import (
    OnboardUser,
    ForwardAuth,
    OpenIdAuthenticate,
    OpenIdAuthenticateCallback,
    DemoEndpoint,
    HealthCheck,
)


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """
    app = Application(
        name=SERVICE_NAME,
    )

    app.add_endpoint(
        method='GET',
        path='/health',
        endpoint=HealthCheck(),
    )

    app.add_endpoint(
        method='POST',
        path='/onboard',
        endpoint=OnboardUser(),
    )

    app.add_endpoint(
        method='GET',
        path='/auth',
        endpoint=ForwardAuth(),
    )

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

    # app.add_endpoint(
    #     method='GET',
    #     path='/demo',
    #     endpoint=DemoEndpoint(),
    #     guards=[
    #         # ServiceGuard(),
    #         ScopedGuard('gc.read', 'gc.transfer'),
    #     ],
    # )

    return app

    # return Application.create(
    #     name=SERVICE_NAME,
    #     endpoints=(
    #         ('POST', '/onboard', OnboardUser()),
    #         ('POST', '/auth', ForwardAuth()),
    #
    #         # OpenID Connect endpoints
    #         ('GET',  '/oidc/auth', OpenIdAuthenticate()),
    #         ('GET',  '/oidc/callback', OpenIdAuthenticateCallback()),
    #     )
    # )
