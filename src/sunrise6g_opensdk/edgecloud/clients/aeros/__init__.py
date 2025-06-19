"""
aerOS client
  This module provides a client for interacting with the aerOS REST API.
  It includes methods for onboarding/deploying applications,
    and querying aerOS continuum entities
  aerOS domain is exposed as zones
  aerOS services and service components are exposed as applications
  Client is initialized with a base URL for the aerOS API
    and an access token for authentication.
"""

from sunrise6g_opensdk.edgecloud.clients.aeros import config
from sunrise6g_opensdk.logger import setup_logger

logger = setup_logger(__name__, is_debug=True, file_name=config.LOG_FILE)

# TODO: The following should only appear in case aerOS client is used
#       Currently even if another client is used, the logs appear
# logger.info("aerOS client initialized")
# logger.debug("aerOS API URL: %s", config.aerOS_API_URL)
# logger.debug("aerOS access token: %s", config.aerOS_ACCESS_TOKEN)
# logger.debug("aerOS debug mode: %s", config.DEBUG)
# logger.debug("aerOS log file: %s", config.LOG_FILE)
