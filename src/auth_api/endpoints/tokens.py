from energytt_platform.api import Endpoint, Context, Unauthorized


class ForwardAuth(Endpoint):
    """
    Mocked ForwardAuth endpoint for Træfik.
    """
    def handle_request(self, context: Context):
        """
        Handle HTTP request.
        """
        if context.raw_token != '123':
            raise Unauthorized('Bad token! Maybe try "123" instead?')
