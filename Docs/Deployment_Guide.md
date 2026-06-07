# Deployment Guide

## Overview

exHacker can be deployed using a variety of free and paid platforms. This guide covers options for each service layer and provides step-by-step instructions.

| Layer | Free Options | Paid Options |
|-------|-------------|--------------|
| Backend API | Railway, Render, Fly.io, Northflank | AWS ECS, GCP Cloud Run, Azure App Service, DigitalOcean App Platform |
| Frontend | Vercel, Netlify, Cloudflare Pages | Vercel Pro, Netlify Pro |
| Database | Supabase, Neon, Railway Postgres | AWS RDS, DigitalOcean Managed Postgres |
| Vector DB | Qdrant Cloud (free tier), Chroma | Qdrant Cloud (paid), Pinecone |
| Monitoring | BetterStack (free tier) | Grafana Cloud, Datadog |

---

## Backend Deployment

### Railway (Free)

Railway offers a generous free tier with $5 of monthly credits — enough for a small application.

**Setup:**

1. Create an account at https://railway.com
2. Install the Railway CLI:
   ```bash
   # macOS / Linux
   curl -fsSL https://railway.app/install.sh | sh

   # Windows (PowerShell)
   irm https://railway.app/install.ps1 | iex
   ```
3. Login and link your project:
   ```bash
   railway login
   railway init
   ```
4. Configure the service:
   ```bash
   # Set root directory to backend
   railway service --name exhacker-backend
   ```
5. Set environment variables:
   ```bash
   railway env set ENVIRONMENT=production
   railway env set DATABASE_URL=<your-supabase-or-neon-url>
   railway env set DATABASE_SYNC_URL=<your-sync-url>
   railway env set CORS_ORIGINS=["https://your-frontend.vercel.app"]
   railway env set LLM_PROVIDER=auto
   railway env set OPENAI_API_KEY=<key>
   railway env set XAI_API_KEY=<key>
   railway env set GEMINI_API_KEY=<key>
   ```
6. Deploy:
   ```bash
   railway up
   ```
7. (Optional) Configure a custom domain in the Railway dashboard.

**Railway Free Tier Limits:**
- $5 credit/month (enough for ~500 hours of a small container)
- 500 MB RAM
- Shared CPU
- 1 GB disk
- Automatic sleep after inactivity

---

### Render (Free)

Render's free tier web services spin down after inactivity.

**Setup:**

1. Create an account at https://render.com
2. Create a **New Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -e ".[dev]"`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Add environment variables (same as Railway above)
6. Click **Create Web Service**

**Render Free Tier Limits:**
- 512 MB RAM
- 0.1 CPU
- Auto-spins down after 15 minutes of inactivity
- 750 hours/month
- Limited to 1 web service + 1 PostgreSQL (if using Render DB)

---

### Fly.io (Free with card)

Fly.io requires a credit card but offers a free allowance.

**Setup:**

1. Install the Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```
2. Login:
   ```bash
   fly auth login
   ```
3. Create configuration:
   ```bash
   cd backend
   fly launch --no-deploy
   ```
4. Configure `fly.toml` (created by `fly launch`):
   ```toml
   [build]
     docker = "Dockerfile"

   [env]
     ENVIRONMENT = "production"

   [[services]]
     http_checks = []
     internal_port = 8000
     processes = ["app"]
     protocol = "tcp"
     script_checks = []

     [[services.ports]]
       handlers = ["http"]
       port = 80
       force_https = true

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```
5. Set secrets:
   ```bash
   fly secrets set DATABASE_URL=<url> OPENAI_API_KEY=<key> CORS_ORIGINS=<origins>
   ```
6. Deploy:
   ```bash
   fly deploy
   ```

**Fly.io Free Tier:**
- Up to 3 shared-CPU VMs
- 256 MB RAM per VM
- 3 GB persistent volume storage
- 160 GB outbound data transfer/month

---

### Northflank (Free)

1. Create an account at https://northflank.com
2. Create a new **Service** from your Git repository
3. Set **Dockerfile Path** to `backend/Dockerfile`
4. Configure port to `8000`
5. Add environment variables
6. Deploy

---

### AWS ECS (Paid)

**Setup:**

1. Push the Docker image to Amazon ECR:
   ```bash
   aws ecr create-repository --repository-name exhacker-backend
   docker tag exhacker-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/exhacker-backend:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/exhacker-backend:latest
   ```
