import logging
import logging_loki
from correlation import correlation_id_var

# Set up the Loki handler
handler = logging_loki.LokiHandler(
    url="http://loki-gateway.loki.svc.cluster.local/loki/api/v1/push",
    tags={"env": "development", "service": "order-services"},
    version="1",
)

# inventory/logger.py
handler = logging_loki.LokiHandler(
    url="http://loki-gateway.loki.svc.cluster.local/loki/api/v1/push",
    tags={"env": "development", "service": "inventory-service"},
    version="1",
)

# Inject multi-tenancy header into the underlying requests session
handler.emitter.session.headers.update({"X-Scope-OrgID": "tenant1"})

class CorrelationFilter(logging.Filter):
    """Injects the correlation ID into every log record."""
    def filter(self, record):
        record.correlationId = correlation_id_var.get()
        return True

# Configure logger
logger = logging.getLogger("order-services")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addFilter(CorrelationFilter())

# Fallback console logger for local development
console_handler = logging.StreamHandler()
console_format = logging.Formatter('%(asctime)s [%(levelname)s] [%(correlationId)s] %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)