import pytest
from energytt_platform.auth import TOKEN_COOKIE_NAME
from flask.testing import FlaskClient
from datetime import datetime, timedelta, timezone

from energytt_platform.sql import SqlEngine

from auth_api.models import DbToken


class TestForwardAuth:
    """
    TODO
    """

    def test__no_token__should_return_no_header_and_status_401(
            self,
            client: FlaskClient,
            session: SqlEngine.Session,
    ):
        """
        TODO
        """

        # -- Act -------------------------------------------------------------

        r = client.get('/token/forward-auth')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401
        assert 'Authorization' not in r.headers

    def test__invalid_token__should_return_no_header_and_status_401(
            self,
            client: FlaskClient,
            session: SqlEngine.Session,
    ):
        """
        TODO
        """

        # -- Act -------------------------------------------------------------

        client.set_cookie(
            server_name='domain.com',  # TODO
            key=TOKEN_COOKIE_NAME,
            value='INVALID-TOKEN',
        )

        r = client.get('/token/forward-auth')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401
        assert 'Authorization' not in r.headers

    @pytest.mark.parametrize('issued, expires', [
        # Token is issued AFTER now:
        (
            datetime.now(tz=timezone.utc) + timedelta(days=1),
            datetime.now(tz=timezone.utc) + timedelta(days=2),
        ),
        # Token is expired:
        (
            datetime.now(tz=timezone.utc) - timedelta(days=2),
            datetime.now(tz=timezone.utc) - timedelta(days=1),
        ),
    ])
    def test__token_issue_or_expire_not_valid_right_now__should_return_no_header_and_status_401(
            self,
            issued: datetime,
            expires: datetime,
            client: FlaskClient,
            session: SqlEngine.Session,
    ):
        """
        TODO
        """

        opaque_token = '12345'
        internal_token = '54321'

        session.begin()
        session.add(DbToken(
            opaque_token=opaque_token,
            internal_token=internal_token,
            issued=issued,
            expires=expires,
            subject='subject',
        ))
        session.commit()

        # -- Act -------------------------------------------------------------

        client.set_cookie(
            server_name='domain.com',  # TODO
            key=TOKEN_COOKIE_NAME,
            value=opaque_token,
        )

        r = client.get('/token/forward-auth')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401
        assert 'Authorization' not in r.headers

    def test__token_exists__should_return_authorization_header_and_status_200(
            self,
            client: FlaskClient,
            session: SqlEngine.Session,
    ):
        """
        TODO
        """

        opaque_token = '12345'
        internal_token = '54321'

        session.begin()
        session.add(DbToken(
            opaque_token=opaque_token,
            internal_token=internal_token,
            issued=datetime.now(tz=timezone.utc),
            expires=datetime.now(tz=timezone.utc) + timedelta(days=1),
            subject='subject',
        ))
        session.commit()

        # -- Act -------------------------------------------------------------

        client.set_cookie(
            server_name='domain.com',  # TODO
            key=TOKEN_COOKIE_NAME,
            value=opaque_token,
        )

        r = client.get('/token/forward-auth')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.headers['Authorization'] == f'Bearer: {internal_token}'


# class TestInspectToken:
#     """
#     TODO
#
#     - Test valid token
#     - Test expired token
#     """
#
#     def test__should_return_auth_url_with_correct_state(
#             self,
#             client: FlaskClient,
#             state_encoder: TokenEncoder[AuthState],
#     ):
#         """
#         TODO
#         """
#
#         # -- Act -------------------------------------------------------------
#
#         r = client.get(
#             path='/oidc/login',
#             query_string={'redirect_uri': 'http://return.com/'},
#         )
#
#         # -- Assert ----------------------------------------------------------
#
#         actual_state = get_auth_state_from_redirect_url(
#             auth_url=r.json['url'],
#             state_encoder=state_encoder,
#         )
#
#         assert r.status_code == 200
#         assert actual_state.redirect_uri == 'http://return.com/'