2. Create an ECS cluster with Fargate launch type
3. Create a task definition:
   ```json
   {
     "family": "exhacker-backend",
     "networkMode": "awsvpc",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/exhacker-backend:latest",
         "portMappings": [{ "containerPort": 8000 }],
         "environment": [
           { "name": "ENVIRONMENT", "value": "production" }
         ],
         "secrets": [
           { "name": "DATABASE_URL", "valueFrom": "arn:aws:ssm:<region>:<account-id>:parameter/exhacker/DATABASE_URL" },
           { "name": "OPENAI_API_KEY", "valueFrom": "arn:aws:ssm:<region>:<account-id>:parameter/exhacker/OPENAI_API_KEY" }
         ]
       }
     ]
   }
   ```
4. Create a service with an Application Load Balancer

---

### GCP Cloud Run (Paid)

```bash
gcloud builds submit --tag gcr.io/<project-id>/exhacker-backend ./backend
gcloud run deploy exhacker-backend \
  --image gcr.io/<project-id>/exhacker-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=production,CORS_ORIGINS=[\"https://your-frontend.vercel.app\"]" \
  --set-secrets "DATABASE_URL=exhacker-database-url:latest"
```

---

### Azure App Service (Paid)

1. Create a Web App in the Azure Portal
2. Choose **Docker Container** as publish method
3. Set Docker image to your container registry
4. Configure Application Settings for environment variables
5. Enable CI/CD from source control

---

### DigitalOcean App Platform (Paid)

1. Create a **New App** in the DigitalOcean dashboard
2. Connect your GitHub repository
3. Set **Source Directory** to `backend`
4. Set **Run Command** to `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Add environment variables in the dashboard
6. Deploy

**Pricing:** Starts at $5/month for basic apps.

---

## Frontend Deployment

### Vercel (Free)

Vercel is the recommended platform for the Next.js frontend.

**Setup:**

1. Create an account at https://vercel.com
2. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```
3. Deploy:
   ```bash
   cd frontend
   vercel login
   vercel --prod
   ```
4. Configure environment variables in the Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` – URL of the deployed backend API (e.g., `https://exhacker-backend.railway.app/api/v1`)
5. (Optional) Configure a custom domain in the Vercel dashboard

**Or via Git integration:**
1. Import your repository in the Vercel dashboard
2. Set **Root Directory** to `frontend`
3. Set **Build Command** to `next build` (default)
4. Set **Output Directory** to `.next` (default)
5. Add environment variable `NEXT_PUBLIC_API_URL`
6. Deploy

**Vercel Free Tier Limits:**
- 100 GB bandwidth/month
- 6000 build minutes/month
- 10 serverless function invocations per day (Hobby plan)
- 1 concurrent build
- Custom domains with automatic HTTPS

---

### Netlify (Free)

```bash
cd frontend
npm run build
netlify deploy --prod --dir=.next
```

Set environment variable `NEXT_PUBLIC_API_URL` in the Netlify dashboard.

**Netlify Free Tier:**
- 100 GB bandwidth/month
- 300 build minutes/month
- 1 concurrent build
- Form handling (not applicable)

---

### Cloudflare Pages (Free)

1. Log in to Cloudflare Dashboard
2. Go to **Pages** > **Create a project** > **Connect to Git**
3. Set build configuration:
   - **Framework preset**: Next.js
   - **Build command**: `npm run build`
   - **Build output directory**: `.next`
4. Set `NEXT_PUBLIC_API_URL` environment variable
5. Deploy

---

## Database Deployment

### Supabase (Free)

Supabase provides a generous free PostgreSQL tier.

**Setup:**

1. Create an account at https://supabase.com
2. Create a new project
3. Copy the database connection string from **Project Settings** > **Database** > **Connection string**
4. It will look like:
   ```
   postgresql+asyncpg://postgres:<password>@<ref>.supabase.co:5432/postgres
   ```
5. Configure additional parameters for pooler (recommended):
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true&prepared_statement_name=false
   DATABASE_SYNC_URL=postgresql+psycopg2://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true
   ```
6. Run migrations:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

**Supabase Free Tier Limits:**
- 500 MB database
- 2 GB bandwidth
- 50,000 monthly active users (for Auth)
- 1 GB file storage
- 2 CPUs (shared)
- Automatic backups (7-day retention)

---

### Neon (Free)

Neon offers serverless PostgreSQL with a generous free tier.

**Setup:**

1. Create an account at https://neon.tech
2. Create a new project
3. Copy the connection string
4. Configure env vars:
   ```
   DATABASE_URL=postgresql+asyncpg://<user>:<password>@<endpoint>.neon.tech:5432/neondb?sslmode=require
   DATABASE_SYNC_URL=postgresql+psycopg2://<user>:<password>@<endpoint>.neon.tech:5432/neondb?sslmode=require
   ```
5. Run migrations:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

**Neon Free Tier Limits:**
- 500 MB database
- 100 hours of compute time/month
- 10 branches
- Automatic backups (7-day retention)
- 1 GB bandwidth/month

---

### Railway Postgres (Free)

When deploying the backend on Railway, you can add a Postgres plugin:

```bash
railway add postgres
```

Railway auto-injects the `DATABASE_URL` environment variable into the backend service.

---

### AWS RDS (Paid)

```bash
# Create PostgreSQL instance (CLI)
aws rds create-db-instance \
  --db-instance-identifier exhacker-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username exhacker \
  --master-user-password <password> \
  --allocated-storage 20

