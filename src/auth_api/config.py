import os


# Service description
SERVICE_NAME = 'Auth API'
SERVICE_SECRET = '12345'
# SERVICE_URL = 'http://eloprindelse.dk/auth'
SERVICE_URL = 'http://localhost:9096/auth'

# OpenID Connect
OIDC_CLIENT_ID = 'e3313f70-efba-4cca-a25c-4d8a2242c28e'
OIDC_CLIENT_SECRET = 'XB1iPJwcivl2bFMJJfeFNyLAGPTRjY1LlmZ3ZwBm+t2ccPjQfT7t6NIHOSRtMoLqjMeKfITtA3T2D9x5W4ArMg=='
OIDC_WANTED_SCOPES = ''
OIDC_PROVIDER_URL = 'https://pp.netseidbroker.dk/op/connect/authorize'
OIDC_WELLKNOWN_URL = 'https://pp.netseidbroker.dk/op/.well-known/openid-configuration'
OIDC_LOGIN_REDIRECT_ENDPOINT = f'{SERVICE_URL}/oidc/callback'
OIDC_LOGOUT_REDIRECT_URL = ''

# System
SYSTEM_SECRET = '54321'

# Event Bus
EVENT_BUS_HOST = os.environ.get('EVENT_BUS_HOST', 'localhost')
EVENT_BUS_PORT = int(os.environ.get('EVENT_BUS_PORT', 9092))
EVENT_BUS_SERVERS = [
    f'{EVENT_BUS_HOST}:{EVENT_BUS_PORT}',
]
