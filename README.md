# Password123 -  Password Manager

## Local Development Setup

### Clone the Repository
```bash
git clone https://github.com/Lxrenz123/pw_manager.git
```

### Frontend Requirements
- Node.js

### Frontend Setup
```bash
cd pw_manager
cd frontend
npm install
npm install vite
npm run dev
```

Edit `frontend/src/script/api-base-url.js`:
```javascript
export const apiBase = "http://localhost:8000"
```

Change Google site keys in `frontend/src/pages/Login.svelte` for reCAPTCHA to work (top variables):
```svelte
let v3Key = "..."
let v2Key = "..."
```

### Backend Setup
```bash
cd backend/
```
### .ENV Template
Create `.env` in `backend/`.
- make sure to adjust these values
```bash
JWT_SECRET_KEY="random string of 64 characters"
ALGORITHM = "HS256"
JWT_TOKEN_EXPIRE = 300
DATABASE_URL = "postgresql+asyncpg://user:password@postgres:5432/pw_manager_db"
DATABASE_URL_ALEMBIC = "postgresql+psycopg2://user:password@localhost:5432/pw_manager_db"
PREAUTH_TOKEN_EXPIRE = 2

RECAPTCHA_SECRET_KEY = "" 

RECAPTCHAV2_SECRET_KEY = ""


#DATABASE CONTAINER
POSTGRES_USER=admin
POSTGRES_PASSWORD="password"
POSTGRES_DATABASE=pw_manager_db

#CSRF HMAC
CSRF_HMAC_SECRET="random string of 64 characters"

#LOGGING AND MONITORING
GRAFANA_PASSWORD_ADMIN="password"
```
Add Postgres user that is non-root and make sure it matches with database URL in `.env` and Alembic URL.

```bash
docker compose up -d --build
docker exec -it backend-postgres-1 psql -U admin -d pw_manager_db
```

In the psql shell:
```
CREATE ROLE pw_manager_user LOGIN PASSWORD 'test';
GRANT CONNECT ON DATABASE pw_manager_db TO pw_manager_user;
GRANT USAGE ON SCHEMA public TO pw_manager_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO pw_manager_user;
GRANT USAGE ON SCHEMA public TO pw_manager_user;
GRANT CREATE ON SCHEMA public TO pw_manager_user;
```

Initialize database into Postgres with Alembic:
```bash
pip install alembic
pip install asyncpg
alembic stamp head
alembic revision --autogenerate -m "database migration"
alembic upgrade head
```

### Testing
Test: http://localhost:8000/api/docs

**Note**: Still don't know how to make access token and csrf token cookies save in local development, I tried changing the cookie properties but nothing worked as my browser kept blocking cookies because of cross site as frontend and backend runs on different ports
