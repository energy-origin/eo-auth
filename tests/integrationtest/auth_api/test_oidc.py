import pytest
from typing import Dict, Any
from unittest.mock import MagicMock

from flask.testing import FlaskClient
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit

from energytt_platform.sql import SqlEngine
from energytt_platform.tokens import TokenEncoder
from energytt_platform.auth import TOKEN_HEADER_NAME
from energytt_platform.api.testing import CookieTester

from auth_api.endpoints.oidc import AuthState
from auth_api.config import (
    DEBUG,
    OIDC_TOKEN_URL,
    OIDC_LOGIN_REDIRECT_URL,
    TOKEN_COOKIE_NAME,
    TOKEN_COOKIE_DOMAIN,
)


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


def assert_token(
        client: FlaskClient,
        opaque_token: str,
        expected_token: Dict[str, Any],
):
    """
    Provided an opaque token, this function translates it to an
    internal token and asserts on it's content.

    :param client:
    :param opaque_token:
    :param expected_token:
    :return:
    """
    client.set_cookie(
        server_name=TOKEN_COOKIE_DOMAIN,
        key=TOKEN_COOKIE_NAME,
        value=opaque_token,
        secure=True,
        httponly=True,
        samesite='Strict',
    )

    r_forwardauth = client.get('/token/forward-auth')

    r_inspect = client.get(
        path='/token/inspect',
        headers={TOKEN_HEADER_NAME: r_forwardauth.headers[TOKEN_HEADER_NAME]}
    )

    assert r_inspect.status_code == 200
    assert r_inspect.json == {'token': expected_token}


# -- Tests -------------------------------------------------------------------


class TestOidcAuth:
    """
    Tests OpenID Connect Auth endpoint.
    """

    def test__should_return_auth_url_with_correct_state(
            self,
            client: FlaskClient,
            state_encoder: TokenEncoder[AuthState],
    ):
        """
        TODO
        """

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/oidc/login',
            query_string={'redirect_uri': 'http://return.com/'},
        )

        # -- Assert ----------------------------------------------------------

        actual_state = get_auth_state_from_redirect_url(
            auth_url=r.json['url'],
            state_encoder=state_encoder,
        )

        assert r.status_code == 200
        assert actual_state.redirect_uri == 'http://return.com/'

    def test__should_redirect_to_auth_url_with_correct_state(
            self,
            client: FlaskClient,
            state_encoder: TokenEncoder[AuthState],
    ):
        """
        TODO
        """

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/oidc/login/redirect',
            query_string={'redirect_uri': 'http://return.com/'},
        )

        # -- Assert ----------------------------------------------------------

        actual_state = get_auth_state_from_redirect_url(
            auth_url=r.headers['Location'],
            state_encoder=state_encoder,
        )

        assert r.status_code == 307
        assert actual_state.redirect_uri == 'http://return.com/'

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


class TestOidcCallback:
    """
    Tests OpenID Connect Auth Callback endpoint.

    TODO Test these:

    oidc.py:
        - Pass errors, should pass errors to redirect_url as query parameters

    backend.py:
        - self.session.fetch_token() returns no ID token (None or '')
        - self.session.fetch_token() returns no ID token (None or '')
        - self.session.fetch_token() returns no UserInfo token (None or '')

    """

    @pytest.mark.parametrize('state', ['', None])
    def test__invalid_state__should_return_status_400(
            self,
            state: str,
            client: FlaskClient,
    ):
        """
        TODO
        """

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/oidc/login/callback',
            query_string={'state': state},
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 400

    def test__valid_state_and_no_errors__should_set_cookie_and_redirect(
            self,
            client: FlaskClient,
            jwk_public: str,
            token_raw: Dict[str, Any],
            id_token: Dict[str, Any],
            session: SqlEngine.Session,
            oauth2_session: MagicMock,
            state_encoder: TokenEncoder[AuthState],
    ):
        """
        TODO
        """

        # -- Arrange ---------------------------------------------------------

        state = AuthState(
            created=datetime.now(tz=timezone.utc),
            redirect_uri='http://redirect-here.com',
        )

        state_encoded = state_encoder.encode(state)

        oauth2_session.get_jwk.return_value = jwk_public
        oauth2_session.fetch_token.return_value = token_raw

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/oidc/login/callback',
            query_string={
                'code': 'some-code',
                'state': state_encoded,
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 307
        assert r.headers['Location'] == 'http://redirect-here.com?success=1'

        # Assert cookies
        cookies = CookieTester(r.headers)
        cookies.assert_has_cookies(TOKEN_COOKIE_NAME)
        cookies.assert_cookie(
            name=TOKEN_COOKIE_NAME,
            domain=TOKEN_COOKIE_DOMAIN,
            http_only=True,
            same_site=True,
            secure=True,
        )

        # Assert Identity Provider
        oauth2_session.fetch_token.assert_called_once_with(
            url=OIDC_TOKEN_URL,
            grant_type='authorization_code',
            code='some-code',
            state=state_encoded,
            redirect_uri=OIDC_LOGIN_REDIRECT_URL,
            verify=not DEBUG,
        )

        # -- Inspect token ---------------------------------------------------

        # Inspect the content of the [opaque] token returned by the endpoint

        opaque_token = cookies.get_value(TOKEN_COOKIE_NAME)

        issued_expected = datetime \
            .fromtimestamp(id_token['iat']) \
            .astimezone(timezone.utc) \
            .isoformat()

        expires_expected = datetime \
            .fromtimestamp(id_token['exp']) \
            .astimezone(timezone.utc) \
            .isoformat()

        token_expected = {
            'issued': issued_expected,
            'expires': expires_expected,
            'actor': id_token['sub'],
            'subject': id_token['sub'],
            'scope': ['meteringpoints.read', 'measurements.read'],
        }

        assert_token(
            client=client,
            opaque_token=opaque_token,
            expected_token=token_expected,
        )

    def test__valid_state_and_no_errors__should_redirect_to_correct_url(
            self,
            client: FlaskClient,
            jwk_public: str,
            token_raw: Dict[str, Any],
            id_token: Dict[str, Any],
            session: SqlEngine.Session,
            oauth2_session: MagicMock,
            state_encoder: TokenEncoder[AuthState],
    ):
        """
        TODO
        """

        # -- Arrange ---------------------------------------------------------

        state = AuthState(
            created=datetime.now(tz=timezone.utc),
            redirect_uri='http://redirect-here.com?something=asd',
        )

        state_encoded = state_encoder.encode(state)

        oauth2_session.get_jwk.return_value = jwk_public
        oauth2_session.fetch_token.return_value = token_raw

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/oidc/login/callback',
            query_string={
                'code': 'some-code',
                'state': state_encoded,
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 307
        assert r.headers['Location'] == 'http://redirect-here.com?something=asd&success=1'
