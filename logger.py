import os
import logging
import json
from correlation import correlation_id_var

SERVICE_NAME = os.getenv("SERVICE_NAME", "order-service").lower().replace(" ", "-")

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "service_name": SERVICE_NAME,
            "correlationId": correlation_id_var.get(),
        })

handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())

app_logger = logging.getLogger(SERVICE_NAME)
app_logger.setLevel(logging.INFO)
app_logger.addHandler(handler)
app_logger.propagate = False