# logger.py
import os, logging, logging_loki
from correlation import correlation_id_var

LOKI_URL = "http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push"
SERVICE_NAME = os.getenv("SERVICE_NAME", "order-service").lower().replace(" ", "-")

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.correlationId = correlation_id_var.get()
        return True

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] [%(correlationId)s] %(message)s')
)

loki_handler = logging_loki.LokiHandler(
    url=LOKI_URL,
    tags={"env": "development", "service_name": SERVICE_NAME},  # ← service_name key
    version="1",
)
loki_handler.emitter.session.headers.update({"X-Scope-OrgID": "tenant1"})

app_logger = logging.getLogger(SERVICE_NAME)
app_logger.setLevel(logging.INFO)
app_logger.addHandler(loki_handler)
app_logger.addHandler(console_handler)
app_logger.addFilter(CorrelationFilter())