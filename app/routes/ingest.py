from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
from app.lib.security import verify_signature, validate_timestamp, validate_payload_ids
from app.lib.config import get_prefixed_env
from app.lib.db import get_adapter
import hashlib
import hmac

router = APIRouter()

@router.post("/ingest")
async def ingest_data(request: Request):
    raw_body = await request.body()
    if not raw_body:
        raise HTTPException(status_code=400, detail="Payload missing")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    signature = request.headers.get("x-postpipe-signature", "")
    
    # Validation
    if not validate_payload_ids(payload):
        raise HTTPException(status_code=400, detail="Invalid Payload Structure")
        
    if not validate_timestamp(payload.get("timestamp")):
        raise HTTPException(status_code=401, detail="Request Expired")

    connector_secret = get_prefixed_env("POSTPIPE_CONNECTOR_SECRET") or get_prefixed_env("JWT_SECRET")
    if not connector_secret:
        raise HTTPException(status_code=500, detail="Server missing connector secret")

    if not verify_signature(raw_body, signature, connector_secret):
        raise HTTPException(status_code=401, detail="Invalid Signature")

    # Transformation & Routing
    routing = payload.get("routing", {})
    
    # Masking/Hashing logic (similar to TS version)
    if routing and routing.get("transformations"):
        transformations = routing["transformations"]
        data = payload.get("data", {})
        if "mask" in transformations:
            for field in transformations["mask"]:
                if field in data:
                    val = str(data[field])
                    visible = val[-4:]
                    data[field] = "*" * max(0, len(val) - 4) + visible
        if "hash" in transformations:
            for field in transformations["hash"]:
                if field in data:
                    data[field] = hashlib.sha256(str(data[field]).encode()).hexdigest()
        payload["data"] = data

    try:
        db_config = payload.get("databaseConfig") or {}
        adapter = get_adapter(db_config.get("type"))
        await adapter.insert(payload)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok", "stored": True}
