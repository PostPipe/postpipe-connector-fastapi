from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional
from app.lib.security import verify_jwt
from app.lib.config import get_prefixed_env
from app.lib.db import get_adapter
import json

router = APIRouter()

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    auth_cookie = request.cookies.get("pp_auth_token")
    
    token = auth_cookie
    if not token and auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: Token missing")
        
    secret = get_prefixed_env("POSTPIPE_CONNECTOR_SECRET") or get_prefixed_env("JWT_SECRET")
    user = verify_jwt(token, secret)
    if user:
        return user
        
    # Legacy secret fallback check
    if token == secret:
        return {"role": "admin"}
        
    raise HTTPException(status_code=403, detail="Forbidden: Invalid Token")

@router.get("/data")
async def get_data(request: Request, formId: str, limit: int = 50, page: int = 1, targetDatabase: Optional[str] = None, databaseConfig: Optional[str] = None, includeDeleted: Optional[str] = None, filter: Optional[str] = None, user = Depends(get_current_user)):
    db_config_parsed = None
    if databaseConfig:
        try:
            db_config_parsed = json.loads(databaseConfig)
        except:
            pass
            
    filter_parsed = None
    if filter:
        try:
            filter_parsed = json.loads(filter)
        except:
            pass

    adapter = get_adapter(db_config_parsed.get("type") if db_config_parsed else None)
    
    data = await adapter.query(formId, {
        "limit": limit,
        "page": page,
        "targetDatabase": targetDatabase,
        "databaseConfig": db_config_parsed,
        "includeDeleted": includeDeleted == "true",
        "filter": filter_parsed
    })
    
    return {"success": True, "count": len(data), "data": data}
