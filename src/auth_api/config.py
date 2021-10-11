import os


DEBUG = True

# Service description
SERVICE_URL = 'http://localhost:9096'
COOKIE_DOMAIN = '127.0.0.1'
INTERNAL_TOKEN_SECRET = '54321'
INTERNAL_TOKEN_SECRET = '54321'

# Tokens
TOKEN_HEADER_NAME = 'Authorization'
TOKEN_COOKIE_NAME = 'Authorization'
TOKEN_COOKIE_DOMAIN = COOKIE_DOMAIN
TOKEN_DEFAULT_SCOPES = [
    'meteringpoints.read',
    'measurements.read',
]

# OpenID Connect
OIDC_CLIENT_ID = os.environ['OIDC_CLIENT_ID']
OIDC_CLIENT_SECRET = os.environ['OIDC_CLIENT_SECRET']
# OIDC_WANTED_SCOPES = os.environ['OIDC_WANTED_SCOPES'].split(' ')
# OIDC_WANTED_SCOPES = ('openid', 'mitid', 'nemid', 'ssn', 'userinfo_token')
# OIDC_PROVIDER_URL = 'https://pp.netseidbroker.dk/op/connect/authorize'
OIDC_LOGIN_URL = os.environ['OIDC_LOGIN_URL']
OIDC_LOGOUT_URL = os.environ['OIDC_LOGOUT_URL']
OIDC_TOKEN_URL = os.environ['OIDC_TOKEN_URL']
OIDC_JWKS_URL = os.environ['OIDC_JWKS_URL']
# OIDC_WELLKNOWN_URL = 'https://pp.netseidbroker.dk/op/.well-known/openid-configuration'
OIDC_LOGIN_REDIRECT_URL = f'{SERVICE_URL}/oidc/login/callback'
# OIDC_LOGOUT_REDIRECT_URL = ''

# SQL
SQL_URI = os.environ['SQL_URI']
SQL_POOL_SIZE = int(os.getenv('SQL_POOL_SIZE', 1))
