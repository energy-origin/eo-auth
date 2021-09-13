"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import pytest
from unittest.mock import patch
from testcontainers.postgres import PostgresContainer

from auth_api.app import create_app
from auth_shared.db import db


@pytest.fixture(scope='class')
def session():
    """
    TODO
    """
    import time
    with PostgresContainer('postgres:13.4') as psql:
        with patch('auth_shared.db.db.uri', new=psql.get_connection_url()):

            # Apply migrations
            db.ModelBase.metadata.create_all(db.engine)

            # Create session
            with db.session_class() as session:
                yield session
    # time.sleep(15)


@pytest.fixture(scope='module')
def client():
    """
    TODO
    """
    # client = create_app().test_client
    # client.
    yield create_app().test_client
