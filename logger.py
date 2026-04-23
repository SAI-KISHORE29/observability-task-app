import os
import logging
import logging_loki
from correlation import correlation_id_var

# Format the service name for Loki tags (e.g., "Order Service" -> "order-service")
APP_NAME = os.getenv("SERVICE_NAME", "Order Service")
LOKI_SERVICE_TAG = APP_NAME.lower().replace(" ", "-")

# Set up ONE dynamic Loki handler
handler = logging_loki.LokiHandler(
    url="http://loki.monitoring.svc.cluster.local:3100/loki/api/v1/push",
    tags={"env": "development", "service": LOKI_SERVICE_TAG},
    version="1",
)

handler.emitter.session.headers.update({"X-Scope-OrgID": "tenant1"})

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.correlationId = correlation_id_var.get()
        return True

# Configure logger dynamically
logger = logging.getLogger(LOKI_SERVICE_TAG)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addFilter(CorrelationFilter())

console_handler = logging.StreamHandler()
console_format = logging.Formatter('%(asctime)s [%(levelname)s] [%(correlationId)s] %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)