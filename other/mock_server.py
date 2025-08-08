from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
import uvicorn
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-server")


@app.post("/api/v2/orderUpdate")
async def receive_order_update(
    request: Request,
    authorization: str = Header(default=None),
    content_type: str = Header(default=None),
):
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse JSON payload: {e}")
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid JSON"})

    logger.info(f"--- Incoming Request to /api/v2/orderUpdate ---")
    logger.info(f"Authorization Header: {authorization}")
    logger.info(f"Content-Type Header: {content_type}")
    logger.info("Payload:")
    logger.info(payload)

    return JSONResponse(content={"status": "success", "message": "Payload received", "data": payload})


@app.post("/api/v2/paymentUpdate")
async def receive_payment_update(
    request: Request,
    authorization: str = Header(default=None),
    content_type: str = Header(default=None),
):
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse payment JSON payload: {e}")
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid JSON"})

    logger.info(f"--- Incoming Request to /api/v2/paymentUpdate ---")
    logger.info(f"Authorization Header: {authorization}")
    logger.info(f"Content-Type Header: {content_type}")
    logger.info("Payload:")
    logger.info(payload)

    # Optional validation example
    required_keys = {"orderNo", "transactionNo", "paymentStatus", "traveller"}
    if not required_keys.issubset(payload.keys()):
        return JSONResponse(status_code=422, content={"status": "error", "message": "Missing required fields"})

    return JSONResponse(content={"status": "success", "message": "Payment update received", "data": payload})


if __name__ == "__main__":
    uvicorn.run("mock_server:app", host="0.0.0.0", port=8081, reload=True)