#     def test__should_redirect_to_auth_url_with_correct_state(
#             self,
#             client: FlaskClient,
#             state_encoder: TokenEncoder[AuthState],
#     ):
#         """
#         TODO
#         """
#
#         # -- Act -------------------------------------------------------------
#
#         r = client.get(
#             path='/oidc/login/redirect',
#             query_string={'redirect_uri': 'http://return.com/'},
#         )
#
#         # -- Assert ----------------------------------------------------------
#
#         actual_state = get_auth_state_from_redirect_url(
#             auth_url=r.headers['Location'],
#             state_encoder=state_encoder,
#         )
#
#         assert r.status_code == 307
#         assert actual_state.redirect_uri == 'http://return.com/'
#
#     @pytest.mark.parametrize('path', [
#         '/oidc/login',
#         '/oidc/login/redirect',
#     ])
#     def test__omit_parameter_redirect_uri__should_return_status_400(
#             self,
#             path: str,
#             client: FlaskClient,
#     ):
#         """
#         TODO
#         """
#
#         # -- Act -------------------------------------------------------------
#
#         r = client.get(
#             path='/oidc/login',
#             query_string={},  # Missing parameter "redirect_uri"
#         )
#
#         # -- Assert ----------------------------------------------------------
#
#         assert r.status_code == 400
#
#
# class TestOidcCallback:
#     """
#     Tests OpenID Connect Auth Callback endpoint.
#
#     TODO Test these:
#
#     oidc.py:
#         - Pass errors, should pass errors to redirect_url as query parameters
#
#     backend.py:
#         - self.session.fetch_token() returns no ID token (None or '')
#         - self.session.fetch_token() returns no ID token (None or '')
#         - self.session.fetch_token() returns no UserInfo token (None or '')
#
#     """
#
#     @pytest.mark.parametrize('state', ['', None])
#     def test__invalid_state__should_return_status_400(
#             self,
#             state: str,
#             client: FlaskClient,
#     ):
#         """
#         TODO
#         """
#
#         # -- Act -------------------------------------------------------------
#
#         r = client.get(
#             path='/oidc/login/callback',
#             query_string={'state': state},
#         )
#
#         # -- Assert ----------------------------------------------------------
#
#         assert r.status_code == 400
#
#     def test__valid_state_and_no_errors__should_set_cookie_and_redirect(
#             self,
#             client: FlaskClient,
#             token_raw: Dict[str, Any],
#             # id_token: MagicMock,
#             session,
#             oauth2_session: MagicMock,
#             state_encoder: TokenEncoder[AuthState],
#     ):
#         """
#         TODO
#         """
#
#         # -- Arrange ---------------------------------------------------------
#
#         state = AuthState(
#             created=datetime.now(tz=timezone.utc),
#             redirect_uri='http://redirect-here.com',
#         )
#
#         state_encoded = state_encoder.encode(state)
#
#         oauth2_session.fetch_token.return_value = token_raw
#
#         # -- Act -------------------------------------------------------------
#
#         r = client.get(
#             path='/oidc/login/callback',
#             query_string={
#                 'code': 'some-code',
#                 'state': state_encoded,
#             },
#         )
#
#         # -- Assert ----------------------------------------------------------
#
#         assert r.status_code == 307
#         assert r.headers['Location'] == 'http://redirect-here.com'
#
#         # Assert cookies
#         cookies = CookieTester(r.headers)
#         cookies.assert_has_cookies(TOKEN_COOKIE_NAME)
#         cookies.assert_cookie(
#             name=TOKEN_COOKIE_NAME,
#             domain=TOKEN_COOKIE_DOMAIN,
#             http_only=True,
#             same_site=True,
#             secure=True,
#         )
#
#         # Assert Identity Provider
#         oauth2_session.fetch_token.assert_called_once_with(
#             url=OIDC_TOKEN_URL,
#             grant_type='authorization_code',
#             code='some-code',
#             state=state_encoded,
#             redirect_uri=OIDC_LOGIN_REDIRECT_URL,
#             verify=not DEBUG,
#         )
#
#         # -- Inspect token ---------------------------------------------------
#
#         opaque_token = cookies.get_value(TOKEN_COOKIE_NAME)
#
#         client.set_cookie(
#             server_name=TOKEN_COOKIE_DOMAIN,
#             key=TOKEN_COOKIE_NAME,
#             value=opaque_token,
#             secure=True,
#             httponly=True,
#             samesite='Strict',
#         )
#
#         r_inspect = client.get('/token/inspect')
#
#         assert r_inspect.status_code == 200
#
#         try:
#             assert r_inspect.json == {
#                 'issued': '',
#                 'expires': '',
#                 'actor': '',
#                 'subject': '',
#                 'scope': [''],
#             }
#         except:
#             j = 2
#             raise
