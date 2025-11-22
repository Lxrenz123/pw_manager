# Password Manager

FastAPI + Svelte password manager with client-side encryption, CSRF-protected cookie auth, PostgreSQL, and Redis.

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis
- Frontend: Svelte (Vite)
- Auth: HTTP-only cookies + CSRF header; optional TOTP 2FA
- Docker: Compose stack for API, Postgres, Redis
- Logging: API container logs to host rsyslog (syslog driver)

-------------------------------------------------------------------------------

## 1) Production/Server setup (Docker + Nginx reverse proxy)

Prerequisites
- Debian/Ubuntu server with a domain (e.g., password123.pw) pointing to the host
- Docker + Docker Compose
- Nginx with TLS (e.g., Let’s Encrypt via certbot)

Project layout
- backend/ (FastAPI app, Dockerfile, docker-compose.yaml)
- frontend/ (Svelte app)

Step A — Configure backend environment
1) Create backend/.env from your template and set values:
   - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE
   - DATABASE_URL (async): postgresql+asyncpg://USER:PASS@postgres:5432/DB
   - DATABASE_URL_ALEMBIC (sync): postgresql://USER:PASS@postgres:5432/DB
   - JWT_SECRET_KEY, ALGORITHM=HS256, JWT_TOKEN_EXPIRE
   - PREAUTH_TOKEN_EXPIRE
   - CSRF_HMAC_SECRET
   - RECAPTCHA_SECRET_KEY (v3/v2 private keys)
   - RECAPTCHAV2_SECRET_KEY

2) Start the stack:
   cd backend
   sudo docker compose up -d --build

3) Initialize database schema:
   sudo docker compose exec api alembic upgrade head

Step B — (Optional) create a restricted DB role
If you want an app-specific user inside the DB:
   sudo docker exec -it backend-postgres-1 psql -U <POSTGRES_USER> -d <POSTGRES_DATABASE>

Run:
   CREATE ROLE pw_manager_user LOGIN PASSWORD 'test';
   GRANT CONNECT ON DATABASE <POSTGRES_DATABASE> TO pw_manager_user;
   GRANT USAGE ON SCHEMA public TO pw_manager_user;
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO pw_manager_user;
   GRANT CREATE ON SCHEMA public TO pw_manager_user;

Adjust your DATABASE_URLs accordingly if you switch to this role.

Step C — Build and deploy frontend
1) Build the Svelte frontend:
   cd frontend
   npm install
   npm run build

2) Serve static files via Nginx:
   sudo rsync -av dist/ /var/www/html/
   sudo chown -R www-data:www-data /var/www/html
   sudo chmod -R 755 /var/www/html

Step D — Nginx reverse proxy to backend API
- Serve frontend at https://password123.pw/
- Reverse proxy API at https://password123.pw/api → FastAPI container (127.0.0.1:8000)

Example Nginx server block (simplified):
   server {
     listen 80;
     server_name password123.pw;
     return 301 https://$host$request_uri;
   }

   server {
     listen 443 ssl http2;
     server_name password123.pw;

     # ssl_certificate /etc/letsencrypt/live/password123.pw/fullchain.pem;
     # ssl_certificate_key /etc/letsencrypt/live/password123.pw/privkey.pem;

     root /var/www/html;
     index index.html;

     # Frontend (SPA)
     location / {
       try_files $uri $uri/ /index.html;
     }

     # API reverse proxy to Docker-hosted FastAPI
     location /api/ {
       proxy_pass http://127.0.0.1:8000/api/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_http_version 1.1;
     }
   }

Notes
- Cookies/CSRF: The API uses cookie auth plus an X-CSRF-TOKEN header. Keep HTTPS enabled in production so cookies can be Secure.
- Trailing slashes: Some routes end with a slash (e.g., /api/user/). Call the exact path to avoid 307 redirects.
- reCAPTCHA:
  - Place the public/site key in the frontend where the widget/script requires it.
  - Place private keys in backend .env (RECAPTCHA_SECRET_KEY, RECAPTCHAV2_SECRET_KEY).
- Logging: docker-compose is set to log via syslog to the host. Ensure rsyslog listens on UDP 514 and is allowed to accept from the Docker bridge (see backend/docker-compose.yaml options).

-------------------------------------------------------------------------------

## 2) Local development setup

Frontend (Vite dev server)
1) Install Node/NPM:
   sudo apt update && sudo apt install -y npm

2) Install deps and run dev:
   cd frontend
   npm install
   npm run dev
   # Dev server defaults to http://localhost:5173

