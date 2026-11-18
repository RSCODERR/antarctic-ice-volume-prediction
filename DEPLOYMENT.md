# CryoPredict — Production Deployment Guide

This document describes how to deploy the CryoPredict scientific platform across containerized, bare-metal Linux (systemd), and cloud environments.

---

## 1. System Requirements

### Hardware:
- **CPU:** 2+ vCPUs recommended
- **RAM:** 2 GB minimum (4 GB recommended for scikit-learn model loading and DataFrame operations)
- **Disk:** 5 GB free disk space (includes model artifacts, CSV tables, and runtime dependencies)

### Software:
- **Python:** 3.10, 3.11, or 3.12
- **Node.js:** 18+ (Node 20 or 22 LTS recommended for building frontend)
- **Docker:** Optional (Docker 24+ and Docker Compose v2 for containerized deployment)

---

## 2. Environment Variables Configuration

Copy `.env.example` to `.env` in the project root:

```bash
cp .env.example .env
```

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DEBUG` | `False` | Enables development autoreload when `True`. Must be `False` in production. |
| `CRYOPREDICT_REPO_ROOT` | `.` | Absolute or relative path to the project root containing `models/`, `reports/`, and `data/`. |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of allowed frontend origins. |
| `BACKEND_HOST` | `0.0.0.0` | Host IP address to bind Uvicorn server. |
| `BACKEND_PORT` | `8000` | Port for the FastAPI backend. |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | API root consumed by the React client during production build. |

---

## 3. Option A: Docker Deployment (Recommended)

CryoPredict includes multi-stage production Dockerfiles for both backend and frontend.

### Build and Start Containers:
```bash
docker compose up -d --build
```

### Check Container Status:
```bash
docker compose ps
docker compose logs -f backend
```

- Frontend is accessible at: `http://localhost`
- Backend API is accessible at: `http://localhost:8000`
- Interactive Swagger documentation: `http://localhost:8000/docs`

---

## 4. Option B: Native Linux / Production VM Deployment

### Step 1: Backend Setup
```bash
# 1. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install backend dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# 3. Verify backend test suite
cd backend
python -m pytest tests/ -v
cd ..

# 4. Start backend with production Gunicorn/Uvicorn workers
uvicorn app.main:app \
  --app-dir backend \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

#### Systemd Service Configuration (`/etc/systemd/system/cryopredict-backend.service`):
```ini
[Unit]
Description=CryoPredict FastAPI Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/cryopredict
EnvironmentFile=/var/www/cryopredict/.env
ExecStart=/var/www/cryopredict/.venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Step 2: Frontend Production Build
```bash
cd frontend

# Set production API URL
export VITE_API_BASE_URL=https://api.yourdomain.com

# Install dependencies and build static assets
npm ci
npm run build
```

The compiled static files are generated in `frontend/dist/`.

#### Nginx Static Host Configuration (`/etc/nginx/sites-available/cryopredict`):
```nginx
server {
    listen 80;
    server_name cryopredict.yourdomain.com;

    root /var/www/cryopredict/frontend/dist;
    index index.html;

    # Client-side routing fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Reverse proxy API requests to backend
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static asset caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
}
```

---

## 5. Security & Production Checklist

- [x] `DEBUG` is set to `False` in production environment.
- [x] CORS origins explicitly whitelist only approved production frontend domains.
- [x] Error handlers catch unexpected exceptions and hide internal server traces.
- [x] `.env` is excluded from version control via `.gitignore`.
- [x] Model weights and projection manifests are mounted read-only.
- [x] Healthcheck endpoint (`/api/health`) configured for load-balancer probes.
- [x] Static assets served with appropriate HTTP caching headers.

---

## 6. Verification Commands

Before traffic routing, run the verification suite:
```bash
# Verify backend API endpoints
.venv/bin/python scratch/stage8_backend_acceptance_test.py

# Verify frontend build
cd frontend && npm run build
```
