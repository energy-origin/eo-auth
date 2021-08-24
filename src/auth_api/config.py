import os


# Service description
# SERVICE_NAME = 'Auth API'
SERVICE_SECRET = '12345'
# SERVICE_URL = 'http://eloprindelse.dk/auth'
SERVICE_URL = 'http://localhost:9096'

# OpenID Connect
OIDC_CLIENT_ID = '0a775a87-878c-4b83-abe3-ee29c720c3e7'
OIDC_CLIENT_SECRET = 'rnlguc7CM/wmGSti4KCgCkWBQnfslYr0lMDZeIFsCJweROTROy2ajEigEaPQFl76Py6AVWnhYofl/0oiSAgdtg=='
OIDC_WANTED_SCOPES = ('openid', 'mitid', 'nemid')
# OIDC_PROVIDER_URL = 'https://pp.netseidbroker.dk/op/connect/authorize'
OIDC_AUTH_URL = 'https://pp.netseidbroker.dk/op/connect/authorize'
OIDC_TOKEN_URL = 'https://pp.netseidbroker.dk/op/connect/token'
OIDC_JWKS_URL = 'https://pp.netseidbroker.dk/op/.well-known/openid-configuration/jwks'
# OIDC_WELLKNOWN_URL = 'https://pp.netseidbroker.dk/op/.well-known/openid-configuration'
OIDC_LOGIN_REDIRECT_URL = f'{SERVICE_URL}/oidc/callback'
# OIDC_LOGOUT_REDIRECT_URL = ''

# System
SYSTEM_SECRET = '54321'

# Event Bus
EVENT_BUS_HOST = os.environ.get('EVENT_BUS_HOST', 'localhost')
EVENT_BUS_PORT = int(os.environ.get('EVENT_BUS_PORT', 9092))
EVENT_BUS_SERVERS = [
    f'{EVENT_BUS_HOST}:{EVENT_BUS_PORT}',
]
