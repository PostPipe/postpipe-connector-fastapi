import os
from fastapi import Request
from fastapi.responses import JSONResponse
from postpipe_connector_core.main import create_postpipe_app

app = create_postpipe_app()




if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
