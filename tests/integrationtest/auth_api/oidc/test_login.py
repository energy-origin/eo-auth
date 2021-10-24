import pytest
from flask.testing import FlaskClient
from urllib.parse import parse_qs, urlsplit

from energytt_platform.tokens import TokenEncoder

from auth_api.oidc import AuthState


# -- Helpers -----------------------------------------------------------------


def get_auth_state_from_redirect_url(
        auth_url: str,
        state_encoder: TokenEncoder[AuthState],
) -> AuthState:
    """
    TODO
    """
    url = urlsplit(auth_url)
    query = parse_qs(url.query)
    state_encoded = query['state'][0]
    return state_encoder.decode(state_encoded)


# -- Tests -------------------------------------------------------------------


class TestOidcLogin:
    """
    Tests OpenID Connect Auth endpoint.
    """

    def test__without_redirect__should_return_auth_url_as_json_with_correct_state(
            self,
            client: FlaskClient,
            state_encoder: TokenEncoder[AuthState],
    ):
        """
        Omitting the 'redirect' parameter should result in the endpoint
        returning the auth URL as part of JSON body.
        """

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/oidc/login',
            query_string={
                'return_url': 'http://return.com/',
            },
        )

        # -- Assert ----------------------------------------------------------

        actual_state = get_auth_state_from_redirect_url(
            auth_url=r.json['url'],
            state_encoder=state_encoder,
        )

        assert r.status_code == 200
        assert actual_state.return_url == 'http://return.com/'

    def test__with_redirect__should_return_auth_url_as_json_with_correct_state(
            self,
            client: FlaskClient,
            state_encoder: TokenEncoder[AuthState],
    ):
        """
        Including the 'redirect' parameter should result in the endpoint
        returning the auth URL as part of a HTTP redirect.
        """

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/oidc/login',
            query_string={
                'return_url': 'http://return.com/',
                'redirect': '1',
            },
        )

        # -- Assert ----------------------------------------------------------

        actual_state = get_auth_state_from_redirect_url(
            auth_url=r.headers['Location'],
            state_encoder=state_encoder,
        )

        assert r.status_code == 307
        assert actual_state.return_url == 'http://return.com/'

    @pytest.mark.parametrize('path', [
        '/oidc/login',
        '/oidc/login/redirect',
    ])
    def test__omit_parameter_redirect_uri__should_return_status_400(
            self,
            path: str,
            client: FlaskClient,
    ):
        """
        TODO
        """

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/oidc/login',
            query_string={},  # Missing parameter "redirect_uri"
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 400
