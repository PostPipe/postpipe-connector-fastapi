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

## ⚡ Deployment on Vercel

The connector is configured to be deployed to Vercel as a Serverless Function out-of-the-box using the provided `vercel.json`.

### Steps:

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Deploy via Vercel CLI**:
   Navigate to the `static-system/my-connector-fastapi` directory and run:
   ```bash
   vercel
   ```
   Follow the prompts to link the project and deploy it.

3. **Configure Environment Variables**:
   In your Vercel Dashboard (Project Settings > Environment Variables), add the required environment variables:
   - `POSTPIPE_CONNECTOR_ID`
   - `JWT_SECRET`
   - `DB_TYPE` (`mongodb` or `postgres`)
   - `DATABASE_URL` / `MONGODB_URI` (depending on your database type)
   - Any other env variables used by your selected database adapter.

4. **Deploy to Production**:
   Once configured, deploy to production:
   ```bash
   vercel --prod
   ```

Alternatively, you can import the repository directly into Vercel via the dashboard. Make sure to set the **Root Directory** to `static-system/my-connector-fastapi`.
