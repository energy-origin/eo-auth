import json
import requests
from typing import Optional
from authlib.jose import jwt
from authlib.integrations.requests_client import OAuth2Session

from .config import (
    OIDC_CLIENT_ID,
    OIDC_CLIENT_SECRET,
    OIDC_WANTED_SCOPES,
    OIDC_AUTH_URL,
    OIDC_TOKEN_URL,
    OIDC_JWKS_URL,
    OIDC_LOGIN_REDIRECT_URL,
)


DEBUG = True


class OidcBackend(object):
    """
    TODO
    """

    @property
    def client(self):
        """
        :rtype: OAuth2Session
        """
        return OAuth2Session(
            client_id=OIDC_CLIENT_ID,
            client_secret=OIDC_CLIENT_SECRET,
            scope=OIDC_WANTED_SCOPES,
        )

    def create_authorization_url(self, state: Optional[str] = None):
        """
        :rtype: (str, str)
        :returns: Tuple of (login_url, state)
        """
        return self.client.create_authorization_url(
            url=OIDC_AUTH_URL,
            state=state,
            redirect_uri=OIDC_LOGIN_REDIRECT_URL,
        )

    def fetch_token(self, code: str, state: str):
        """
        :param str code:
        :param str state:
        :rtype: collections.abc.Mapping
        """
        return self.client.fetch_token(
            url=OIDC_TOKEN_URL,
            grant_type='authorization_code',
            code=code,
            state=state,
            redirect_uri=OIDC_LOGIN_REDIRECT_URL,
            verify=not DEBUG,
        )
        # try:
        #     return self.client.fetch_token(
        #         url=OIDC_TOKEN_URL,
        #         grant_type='authorization_code',
        #         code=code,
        #         state=state,
        #         redirect_uri=OIDC_LOGIN_REDIRECT_URL,
        #         verify=not DEBUG,
        #     )
        # except json.decoder.JSONDecodeError as e:
        #     # logger.exception('JSONDecodeError from Hydra', extra={'doc': e.doc})
        #     raise

    def refresh_token(self, refresh_token):
        """
        :param str refresh_token:
        :rtype: OAuth2Token
        """
        try:
            return self.client.refresh_token(
                url=OIDC_TOKEN_URL,
                refresh_token=refresh_token,
                verify=not DEBUG,
            )
        except json.decoder.JSONDecodeError as e:
            # logger.exception('JSONDecodeError from Hydra', extra={'doc': e.doc})
            raise

    def get_id_token(self, token):
        """
        :param collections.abc.Mapping token:
        :rtype: collections.abc.Mapping
        """
        j = self.get_jwks()
        if 'id_token' in token:
            return jwt.decode(token['id_token'], key=j)
        else:
            return None

    def get_jwks(self):
        """
        TODO cache?
        :rtype: str
        """
        jwks_response = requests.get(url=OIDC_JWKS_URL, verify=not DEBUG)
        jwks = jwks_response.content
        return jwks.decode()

    # def get_jwks(self):
    #     """
    #     TODO cache?
    #     :rtype: str
    #     """
    #     jwks = redis.get('HYDRA_JWKS')
    #
    #     if jwks is None:
    #         jwks_response = requests.get(url=OIDC_WELLKNOWN_URL, verify=not DEBUG)
    #         jwks = jwks_response.content
    #         redis.set('HYDRA_JWKS', jwks.decode(), ex=3600)
    #
    #     return jwks.decode()

    # def get_logout_url(self):
    #     """
    #     Returns the url do redirect the user to, to complete the logout.
    #     :rtype: str
    #     """
    #
    #     return HYDRA_LOGOUT_ENDPOINT


# -- Singletons --------------------------------------------------------------


oidc = OidcBackend()
