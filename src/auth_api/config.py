import os


# -- General -----------------------------------------------------------------

# Enable/disable debug mode
DEBUG = True

# Service' public URL
SERVICE_URL = os.environ.get('SERVICE_URL', '')

# Secret used to sign internal token
INTERNAL_TOKEN_SECRET = os.environ.get('INTERNAL_TOKEN_SECRET', '')

# Key to encrypt social security numbers
SSN_ENCRYPTION_KEY = os.environ.get('SSN_ENCRYPTION_KEY', '')


# -- SQL ---------------------------------------------------------------------

# SqlAlchemy connection string
SQL_URI = os.environ.get('SQL_URI', '')

# Number of concurrent connection to SQL database
SQL_POOL_SIZE = int(os.getenv('SQL_POOL_SIZE', 1))


# -- Tokens ------------------------------------------------------------------

# The domain to set token cookie on
TOKEN_COOKIE_DOMAIN = os.environ.get('TOKEN_COOKIE_DOMAIN', '127.0.0.1')

# Scopes to grant when creating internal tokens
TOKEN_DEFAULT_SCOPES = [
    'meteringpoints.read',
    'measurements.read',
]


# -- URLs --------------------------------------------------------------------

# Callback URL after OpenID Connect authentication flow
OIDC_LOGIN_CALLBACK_PATH = '/oidc/login/callback'
OIDC_LOGIN_CALLBACK_URL = \
    f'{SERVICE_URL}{OIDC_LOGIN_CALLBACK_PATH}'

# Callback URL after OpenID Connect SSN validation flow
OIDC_SSN_VALIDATE_CALLBACK_PATH = '/oidc/login/callback/ssn'
OIDC_SSN_VALIDATE_CALLBACK_URL = \
    f'{SERVICE_URL}{OIDC_SSN_VALIDATE_CALLBACK_PATH}'


# -- OpenID Connect ----------------------------------------------------------

OIDC_CLIENT_ID = os.environ.get('OIDC_CLIENT_ID')
OIDC_CLIENT_SECRET = os.environ.get('OIDC_CLIENT_SECRET')
OIDC_AUTHORITY_URL = os.environ.get('OIDC_AUTHORITY_URL')

OIDC_LOGIN_URL = f'{OIDC_AUTHORITY_URL}/connect/authorize'
OIDC_TOKEN_URL = f'{OIDC_AUTHORITY_URL}/connect/token'
OIDC_JWKS_URL = f'{OIDC_AUTHORITY_URL}/.well-known/openid-configuration/jwks'
OIDC_API_LOGOUT_URL = f'{OIDC_AUTHORITY_URL}/api/v1/session/logout'
