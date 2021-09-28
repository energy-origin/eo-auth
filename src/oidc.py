# import json
# import requests
# from authlib.jose import jwt
# from authlib.common.security import generate_token
# from authlib.integrations.requests_client import OAuth2Session
#
# from auth_api.config import (
#     OIDC_CLIENT_ID,
#     OIDC_CLIENT_SECRET,
#     OIDC_WANTED_SCOPES,
#     OIDC_WANTED_SCOPES,
#     OIDC_LOGIN_REDIRECT_ENDPOINT,
# )
#
#
# # class OpenIdBackend(object):
# #     """
# #     TODO
# #     """
# #
# #     @property
# #     def client(self):
# #         """
# #         :rtype: OAuth2Session
# #         """
# #         return OAuth2Session(
# #             client_id=OIDC_CLIENT_ID,
# #             client_secret=OIDC_CLIENT_SECRET,
# #             scope=OIDC_WANTED_SCOPES,
# #         )
# #
# #     def register_login_state(self):
# #         """
# #         :rtype: (str, str)
# #         :returns: Tuple of (login_url, state)
# #         """
# #         self.client.
# #
# #         return self.client.create_authorization_url(
# #             url=HYDRA_AUTH_ENDPOINT,
# #             redirect_uri=OIDC_LOGIN_REDIRECT_ENDPOINT,
# #         )
# #         # try:
# #         #     return self.client.create_authorization_url(
# #         #         url=HYDRA_AUTH_ENDPOINT,
# #         #         redirect_uri=OIDC_LOGIN_REDIRECT_ENDPOINT,
# #         #     )
# #         # except json.decoder.JSONDecodeError as e:
# #         #     logger.exception('JSONDecodeError from Hydra', extra={'doc': e.doc})
# #         #     raise
# #
# #     def fetch_token(self, code, state):
# #         """
# #         :param str code:
# #         :param str state:
# #         :rtype: collections.abc.Mapping
# #         """
# #         try:
# #             return self.client.fetch_token(
# #                 url=HYDRA_TOKEN_ENDPOINT,
# #                 grant_type='authorization_code',
# #                 code=code,
# #                 state=state,
# #                 redirect_uri=LOGIN_CALLBACK_URL,
# #                 verify=not DEBUG,
# #             )
# #         except json.decoder.JSONDecodeError as e:
# #             logger.exception('JSONDecodeError from Hydra', extra={'doc': e.doc})
# #             raise
# #
# #     def refresh_token(self, refresh_token):
# #         """
# #         :param str refresh_token:
# #         :rtype: OAuth2Token
# #         """
# #         try:
# #             return self.client.refresh_token(
# #                 url=HYDRA_TOKEN_ENDPOINT,
# #                 refresh_token=refresh_token,
# #                 verify=not DEBUG,
# #             )
# #         except json.decoder.JSONDecodeError as e:
# #             logger.exception('JSONDecodeError from Hydra', extra={'doc': e.doc})
# #             raise
# #
# #     def get_id_token(self, token):
# #         """
# #         :param collections.abc.Mapping token:
# #         :rtype: collections.abc.Mapping
# #         """
# #         if 'id_token' in token:
# #             return jwt.decode(token['id_token'], key=self.get_jwks())
# #         else:
# #             return None
# #
# #     def get_jwks(self):
# #         """
# #         TODO cache?
# #         :rtype: str
# #         """
# #         jwks = redis.get('HYDRA_JWKS')
# #
# #         if jwks is None:
# #             jwks_response = requests.get(url=HYDRA_WELLKNOWN_ENDPOINT, verify=not DEBUG)
# #             jwks = jwks_response.content
# #             redis.set('HYDRA_JWKS', jwks.decode(), ex=3600)
# #
# #         return jwks.decode()
# #
# #     def get_logout_url(self):
# #         """
# #         Returns the url do redirect the user to, to complete the logout.
# #         :rtype: str
# #         """
# #         return HYDRA_LOGOUT_ENDPOINT
#
#
# client = OAuth2Session(
#     # client_id=OIDC_CLIENT_ID,
#     client_id='0a775a87-878c-4b83-abe3-ee29c720c3e7',
#     # client_secret=OIDC_CLIENT_SECRET,
#     client_secret='rnlguc7CM/wmGSti4KCgCkWBQnfslYr0lMDZeIFsCJweROTROy2ajEigEaPQFl76Py6AVWnhYofl/0oiSAgdtg==',
#     scope='openid mitid nemid',
#     redirect_uri='http://127.0.0.1:9090/oidc/callback',
# )
#
# with client as session:
#     # url, state = session.create_authorization_url(
#     #     url='https://pp.netseidbroker.dk/op/connect/authorize',
#     #     idp_values='openid mitid nemid',
#     #     grant_type='authorization_code',
#     # )
#
#     token = session.fetch_token(
#         url='https://pp.netseidbroker.dk/op/connect/token',
#         grant_type='authorization_code',
#         code='DF0D3C3278DD029DA97E39EEE9BA18F4D717A31320AEAF45930AA8BFB279D6D1',
#         state='NPFVVGh4xWekTRwXe6huc1NOWqMwmg',
#         redirect_uri='http://127.0.0.1:9090/oidc/callback',
#         verify=False,
#     )
#
#     j = 2
