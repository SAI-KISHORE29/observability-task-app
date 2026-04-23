import os
import time
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

# Import both loggers from our new logger.py
from logger import order_logger, inventory_logger
from correlation import CorrelationIdMiddleware

# --- HARDCODED SELECTION ---
APP_NAME = os.getenv("SERVICE_NAME", "Order Service")

# Pick the correct logger based on the deployment
if APP_NAME == "Inventory Service":
    logger = inventory_logger
else:
    logger = order_logger

app = FastAPI(title=APP_NAME)
Instrumentator().instrument(app).expose(app)

# Add Middlewares
app.add_middleware(CorrelationIdMiddleware)

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Pino-style request logging middleware"""
    try:
        response = await call_next(request)
        logger.info(
            "request_completed", 
            extra={"tags": {"req_method": request.method, "req_url": str(request.url)}}
        )
        return response
    except Exception as e:
        logger.error(f"request_error: {str(e)}", exc_info=True)
        raise

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("validation_failed", extra={"tags": {"payload": "invalid"}})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid payload"}
    )

# --- Models ---
class OrderCreate(BaseModel):
    customer: str
    items: List[str]

class OrderUpdate(BaseModel):
    status: str

# In-memory DB
orders: Dict[str, Any] = {}

# --- Routes ---
@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate):
    order_id = f"ord_{int(time.time() * 1000)}"
    new_order = {
        "id": order_id,
        "customer": order.customer,
        "items": order.items,
        "status": "CREATED",
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    orders[order_id] = new_order
    logger.info("order_created", extra={"tags": {"orderId": order_id}})
    return new_order

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = orders.get(order_id)
    if not order:
        logger.warning("order_not_found", extra={"tags": {"orderId": order_id}})
        raise HTTPException(status_code=404, detail="Order not found")
    logger.info("order_fetched", extra={"tags": {"orderId": order_id}})
    return order

@app.patch("/orders/{order_id}")
async def update_order(order_id: str, order_update: OrderUpdate):
    order = orders.get(order_id)
    if not order:
        logger.warning("order_not_found", extra={"tags": {"orderId": order_id}})
        raise HTTPException(status_code=404, detail="Order not found")
    order["status"] = order_update.status
    logger.info("order_updated", extra={"tags": {"orderId": order_id, "newStatus": order_update.status}})
    return order

@app.get("/simulate-error")
async def simulate_error():
    try:
        raise Exception("Simulated internal failure")
    except Exception as e:
        logger.error("internal_error", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal error"}
        )

@app.get("/")
async def root():
    # Dynamically return the name of the service running
    return JSONResponse(content=f"{APP_NAME} is running as expected.")

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 3000))
    logger.info(f"{APP_NAME} running at http://localhost:{PORT}")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)