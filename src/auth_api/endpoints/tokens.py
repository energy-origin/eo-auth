from typing import List, Optional
from dataclasses import dataclass, field

from energytt_platform.models.auth import InternalToken
from energytt_platform.api import Endpoint, Context, Unauthorized
from energytt_platform.tokens import TokenEncoder

from auth_shared.config import TOKEN_SECRET
from auth_shared.db import db
from auth_shared.queries import TokenQuery


class ForwardAuth(Endpoint):
    """
    Mocked ForwardAuth endpoint for Træfik.
    """

    @db.session()
    def handle_request(self, context: Context, session: db.Session):
        """
        Handle HTTP request.
        """
        token = TokenQuery(session) \
            .has_opaque_token(context.raw_token) \
            .one_or_none()

        if token is None:
            raise Unauthorized('Bad token! Maybe try "123" instead?')

        if context.raw_token != '123':
            raise Unauthorized('Bad token! Maybe try "123" instead?')


class CreateTestToken(Endpoint):
    """
    Creates a new token (for testing purposes).
    """

    @dataclass
    class Request:
        token: InternalToken

    @dataclass
    class Response:
        token: str

    def handle_request(
            self,
            request: Request,
            context: Context,
    ):
        """
        Handle HTTP request.
        """
        encoder = TokenEncoder(
            schema=InternalToken,
            secret=TOKEN_SECRET,
        )

        return self.Response(
            token=encoder.encode(request.token),
        )
