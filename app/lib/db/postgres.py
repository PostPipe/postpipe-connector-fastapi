import os
import json
from typing import Any, Dict, List, Optional
# pyrefly: ignore [missing-import]
import asyncpg
from datetime import datetime
from .base import DatabaseAdapter

class PostgresAdapter(DatabaseAdapter):
    def __init__(self):
        self.default_url = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
        self._pool = None

    def _resolve_url(self, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        context = context or {}
        db_config = context.get("databaseConfig") or {}
        
        # In PostPipe, the frontend configuration passes 'uri' as the env variable name
        uri_key = db_config.get("uri") or db_config.get("url")
        if uri_key and os.environ.get(uri_key):
            return os.environ.get(uri_key)
            
        target = context.get("targetDb") or context.get("targetDatabase")
        if target:
            if os.environ.get(target): return os.environ.get(target)
            if os.environ.get(f"POSTGRES_URL_{target.upper()}"): return os.environ.get(f"POSTGRES_URL_{target.upper()}")
            if os.environ.get(f"DATABASE_URL_{target.upper()}"): return os.environ.get(f"DATABASE_URL_{target.upper()}")
            
        prefix = os.environ.get("POSTPIPE_VAR_PREFIX", "")
        if prefix:
            if os.environ.get(f"{prefix}_POSTGRES_URL"): return os.environ.get(f"{prefix}_POSTGRES_URL")
            if os.environ.get(f"{prefix}_DATABASE_URL"): return os.environ.get(f"{prefix}_DATABASE_URL")
            
        return self.default_url

    async def connect(self, context: Optional[Dict[str, Any]] = None) -> None:
        url = self._resolve_url(context)
        if not self._pool and url:
            self._pool = await asyncpg.create_pool(url)

    async def _ensure_table(self, table_name: str, context: Optional[Dict[str, Any]] = None):
        if not self._pool:
            await self.connect(context)
        if not self._pool:
            raise Exception("PostgreSQL connection URL not found. Please set POSTGRES_URL in your .env")
        async with self._pool.acquire() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    form_id VARCHAR(255) NOT NULL,
                    submission_id VARCHAR(255) UNIQUE NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    data JSONB,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """)

    def _get_table_name(self, context: Optional[Dict] = None) -> str:
        context = context or {}
        target = context.get("targetDb") or context.get("targetDatabase")
        if target and not target.lower().startswith(("postgres", "pg", "neon")):
            return target.replace("-", "_")
        return "postpipe_submissions"

    async def insert(self, submission: Dict[str, Any]) -> None:
        table = self._get_table_name(submission)
        await self._ensure_table(table, submission)
        
        ts_str = submission["timestamp"].replace('Z', '+00:00')
        ts_obj = datetime.fromisoformat(ts_str)
        
        async with self._pool.acquire() as conn:
            await conn.execute(f"""
                INSERT INTO {table} (form_id, submission_id, timestamp, data)
                VALUES ($1, $2, $3, $4)
            """, submission["formId"], submission["submissionId"], ts_obj, json.dumps(submission.get("data", {})))

    async def query(self, form_id: str, options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        options = options or {}
        table = self._get_table_name(options)
        await self._ensure_table(table, options)
        
        limit = options.get("limit", 50)
        page = max(1, options.get("page", 1))
        offset = (page - 1) * limit
        include_deleted = options.get("includeDeleted", False)
        
        query = f"SELECT * FROM {table} WHERE form_id = $1"
        if not include_deleted:
            query += " AND is_deleted = FALSE"
        query += " ORDER BY timestamp DESC LIMIT $2 OFFSET $3"
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, form_id, limit, offset)
            
        results = []
        for row in rows:
            results.append({
                "formId": row["form_id"],
                "submissionId": row["submission_id"],
                "timestamp": row["timestamp"].isoformat(),
                "data": json.loads(row["data"]) if row["data"] else {},
                "is_deleted": row["is_deleted"]
            })
        return results

    async def update_submission(self, form_id: str, submission_id: str, patch: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> bool:
        table = self._get_table_name(options)
        await self._ensure_table(table, options)
        
        async with self._pool.acquire() as conn:
            # Simple JSONB merge
            result = await conn.execute(f"""
                UPDATE {table} 
                SET data = data || $1::jsonb, updated_at = CURRENT_TIMESTAMP
                WHERE form_id = $2 AND submission_id = $3
            """, json.dumps(patch), form_id, submission_id)
            return result == "UPDATE 1"

    async def delete_submission(self, form_id: str, submission_id: str, hard: bool, options: Optional[Dict[str, Any]] = None) -> bool:
        table = self._get_table_name(options)
        await self._ensure_table(table, options)
        
        async with self._pool.acquire() as conn:
            if hard:
                result = await conn.execute(f"DELETE FROM {table} WHERE form_id = $1 AND submission_id = $2", form_id, submission_id)
            else:
                result = await conn.execute(f"UPDATE {table} SET is_deleted = TRUE WHERE form_id = $1 AND submission_id = $2", form_id, submission_id)
            return result.endswith("1")

    async def find_user_by_email(self, email: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
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
