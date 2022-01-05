import logging

from origin.logs import JsonFormatter

from .config import SERVICE_NAME


formatter = JsonFormatter(service=SERVICE_NAME)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

# logger = logging.getLogger(__name__)
# logger.addHandler(handler)
# logger.setLevel(LOG_LEVEL)
