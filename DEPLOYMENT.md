# Deployment

## Local development

```bash
git clone <repository-url>
cd veteran-referral-portal/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

createdb veteran_referral_portal
psql -d veteran_referral_portal -f ../database/schema.sql
psql -d veteran_referral_portal -f ../database/users_schema.sql

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
# sanity checks
curl http://localhost:8000/health

curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=va_admin&password=admin123"
```

## AWS infrastructure (Terraform)

`infrastructure/` provisions the networking and database layer: a VPC with public/private/database subnets, an RDS Postgres instance (Multi-AZ when `environment = "prod"`), security groups, an S3 bucket + budget for cost tracking.

```bash
aws configure
cd infrastructure
terraform init
terraform plan
terraform apply
terraform output   # database endpoint, etc.
```

Then apply the schema against the real database:
```bash
./scripts/init_database.sh
```

### What's not built yet

This Terraform does not provision anywhere to run the application itself (no ECS/Fargate, no ALB, no container registry). Running the API against the real RDS instance today means pointing `DATABASE_URL` at the Terraform-managed endpoint and running the FastAPI app yourself (a VM, a container you run manually, etc.) — there's no one-command path to a hosted deployment yet.

## Environment variables

See `database_url`, `secret_key`, `allowed_origins`, `allowed_hosts` in `backend/app/config.py` for what's configurable, and the `.env` example in the README.
