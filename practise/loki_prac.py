import logging
import logging_loki
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

handler = logging_loki.LokiHandler(
    url="http://localhost:3100/loki/api/v1/push",
    tags={"application": "my_app"},
    version="1"
)
logger.addHandler(handler)
logger.info("Hello Loki! This is a test log.")
logger.error("Something went wrong!")
