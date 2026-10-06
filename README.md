# Veteran Referral Outcomes Portal

A system for tracking outcomes of referrals from the Veterans Crisis Line (VCL/988) to Veteran Service Organizations (VSOs/VSAs), without storing personally identifiable information in the shared system. VSAs log what happened with a referral (contacted, engaged, completed, etc.) using a token rather than any veteran identity, and the VA side gets aggregate reporting on referral effectiveness.

## Architecture

- **Backend**: FastAPI (Python), SQLAlchemy ORM
- **Frontend**: Next.js (React, TypeScript)
- **Database**: PostgreSQL with Row-Level Security for per-VSA data isolation
- **Infrastructure**: Terraform (AWS) for the real environment; see `infrastructure/`

Roles: `VA_ADMIN` (sees all VSAs), `VSA_ADMIN` / `VSA_USER` (see only their own VSA's data).

## Local setup

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

**Database** (requires a running PostgreSQL instance)
```bash
createdb veteran_referral_portal
psql -d veteran_referral_portal -f database/schema.sql
psql -d veteran_referral_portal -f database/users_schema.sql
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Demo accounts (seeded by `database/users_schema.sql`)
- VA admin: `va_admin` / `admin123`
- VSA admin (VSA001): `vsa_admin` / `vsapass123`

## API

- `POST /v1/auth/login`, `GET /v1/auth/users/me`
- `GET/POST /v1/referrals`, `GET /v1/referrals/{token}`, `POST /v1/referrals/import/csv`, `GET /v1/referrals/summary/stats`
- `GET/POST /v1/outcomes`, `PUT/DELETE /v1/outcomes/{id}`, `POST /v1/outcomes/bulk`, `GET /v1/outcomes/summary/stats`

Referral creation/import is VA-admin-only (referrals originate from the crisis line side); outcomes are VSA-only. Read endpoints are shared: VA admins see across all VSAs, VSA staff see only their own.

## Data isolation

Zero-PII is enforced at two layers:
1. Application-level filtering by `vsa_id` in each endpoint.
2. Postgres Row-Level Security policies (`database/schema.sql`), enforced with `FORCE ROW LEVEL SECURITY` so they apply even to the table-owning role. The backend sets the Postgres session variables these policies check (`app.vsa_id`, `app.user_role`) per request via `get_db_with_context` in `app/core/auth.py`.

Inbound CSV imports are also scanned for accidental PII (SSNs, emails, phone numbers, name-like patterns) before being accepted — see `app/core/pii_detector.py`.

## Testing

```bash
cd backend
pip install -r requirements.txt
pytest tests/
```

Current coverage is the PII detector and referral-endpoint authorization — the two places that had real bugs (dead PII regexes, missing auth) before. Not a full suite yet.

```bash
cd frontend
npm run build
npm run lint
```

## Known limitations

- No automated tests for the outcomes endpoints or the frontend yet.
- `npm audit` still flags issues that require a Next.js major-version bump (15 → 16); not done here since it's a breaking change.
- The Terraform in `infrastructure/` provisions networking, RDS, and cost tracking; it doesn't yet provision anywhere to actually run the application (ECS/EC2/container hosting). `DEPLOYMENT.md` covers what's real today.
