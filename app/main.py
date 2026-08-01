from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routes.ingest import router as ingest_router
from app.routes.data import router as data_router
from app.routes.auth import router as auth_router
from app.routes.cdn import router as cdn_router
from app.routes.rbac import router as rbac_router
from app.routes.rbsc import router as rbsc_router

load_dotenv()

app = FastAPI(title="PostPipe FastAPI Connector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/postpipe")
app.include_router(data_router, prefix="/postpipe")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(cdn_router, prefix="/api/public/cdn")
app.include_router(rbac_router, prefix="/api/rbac")
app.include_router(rbsc_router, prefix="/postpipe/rbsc")

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "PostPipe FastAPI Connector",
        "version": "v1.0.0",
        "config": {
            "dbTypeDetected": os.environ.get("DB_TYPE", "InMemory"),
            "hasConnectorId": bool(os.environ.get("POSTPIPE_CONNECTOR_ID")),
            "mongoDetected": any(k.startswith("MONGODB_URI") for k in os.environ.keys()),
            "pgDetected": any(k.startswith("POSTGRES_URL") or k.startswith("DATABASE_URL") for k in os.environ.keys())
        }
    }
