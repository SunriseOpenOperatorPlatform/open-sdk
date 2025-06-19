##
# This file is part of the Open SDK
#
# Contributors:
#   - Vasilis Pitsilis (vpitsilis@dat.demokritos.gr, vpitsilis@iit.demokritos.gr)
#   - Andreas Sakellaropoulos (asakellaropoulos@iit.demokritos.gr)
##
"""
Docstring
"""
from requests.exceptions import HTTPError, RequestException, Timeout

import sunrise6g_opensdk.edgecloud.clients.aeros.config as config
from sunrise6g_opensdk.logger import setup_logger


def catch_requests_exceptions(func):
    """
    Docstring
    """
    logger = setup_logger(__name__, is_debug=True, file_name=config.LOG_FILE)

    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except HTTPError as e:
            logger.info("4xx or 5xx: %s \n", {e})
            return None  # raise our custom exception or log, etc.
        except ConnectionError as e:
            logger.info(
                "Raised for connection-related issues (e.g., DNS resolution failure, network issues): %s \n",
                {e},
            )
            return None  # raise our custom exception or log, etc.
        except Timeout as e:
            logger.info("Timeout occured: %s \n", {e})
            return None  # raise our custom exception or log, etc.
        except RequestException as e:
            logger.info("Request failed: %s \n", {e})
            return None  # raise our custom exception or log, etc.

    return wrapper
