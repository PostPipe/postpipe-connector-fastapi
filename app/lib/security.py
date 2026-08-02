import hmac
import hashlib
from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
import jwt
from typing import Optional, Dict, Any

def verify_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    if not signature or not secret or not raw_body:
        return False
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

def validate_timestamp(timestamp: str, max_age_ms: int = 5 * 60 * 1000) -> bool:
    try:
        # Handle ISO-8601 with or without Z
        ts_str = timestamp.replace('Z', '+00:00')
        ts = datetime.fromisoformat(ts_str).timestamp() * 1000
        now = datetime.now(timezone.utc).timestamp() * 1000
        return (now - ts) <= max_age_ms
    except Exception:
        return False

def validate_payload_ids(payload: dict) -> bool:
    return bool(payload and payload.get('formId') and payload.get('submissionId') and payload.get('timestamp'))

def verify_jwt(token: str, secret: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except Exception:
        return None
