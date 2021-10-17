import os


# -- General -----------------------------------------------------------------

# Enable/disable debug mode
DEBUG = True

# Service' public URL
SERVICE_URL = 'http://localhost:9096'

# Secret used to sign internal token
INTERNAL_TOKEN_SECRET = '54321'

# Key to encrypt social security numbers
SSN_ENCRYPTION_KEY = '54321'


# -- SQL ---------------------------------------------------------------------

# SqlAlchemy connection string
SQL_URI = os.environ['SQL_URI']

# Number of concurrent connection to SQL database
SQL_POOL_SIZE = int(os.getenv('SQL_POOL_SIZE', 1))


# -- Tokens ------------------------------------------------------------------

# The header to read internal tokens from
TOKEN_HEADER_NAME = 'Authorization'

# The cookie to set tokens in
TOKEN_COOKIE_NAME = 'Authorization'

# The domain to set token cookie on
TOKEN_COOKIE_DOMAIN = '127.0.0.1'

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

# Callback URL after OpenID Connect logout flow
OIDC_LOGOUT_CALLBACK_PATH = '/oidc/logout/callback'
OIDC_LOGOUT_CALLBACK_URL = \
    f'{SERVICE_URL}{OIDC_LOGOUT_CALLBACK_PATH}'


# -- OpenID Connect ----------------------------------------------------------

OIDC_CLIENT_ID = os.environ['OIDC_CLIENT_ID']
OIDC_CLIENT_SECRET = os.environ['OIDC_CLIENT_SECRET']
OIDC_LOGIN_URL = os.environ['OIDC_LOGIN_URL']
OIDC_LOGOUT_URL = os.environ['OIDC_LOGOUT_URL']
OIDC_TOKEN_URL = os.environ['OIDC_TOKEN_URL']
OIDC_JWKS_URL = os.environ['OIDC_JWKS_URL']
