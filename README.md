## **Project Overview**

This project is a full-stack password manager consisting of:

* A **FastAPI backend**
* A **Svelte frontend**
* A **PostgreSQL** database
* A **Docker-based** monitoring and logging stack
* An **Nginx** reverse proxy

The live production deployment is available at:

👉 **[https://password123.pw](https://password123.pw)**

The application implements secure JWT authentication, CSRF protection, 2-factor authentication (TOTP), encrypted secret storage, rate-limiting, Google reCAPTCHA, and full observability through Loki + Grafana.


## **Technology Stack**

### **Backend**

* FastAPI (Python)
* SQLAlchemy ORM
* Alembic (database migrations)
* PostgreSQL
* Redis (token blacklist, rate limiting)
* Nginx (reverse proxy)

### **Frontend**

* Svelte
* JavaScript
* Vite (build tool)
* Nginx (serving static assets)

### **Docker Stack**

The application uses Docker Compose and includes:

* `api` (FastAPI backend)
* `postgres` (database)
* `redis`
* `grafana`
* `loki`
* `promtail`


## **Directory Structure Overview**

### **Backend**

| Path                              | Explanation                      |
|  | -- |
| `/backend/app/models/`            | Database models                  |
| `/backend/app/routers/`           | API endpoints                    |
| `/backend/app/schema/`            | Pydantic validation schemas      |
| `/backend/app/main.py`            | FastAPI app entrypoint           |
| `/backend/app/csrf_protection.py` | CSRF token system                |
| `/backend/app/auth.py`            | Authentication & JWT logic       |
| `/backend/app/database.py`        | Database connection/session      |
| `/backend/app/limiter.py`         | Rate limiting logic              |
| `/backend/app/twofa.py`           | TOTP / Two-factor authentication |
| `/backend/app/recaptcha.py`       | Google reCAPTCHA API             |

### **Frontend**

| Path                                   | Explanation             |
| -- | -- |
| `/frontend/src/`                       | Svelte application code |
| `/frontend/src/script/api-base-url.js` | Defines API base URL    |

Frontend static files are compiled using:

```bash
npm run build
```

The output inside `dist/` is served by Nginx.


# **NGINX Reverse Proxy Configuration**

### Forward API requests to FastAPI:

```nginx
location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Forward all frontend routes to `index.html`:

```nginx
location / {
        try_files $uri /index.html;
}
```

This ensures Svelte routing works correctly on reload.


# **Local Development Setup**

## **1. Clone the Repository**

```bash
git clone https://github.com/Lxrenz123/pw_manager.git
cd pw_manager
```


## **2. Frontend Setup**

### Requirements

* Node.js (18+)

Install dependencies:

```bash
cd frontend
npm install
npm install vite
```

Run dev server:

```bash
npm run dev
```

Configure API base URL:

```javascript
// frontend/src/script/api-base-url.js
export const apiBase = "http://localhost:8000"
```

Update reCAPTCHA keys in:

```
frontend/src/pages/Login.svelte
```


## **3. Backend Setup**

Move into backend directory:

```bash
cd ../backend
```

Create `.env` file:

```
JWT_SECRET_KEY="random string"
ALGORITHM="HS256"
JWT_TOKEN_EXPIRE=300
DATABASE_URL="postgresql+asyncpg://user:password@postgres:5432/pw_manager_db"
DATABASE_URL_ALEMBIC="postgresql+psycopg2://user:password@localhost:5432/pw_manager_db"
PREAUTH_TOKEN_EXPIRE=2

RECAPTCHA_SECRET_KEY=""
RECAPTCHAV2_SECRET_KEY=""

POSTGRES_USER=admin
POSTGRES_PASSWORD="password"
POSTGRES_DATABASE=pw_manager_db

CSRF_HMAC_SECRET="random string"
GRAFANA_PASSWORD_ADMIN="password"
```


## **4. Start Docker Stack**

```bash
docker compose up -d --build
```

### Access Postgres:

```bash
docker exec -it backend-postgres-1 psql -U admin -d pw_manager_db
```

Inside psql:

```sql
CREATE ROLE pw_manager_user LOGIN PASSWORD 'test';
GRANT CONNECT ON DATABASE pw_manager_db TO pw_manager_user;
GRANT USAGE ON SCHEMA public TO pw_manager_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO pw_manager_user;
GRANT CREATE ON SCHEMA public TO pw_manager_user;
```


## **5. Run Alembic Migrations**

Install packages:

```bash
pip install alembic asyncpg psycopg2
```

Initialize database:

```bash
alembic stamp head
alembic revision --autogenerate -m "database migration"
alembic upgrade head
```


## **6. Test API**

FastAPI documentation UI is available at:

👉 **[http://localhost:8000/api/docs](http://localhost:8000/api/docs)**


## **Important Note About Local Cookies**

Browsers block cookies between:

* `localhost:5173` (frontend)
* `localhost:8000` (backend)

This triggers **SameSite + secure cookie restrictions**.

Solutions:

* use a local reverse proxy
* disable cookie security in dev mode
* run frontend through backend

Production works fine.




