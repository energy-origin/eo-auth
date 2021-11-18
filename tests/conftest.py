"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import sys

from os.path import dirname as d
from os.path import abspath, join

# Adds the src folder to the local path
root_dir = join(d(d(abspath(__file__))), 'src')
sys.path.append(root_dir)

# # -- SQL Continue normal import

import pytest
from unittest.mock import patch
from testcontainers.postgres import PostgresContainer

from origin.sql import SqlEngine, POSTGRES_VERSION

from auth_api.db import db as _db


# # -- SQL ---------------------------------------------------------------------


@pytest.fixture(scope='function')
def psql_uri():
    """
    TODO
    """
    image = f'postgres:{POSTGRES_VERSION}'

    with PostgresContainer(image) as psql:
        yield psql.get_connection_url()


@pytest.fixture(scope='function')
def db(psql_uri: str) -> SqlEngine:
    """
    TODO
    """
    with patch('auth_api.db.db.uri', new=psql_uri):
        yield _db


@pytest.fixture(scope='function')
def mock_session(db: SqlEngine) -> SqlEngine.Session:
    """
    TODO
    """
    db.apply_schema()

    with db.make_session() as session:
        yield session

