import os


DEBUG = True

# Service description
SERVICE_URL = 'http://localhost:9096'
SERVICE_DOMAIN = '127.0.0.1'
INTERNAL_TOKEN_SECRET = '54321'

# Tokens
TOKEN_HEADER_NAME = 'Authorization'
TOKEN_COOKIE_NAME = 'Authorization'
TOKEN_COOKIE_DOMAIN = SERVICE_DOMAIN
TOKEN_DEFAULT_SCOPES = [
    'meteringpoints.read',
    'measurements.read',
]

# OpenID Connect
OIDC_CLIENT_ID = '0a775a87-878c-4b83-abe3-ee29c720c3e7'
OIDC_CLIENT_SECRET = 'rnlguc7CM/wmGSti4KCgCkWBQnfslYr0lMDZeIFsCJweROTROy2ajEigEaPQFl76Py6AVWnhYofl/0oiSAgdtg=='
# OIDC_WANTED_SCOPES = ('openid', 'mitid', 'nemid')
OIDC_WANTED_SCOPES = ('openid', 'mitid', 'nemid', 'ssn', 'userinfo_token')
# OIDC_PROVIDER_URL = 'https://pp.netseidbroker.dk/op/connect/authorize'
OIDC_LOGIN_URL = 'https://pp.netseidbroker.dk/op/connect/authorize'
OIDC_LOGOUT_URL = 'https://pp.netseidbroker.dk/op/connect/endsession'
OIDC_TOKEN_URL = 'https://pp.netseidbroker.dk/op/connect/token'
OIDC_JWKS_URL = 'https://pp.netseidbroker.dk/op/.well-known/openid-configuration/jwks'
# OIDC_WELLKNOWN_URL = 'https://pp.netseidbroker.dk/op/.well-known/openid-configuration'
OIDC_LOGIN_REDIRECT_URL = f'{SERVICE_URL}/oidc/login/callback'
# OIDC_LOGOUT_REDIRECT_URL = ''

# SQL
SQL_URI = os.getenv('SQL_URI', 'postgresql://postgres:1234@localhost:5432/auth')
SQL_POOL_SIZE = int(os.getenv('SQL_POOL_SIZE', 1))
