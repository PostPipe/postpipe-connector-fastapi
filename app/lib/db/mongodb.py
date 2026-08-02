import os
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from .base import DatabaseAdapter
from bson import ObjectId

_connection_pool: Dict[str, AsyncIOMotorClient] = {}

class MongoAdapter(DatabaseAdapter):
    def __init__(self):
        self.default_uri = os.environ.get("MONGODB_URI", "")
        self.default_db_name = os.environ.get("MONGODB_DB_NAME", "postpipe")
        self.collection_name = os.environ.get("MONGODB_COLLECTION", "submissions")

    def _resolve_uri(self, target_name: Optional[str], database_config: Optional[Dict] = None) -> Optional[str]:
        if database_config and database_config.get("uri"):
            env_var_name = database_config["uri"]
            uri = os.environ.get(env_var_name)
            if uri:
                return uri

        if target_name and os.environ.get(target_name):
            return os.environ.get(target_name)

        if target_name:
            dynamic_key = f"MONGODB_URI_{target_name.upper()}"
            dynamic_uri = os.environ.get(dynamic_key)
            if dynamic_uri:
                return dynamic_uri

        prefix = os.environ.get("POSTPIPE_VAR_PREFIX", "")
        if prefix:
            prefixed = os.environ.get(f"{prefix}_MONGODB_URI")
            if prefixed:
                return prefixed

        if self.default_uri:
            return self.default_uri

        # Fallback
        for k, v in os.environ.items():
            if k.startswith("MONGODB_URI_") and v:
                return v

        return None

    def _get_target_config(self, payload: Optional[Dict] = None) -> Dict[str, str]:
        payload = payload or {}
        target_name = payload.get("targetDb") or payload.get("targetDatabase")
        db_config = payload.get("databaseConfig")

        uri = self._resolve_uri(target_name, db_config) or ""
        db_name = self.default_db_name

        if db_config and db_config.get("dbName"):
            db_name = db_config["dbName"]
        elif target_name and not any(k in target_name.lower() for k in ['url', 'uri', 'mongodb', 'atlas', 'database']):
            db_name = target_name

        return {"uri": uri, "dbName": db_name}

    async def _get_client(self, uri: str) -> AsyncIOMotorClient:
        if uri in _connection_pool:
            return _connection_pool[uri]

        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=10000)
        _connection_pool[uri] = client
        return client

    async def connect(self, context: Optional[Dict[str, Any]] = None) -> None:
        pass # Client is initialized dynamically

    async def insert(self, submission: Dict[str, Any]) -> None:
        config = self._get_target_config(submission)
        if not config["uri"]:
            raise Exception("MongoDB URI not found")
            
        client = await self._get_client(config["uri"])
        db = client[config["dbName"]]
        col = db[self.collection_name]
        
        await col.insert_one(submission)

    async def query(self, form_id: str, options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        options = options or {}
        config = self._get_target_config(options)
        if not config["uri"]:
            raise Exception("MongoDB URI not found")
            
        client = await self._get_client(config["uri"])
        db = client[config["dbName"]]
        col = db[self.collection_name]
        
        limit = options.get("limit", 50)
        page = max(1, options.get("page", 1))
        skip = (page - 1) * limit
        
        match_query = {"formId": form_id}
        if not options.get("includeDeleted"):
            match_query["is_deleted"] = {"$ne": True}
            
        cursor = col.find(match_query).sort("timestamp", -1).skip(skip).limit(limit)
        docs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            docs.append(doc)
            
        return docs

    async def update_submission(self, form_id: str, submission_id: str, patch: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> bool:
        config = self._get_target_config(options)
        if not config["uri"]:
            return False
            
        client = await self._get_client(config["uri"])
        db = client[config["dbName"]]
        col = db[self.collection_name]
        
        result = await col.update_one(
            {"formId": form_id, "submissionId": submission_id},
            {"$set": {"data": patch, "updated_at": patch.get("updated_at")}} # Simplified patch mapping
        )
        return result.modified_count > 0

    async def delete_submission(self, form_id: str, submission_id: str, hard: bool, options: Optional[Dict[str, Any]] = None) -> bool:
        config = self._get_target_config(options)
        if not config["uri"]:
            return False
            
        client = await self._get_client(config["uri"])
        db = client[config["dbName"]]
        col = db[self.collection_name]
        
        if hard:
            result = await col.delete_one({"formId": form_id, "submissionId": submission_id})
            return result.deleted_count > 0
        else:
            result = await col.update_one(
                {"formId": form_id, "submissionId": submission_id},
                {"$set": {"is_deleted": True}}
            )
            return result.modified_count > 0

    async def find_user_by_email(self, email: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        # Simplified user auth mock
        pass
    
    async def insert_user(self, user: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> None:
        pass
        
    async def update_user_last_login(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass
        
    async def update_user_password(self, user_id: str, new_password_hash: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass
        
    async def verify_user_email(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass
        
    async def update_user_otp(self, user_id: str, otp: str, expires_at: Any, context: Optional[Dict[str, Any]] = None) -> None:
        pass
