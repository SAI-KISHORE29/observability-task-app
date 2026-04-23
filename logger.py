import logging
import logging_loki
from correlation import correlation_id_var

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.correlationId = correlation_id_var.get()
        return True

# Shared console handler for local terminal debugging
console_handler = logging.StreamHandler()
console_format = logging.Formatter('%(asctime)s [%(levelname)s] [%(correlationId)s] %(message)s')
console_handler.setFormatter(console_format)

# ==========================================
# 1. ORDER SERVICE LOGGER
# ==========================================
order_handler = logging_loki.LokiHandler(
    url="http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push",
    tags={"env": "development", "service": "order-service"},
    version="1",
)
order_handler.emitter.session.headers.update({"X-Scope-OrgID": "tenant1"})

order_logger = logging.getLogger("order-service")
order_logger.setLevel(logging.INFO)
order_logger.addHandler(order_handler)
order_logger.addFilter(CorrelationFilter())
order_logger.addHandler(console_handler)

# ==========================================
# 2. INVENTORY SERVICE LOGGER
# ==========================================
inventory_handler = logging_loki.LokiHandler(
    url="http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push",
    tags={"env": "development", "service": "inventory-service"},
    version="1",
)
inventory_handler.emitter.session.headers.update({"X-Scope-OrgID": "tenant1"})

inventory_logger = logging.getLogger("inventory-service")
inventory_logger.setLevel(logging.INFO)
inventory_logger.addHandler(inventory_handler)
inventory_logger.addFilter(CorrelationFilter())
inventory_logger.addHandler(console_handler)