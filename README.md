# Auth

This is the repository for the Auth-domain - a part of [Project Energy Track and Trace](https://github.com/Energy-Track-and-Trace).

This domain is responsible for:

- Authenticating users via OpenID Connect
- Issuing authorization-tokens to clients
- Translating opaque tokens to internal tokens (via a Træfik ForwardAuth endpoint)


# Content

- Building and running the services
    - Requirements
    - Installation and running locally
    - Building and running Docker images
    - Running tests
    - Environment variables
- Architecture and implementation
- Database and migrations

# Installation and running locally (for development)

The following sections describes how to install and run the project locally for development and debugging.


## Requirements

- Python 3.8+
- Pipenv
- An SQL server with one database created in advance (PostgreSQL, MSSQL, MySQL, etc.)


### First time installation

Make sure to upgrade your system packages for good measure:
   
    pip install --upgrade --user setuptools pip pipenv

Then install project dependencies:

    pipenv update --dev

Define necessary environment variables (listed below).
You can define them in the .env file in the root of the project
([more details on this here](https://pipenv-fork.readthedocs.io/en/latest/advanced.html#automatic-loading-of-env)).

    SERVICE_URL=http://127.0.0.1:9096
    INTERNAL_TOKEN_SECRET=12345
    SSN_ENCRYPTION_KEY=54321
    TOKEN_COOKIE_DOMAIN=127.0.0.1
    SQL_URI=postgresql://postgres:1234@localhost:5432/auth
    SQL_POOL_SIZE=1
    OIDC_CLIENT_ID=<OpenID Connect Client ID>
    OIDC_CLIENT_SECRET=<OpenID Connect Client secret>
    OIDC_AUTHORITY_URL=<OpenID Connect authority URL>

Navigate to the source directory:

    cd src/

Apply database migrations:

    pipenv run alembic --config=migrations/alembic.ini upgrade head

### Running API service locally (for development)

Start the local development server (NOT for production use):

    pipenv run python -m auth_api

### Running tests

Run unit- and integration tests:

    pipenv run python -m pytest ../tests/


# Environment variables

Name | Description | Example
:--- | :--- | :--- |
`DEBUG` | Whether or not to enable debugging mode (off by default) | `True``True` or `False`
`SERVICE_URL` | Public URL to this service without trailing slash | `https://project.com/api/auth`
**Tokens, Secrets, and Keys:** | |
`TOKEN_COOKIE_DOMAIN` | The domain to set cookie on (Bearer token) | `project.com`
`INTERNAL_TOKEN_SECRET` | Secret to sign and verify internal tokens | `something-secret`
`SSN_ENCRYPTION_KEY` | Key en encrypt social security numbers | `something-secret`
**SQL:** | |
`SQL_URI` | Database connection string for SQLAlchemy | `postgresql://scott:tiger@localhost/mydatabase`
`SQL_POOL_SIZE` | Connection pool size per container | `10`
**OpenID Connect:** | |
`OIDC_CLIENT_ID` | OpenID Connect client ID | 
`OIDC_CLIENT_SECRET` | OpenID Connect client secret | 
`OIDC_AUTHORITY_URL` | OpenID Connect authority URL | 


# Building and running production-ready Docker image

All microservices in a single domain are build into a single Docker image
with multiple entrypoints.

## Building Docker image

    docker build -t auth:v1 .

## Running container images

Web API:

    docker run --entrypoint /app/entrypoint_api.sh auth:v1


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
