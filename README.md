# Project Origin AccountService

This is the repository for the Auth-domain - a part of [Energy Track and Trace](https://github.com/Energy-Track-and-Trace).

This domain is responsible for:

- Authenticating users via OpenID Connect
- Issue authorization tokens to clients


# Installation and running locally

The following sections describes how to install and run the project locally for development and debugging.


## Requirements

- Python 3.8+
- Pipenv
- A PostgreSQL server with one database


### First time installation


Initially, make sure to define necessary environment variables (listed below).
You can define them in the .env file in the root of the project
([more details on this here](https://pipenv-fork.readthedocs.io/en/latest/advanced.html#automatic-loading-of-env)).

Also, make sure to upgrade your system packages for good measure:
   
    pip install --upgrade --user setuptools pip pipenv

Then install project dependencies:

    pipenv install

Then apply database migrations:

    cd src/migrations
    pipenv run migrate
    cd ../../

### Running locally (development)

This starts the local development server (NOT for production use):

    pipenv run develop

### Running tests

Run unit- and integration tests:

    pipenv run pytest


## Environment variables

Name | Description | Example
:--- | :--- | :--- |
`DEBUG` | Whether or not to enable debugging mode (off by default) | `0` or `1`
`SERVICE_URL` | Public URL to this service without trailing slash | `https://account.projectorigin.dk`
**Secrets & Keys:** | |
`INTERNAL_TOKEN_SECRET` | Secret to sign and verify internal tokens | `something-secret`
`SSN_ENCRYPTION_KEY` | Key en encrypt social security numbers | `something-secret`
**SQL:** | |
`SQL_URI` | Database connection string for SQLAlchemy | `postgresql://scott:tiger@localhost/mydatabase`
`SQL_POOL_SIZE` | Connection pool size per container | `10`
**OpenID Connect:** | |
`OIDC_CLIENT_ID` | OpenID Connect client ID | 
`OIDC_CLIENT_SECRET` | OpenID Connect client secret | 
`OIDC_LOGIN_URL` | OpenID Connect login endpoint URL | 
`OIDC_LOGOUT_URL` | OpenID Connect logout endpoint URL | 
`OIDC_TOKEN_URL` | OpenID Connect token endpoint URL | 
`OIDC_JWKS_URL` | OpenID Connect JWKS endpoint URL | 


## Building container image

    docker build -f Dockerfile -t account-service:v1 .

## Running container images

Web API:

    docker run --entrypoint /app/entrypoint.web.sh account-service:v1

Worker:

    docker run --entrypoint /app/entrypoint.worker.sh account-service:v1

Worker Beat:

    docker run --entrypoint /app/entrypoint.beat.sh account-service:v1

# System architecture

The following diagram depicts the overall architecture of AccountService and its dependencies. A few key points are listed below the diagram.

![alt text](doc/AccountService.png)

- It exposes a web API using OAuth2 authentication.
- It has one asynchronous worker running its own process (container).
- The web API process starts asynchronous tasks by submitting them to a distributed queue using Redis.
- A Beat process kicks off periodic tasks.


# 3rd party libraries

This project uses the following 3rd party libraries:

- [Flask](https://flask.palletsprojects.com/en/1.1.x/): HTTP framework
- [SQLAlchemy](https://www.sqlalchemy.org/): Database ORM
- [Alembic](https://alembic.sqlalchemy.org/en/latest/): Database migrations and revisioning
- [Marshmallow](https://marshmallow.readthedocs.io/en/stable/): JSON serialization/deserialization and validation
- [Celery](https://docs.celeryproject.org/): Asynchronous tasks
- [Redis](https://pypi.org/project/redis/): Celery backend + caching
- [OpenCensus](https://github.com/census-instrumentation/opencensus-python): Logging and tracing
- [Authlib](https://docs.authlib.org): OAuth2 implementation
- [Origin-Ledger-SDK](https://pypi.org/project/Origin-Ledger-SDK/): Interface with the blockchain ledger
- [bip32utils](https://github.com/lyndsysimon/bip32utils/): Generating block keys for the ledger
- [pytest](https://docs.pytest.org/): Testing
