import os
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from postpipe_connector_core.main import create_postpipe_app
from postpipe_connector_core.lib.db.postgres import PostgresAdapter

original_insert = PostgresAdapter.insert

async def patched_insert(self, submission: dict) -> None:
    ts_val = submission.get("timestamp")
    if isinstance(ts_val, str):
        try:
            submission["timestamp"] = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
        except ValueError:
            submission["timestamp"] = datetime.now(timezone.utc)
    elif not isinstance(ts_val, datetime):
        submission["timestamp"] = datetime.now(timezone.utc)
        
    return await original_insert(self, submission)

PostgresAdapter.insert = patched_insert

app = create_postpipe_app()




if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
