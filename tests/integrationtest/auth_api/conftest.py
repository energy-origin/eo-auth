"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import pytest
from uuid import uuid4
from typing import Dict, Any
from unittest.mock import patch
from authlib.jose import jwt, jwk
from flask.testing import FlaskClient
from datetime import datetime, timezone, timedelta

from energytt_platform.tokens import TokenEncoder

from auth_api.app import create_app
from auth_api.oidc import AuthState
from auth_api.config import INTERNAL_TOKEN_SECRET

from .keys import PRIVATE_KEY, PUBLIC_KEY


# -- API ---------------------------------------------------------------------


@pytest.fixture(scope='function')
def client() -> FlaskClient:
    """
    TODO
    """
    return create_app().test_client


@pytest.fixture(scope='function')
def oauth2_session():
    """
    TODO
    """
    with patch('auth_api.oidc.signaturgruppen.oidc.session') as session:
        yield session


@pytest.fixture(scope='function')
def state_encoder() -> TokenEncoder[AuthState]:
    """
    TODO
    """
    return TokenEncoder(
        schema=AuthState,
        secret=INTERNAL_TOKEN_SECRET,
    )


# -- Keys & Security ---------------------------------------------------------


@pytest.fixture(scope='function')
def jwk_public() -> str:
    """
    TODO
    """
    return jwk.dumps(PUBLIC_KEY, kty='RSA')


@pytest.fixture(scope='function')
def jwk_private() -> str:
    """
    TODO
    """
    return jwk.dumps(PRIVATE_KEY, kty='RSA')


# -- Tokens ------------------------------------------------------------------


@pytest.fixture(scope='function')
def token_issued() -> datetime:
    """
    TODO
    """
    return datetime.now(tz=timezone.utc)


@pytest.fixture(scope='function')
def token_expires(token_issued: datetime) -> datetime:
    """
    TODO
    """
    return token_issued + timedelta(days=1)


@pytest.fixture(scope='function')
def token_raw(
    id_token_encoded: str,
    userinfo_token_encoded: str,
    token_expires: datetime,
) -> Dict[str, Any]:
    """
    TODO
    """
    return {
        'id_token': id_token_encoded,
        'access_token': '',
        'expires_in': 3600,
        'token_type': 'Bearer',
        'scope': 'openid mitid nemid ssn userinfo_token',
        'userinfo_token': userinfo_token_encoded,
        'expires_at': int(token_expires.timestamp()),
    }


@pytest.fixture(scope='function')
def id_token(
        token_issued: datetime,
        token_expires: datetime,
) -> Dict[str, Any]:
    """
    TODO
    """
    return {
        'iss': 'https://pp.netseidbroker.dk/op',
        'nbf': 1632389546,
        'iat': int(token_issued.timestamp()),
        'exp': int(token_expires.timestamp()),
        'auth_time': int(token_issued.timestamp()),
        'aud': str(uuid4()),
        # 'aud': '0a775a87-878c-4b83-abe3-ee29c720c3e7',
        'amr': ['code_app'],
        'at_hash': '-Y-YJBoneGN5sEk6vawM9A',
        'sub': 'ad845954-ed1d-4c73-846a-ef9b4c36f6f8',
        'idp': 'mitid',
        'acr': 'https://data.gov.dk/concept/core/nsis/Substantial',
        'neb_sid': str(uuid4()),
        # 'neb_sid': '4e1bcbd3-d568-4319-9ce3-a1b110f86d53',
        'loa': 'https://data.gov.dk/concept/core/nsis/Substantial',
        'identity_type': 'private',
        'transaction_id': str(uuid4()),
        # 'transaction_id': 'a805f253-e8ea-4457-9996-c67bf704ab4a',
        'session_expiry': '1632403505',
    }


@pytest.fixture(scope='function')
def id_token_encoded(
        jwk_private: str,
        id_token: Dict[str, Any],
) -> str:
    """
    TODO
    """
    token = jwt.encode(
        header={'alg': 'RS256'},
        payload=id_token,
        key=jwk_private,
    )

    return token.decode()


@pytest.fixture(scope='function')
def userinfo_token() -> Dict[str, Any]:
    """
    TODO
    """
    return {
        'iss': 'https://pp.netseidbroker.dk/op',
        'nbf': 1632389572,
        'iat': 1632389572,
        'exp': 1632389872,
        'amr': ['code_app'],
        'mitid.uuid': '7ddb51e7-5a04-41f8-9f3c-eec1d9444979',
        'mitid.age': '55',
        'mitid.identity_name': 'Anker Andersen',
        'mitid.date_of_birth': '1966-02-03',
        'loa': 'https://data.gov.dk/concept/core/nsis/Substantial',
        'acr': 'https://data.gov.dk/concept/core/nsis/Substantial',
        'identity_type': 'private',
        'idp': 'mitid',
        'dk.cpr': '0302669597',
        'auth_time': '1632387312',
        'sub': 'ad845954-ed1d-4c73-846a-ef9b4c36f6f8',
        'aud': '0a775a87-878c-4b83-abe3-ee29c720c3e7',
        'transaction_id': 'a805f253-e8ea-4457-9996-c67bf704ab4a',
    }


@pytest.fixture(scope='function')
def userinfo_token_encoded(
        jwk_private: str,
        userinfo_token: Dict[str, Any],
) -> str:
    """
    TODO
    """
    token = jwt.encode(
        header={'alg': 'RS256'},
        payload=userinfo_token,
        key=jwk_private,
    )

    return token.decode()
