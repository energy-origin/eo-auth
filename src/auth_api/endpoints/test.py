import logging

from origin.api import Endpoint


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s - %(extra)s')  # noqa: E501

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)


class TestLogging(Endpoint):
    def handle_request(self):
        """
        Handle HTTP request.
        """
        extra = {
            "service": "auth-api",
            "something": {
                "foo": "bar",
                "spam": [1, 2, 3, 4],
            },
        }

        logger.error(
            "Something happened",
            extra={"extra": extra},
        )


class TestLoggingException(Endpoint):
    def handle_request(self):
        """
        Handle HTTP request.
        """
        extra = {
            "service": "auth-api",
            "something": {
                "foo": "bar",
                "spam": [1, 2, 3, 4],
            },
        }

        try:
            0/0
        except Exception as e:
            logger.exception(
                "Something happened",
                extra={"extra": extra},
            )