# Get endpoint
aws rds describe-db-instances --db-instance-identifier exhacker-db --query "DBInstances[0].Endpoint.Address"
```

---

### DigitalOcean Managed Postgres (Paid)

1. Create a database in the DigitalOcean dashboard
2. Choose PostgreSQL 16
3. Select a plan (starts at $15/month for 1 GB RAM, 10 GB storage)
4. Copy the connection string from the dashboard

---

## Vector DB Deployment

### Qdrant Cloud (Free)

**Setup:**

1. Create an account at https://cloud.qdrant.io
2. Create a new cluster (free tier: 1 GB)
3. Copy the cluster URL and API key
4. Configure env vars:
   ```
   QDRANT_URL=https://<your-cluster>.cloud.qdrant.io:6333
   QDRANT_API_KEY=<your-api-key>
   ```

**Qdrant Free Tier:**
- 1 GB storage
- Standard performance
- Single replica

---

### Chroma (Self-hosted / Free)

Chroma can be run locally or embedded directly in the backend:

```python
# Embedded (no additional deployment needed)
import chromadb
client = chromadb.Client()
```

For a standalone Chroma server:
```bash
docker run -p 8000:8000 chromadb/chroma
```

---

## Monitoring

### BetterStack (Free Tier)

1. Create an account at https://betterstack.com
2. Add a **Uptime Monitor** for your backend URL
3. Configure notification channels (email, Slack, etc.)
4. Set up log monitoring via **Logs** integration:
   ```bash
   # Install the source
   curl -s https://betterstack.com/install.sh | sudo bash
   ```
5. For log shipping, the structured logging format (structlog) integrates easily.

**Free Tier Limits:**
- 10 uptime monitors (3-minute check interval)
- 1 GB log ingestion/month
- 3 days log retention
- 1 team member

---

### Grafana + Prometheus

**Option 1: Grafana Cloud (Free)**

1. Sign up at https://grafana.com
2. Create a stack
3. Add the Grafana Agent or Prometheus remote write endpoint
4. Configure the backend to expose metrics:
   ```python
   # In app/main.py or a separate metrics endpoint
   from prometheus_client import generate_latest, Counter, Histogram
   ```

**Free Tier:**
- 10,000 metrics series
- 50 GB logs
- 14 day retention

**Option 2: Self-hosted**

```bash
# docker-compose addition
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./infrastructure/prometheus:/etc/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
```

---

## Full Production Stack Example (Docker Compose)

For a self-hosted production deployment, extend the `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-exhacker}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: exhacker
    restart: always

  backend:
    build: ./backend
    environment:
      ENVIRONMENT: production
      DATABASE_URL: postgresql+asyncpg://exhacker:${POSTGRES_PASSWORD}@postgres:5432/exhacker
      CORS_ORIGINS: ${CORS_ORIGINS}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      XAI_API_KEY: ${XAI_API_KEY}
    depends_on:
      - postgres
    restart: always

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: https://api.yourdomain.com/api/v1
    depends_on:
      - backend
    restart: always

  nginx:
    image: nginx:alpine
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    restart: always

volumes:
  postgres_data:
```

---

## Environment Variable Reference by Platform

| Variable | Vercel | Railway | Render | Fly.io |
|----------|--------|---------|--------|--------|
| `ENVIRONMENT` | Dashboard | `railway env set` | Dashboard | `fly secrets set` |
| `DATABASE_URL` | N/A | `railway env set` | Dashboard | `fly secrets set` |
| `DATABASE_SYNC_URL` | N/A | `railway env set` | Dashboard | `fly secrets set` |
| `OPENAI_API_KEY` | N/A | `railway env set` | Dashboard | `fly secrets set` |
| `XAI_API_KEY` | N/A | `railway env set` | Dashboard | `fly secrets set` |
| `GEMINI_API_KEY` | N/A | `railway env set` | Dashboard | `fly secrets set` |
| `CORS_ORIGINS` | N/A | `railway env set` | Dashboard | `fly secrets set` |
| `NEXT_PUBLIC_API_URL` | Dashboard | Dashboard | Dashboard | Dashboard |
