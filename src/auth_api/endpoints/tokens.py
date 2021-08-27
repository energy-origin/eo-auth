from energytt_platform.api import Endpoint, Context, Unauthorized

from ..db import db
from ..queries import TokenQuery


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
