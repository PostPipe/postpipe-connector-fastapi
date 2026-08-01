# PostPipe FastAPI Connector

This is a self-hosted connector for [PostPipe](https://postpipe.in) built in Python (FastAPI).
It acts as a secure bridge between PostPipe's Ingest API and your private database.

## 🚀 Getting Started

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and fill in your details:

```env
POSTPIPE_CONNECTOR_ID=pp_conn_...
JWT_SECRET=...                  # Keep this secret!
DB_TYPE=mongodb                 # mongodb | postgres
```

### 3. Run Locally

```bash
uvicorn app.main:app --reload --port 3000
```

The server will listen on port 3000.
Endpoint: `POST http://localhost:3000/postpipe/ingest`
