from energytt_platform.api import Application

from .endpoints import (
    ForwardAuth,
    OpenIdAuthenticate,
    OpenIdAuthenticateCallback,
)


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """
    return Application.create(
        name='Auth API',
        health_check_path='/health',
        endpoints=(
            ('GET', '/auth', ForwardAuth()),
            ('GET', '/oidc/auth', OpenIdAuthenticate()),
            ('GET', '/oidc/callback', OpenIdAuthenticateCallback()),
        )
    )

    # app = Application(
    #     name=SERVICE_NAME,
    # )
    #
    # # app.add_endpoint(
    # #     method='GET',
    # #     path='/health',
    # #     endpoint=HealthCheck(),
    # # )
    #
    # app.add_endpoint(
    #     method='POST',
    #     path='/onboard',
    #     endpoint=OnboardUser(),
    # )
    #
    # app.add_endpoint(
    #     method='GET',
    #     path='/auth',
    #     endpoint=ForwardAuth(),
    # )
    #
    # app.add_endpoint(
    #     method='GET',
    #     path='/oidc/auth',
    #     endpoint=OpenIdAuthenticate(),
    # )
    #
    # app.add_endpoint(
    #     method='GET',
    #     path='/oidc/callback',
    #     endpoint=OpenIdAuthenticateCallback(),
    # )
    #
    # # app.add_endpoint(
    # #     method='GET',
    # #     path='/demo',
    # #     endpoint=DemoEndpoint(),
    # #     guards=[
    # #         # ServiceGuard(),
    # #         ScopedGuard('gc.read', 'gc.transfer'),
    # #     ],
    # # )
    #
    # return app
    #
    # # return Application.create(
    # #     name=SERVICE_NAME,
    # #     endpoints=(
    # #         ('POST', '/onboard', OnboardUser()),
    # #         ('POST', '/auth', ForwardAuth()),
    # #
    # #         # OpenID Connect endpoints
    # #         ('GET',  '/oidc/auth', OpenIdAuthenticate()),
    # #         ('GET',  '/oidc/callback', OpenIdAuthenticateCallback()),
    # #     )
    # # )