3) API base URL
   - Option 1 (recommended): keep apiBase relative (/api) and use a Vite proxy in vite.config.js to http://localhost:8000.
   - Option 2: set frontend/src/script/api-base-url.js to 'http://localhost:8000/api' explicitly.

4) reCAPTCHA
   - Put your reCAPTCHA public/site key in the frontend where you render/initialize it.

Backend (FastAPI + Alembic)
1) Python env:
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2) .env:
   - Create backend/.env with DB URLs (can point to local Postgres or the dockerized Postgres), JWT secret, CSRF_HMAC_SECRET, and reCAPTCHA private keys.

3) CORS for local dev:
   - Ensure app/main.py allows origins: http://localhost:5173
   - Example already present:
     allow_origins=["https://password123.pw"] → add "http://localhost:5173" during development.

4) Cookies for local:
   - Use non-Secure cookies locally (secure=false) while on http://localhost.
   - Avoid setting a cookie Domain for localhost, or set it explicitly to localhost.
   - In frontend Login.svelte fetch calls, include cookies:
     credentials: 'include'

5) Database and migrations:
   - Start Postgres/Redis (via Docker or local services). With Compose:
     cd backend
     sudo docker compose up -d postgres redis
   - Initialize/upgrade schema:
     alembic upgrade head
   - Create a migration when models change:
     alembic revision --autogenerate -m "message"
     alembic upgrade head
   - Troubleshooting “Can’t locate revision …”:
     The DB may reference a missing migration. Inspect/clear alembic_version (only if you know the state) and re-run upgrade.

6) Run API:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Quick local end-to-end
- Backend: uvicorn on 8000
- Frontend: Vite on 5173 with credentials: 'include' on login requests and correct CSRF header
- CORS: allow http://localhost:5173 in FastAPI
- API base URL: relative /api with Vite proxy, or http://localhost:8000/api

-------------------------------------------------------------------------------

## 3) Docker Compose (local or server)

Start all services:
   cd backend
   sudo docker compose up -d --build

View logs:
   sudo docker compose logs -f api

Apply migrations inside the container:
   sudo docker compose exec api alembic upgrade head

-------------------------------------------------------------------------------

## 4) Environment variables (backend/.env)

Required
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- POSTGRES_DATABASE=pw_manager
- DATABASE_URL=postgresql+asyncpg://USER:PASS@postgres:5432/DB
- DATABASE_URL_ALEMBIC=postgresql://USER:PASS@postgres:5432/DB
- JWT_SECRET_KEY=change_me
- ALGORITHM=HS256
- JWT_TOKEN_EXPIRE=3600
- PREAUTH_TOKEN_EXPIRE=300
- CSRF_HMAC_SECRET=change_me
- RECAPTCHA_SECRET_KEY=<private key v3 or server-side key>
- RECAPTCHAV2_SECRET_KEY=<private key v2>

Security
- Use strong, unique secrets (JWT_SECRET_KEY, CSRF_HMAC_SECRET).
- Always use HTTPS in production so cookies can be Secure and SameSite policies are enforced.

-------------------------------------------------------------------------------

## 5) Nginx + static deployment summary

- Build frontend: npm run build
- Copy dist/ to /var/www/html:
   sudo rsync -av frontend/dist/ /var/www/html/
   sudo chown -R www-data:www-data /var/www/html
   sudo chmod -R 755 /var/www/html

- Reverse proxy /api to the FastAPI service on 127.0.0.1:8000 (see example config above).
- Obtain TLS certs (certbot) and enable HTTPS.

-------------------------------------------------------------------------------

## 6) Troubleshooting

Mixed Content blocked
- Serve everything via HTTPS in production.
- For local dev: ensure frontend calls http://localhost:8000 or use Vite proxy to avoid cross-scheme calls.

CORS/CSRF
- Ensure http://localhost:5173 is in allow_origins during dev.
- Always send cookies with fetch:
   credentials: 'include'
- Send X-CSRF-TOKEN header with the csrf_token cookie’s value.

Trailing slash redirects
- If a route is declared with a trailing slash (e.g., /api/user/), call it with the trailing slash to avoid a 307 redirect.

Alembic “Can’t locate revision”
- The DB’s alembic_version may reference a non-existent file. Inspect it and either align versions or clear carefully, then run alembic upgrade head.

Postgres role setup
- See the “restricted DB role” section if you want to run with a non-superuser in the DB.

Syslog not receiving API logs
- Ensure rsyslog is listening on UDP 514 and permitted to accept from the Docker bridge address used in backend/docker-compose.yaml.