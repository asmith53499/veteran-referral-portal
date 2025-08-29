# Veteran Referral Portal - Development Notes

## 🎯 Project Status: Infrastructure Complete, Ready for Backend

### ✅ COMPLETED
- [x] Project structure & folder organization
- [x] CSV intake design (PII-safe structure)
- [x] AWS infrastructure deployment
- [x] PostgreSQL RDS database (15.7)
- [x] VPC with isolated subnets
- [x] Security groups & IAM roles
- [x] Cost allocation tags & budget monitoring
- [x] Database schema design
- [x] Row-Level Security (RLS) planning

### 🏗️ INFRASTRUCTURE DETAILS
- **VPC**: `10.0.0.0/16` (us-east-1)
- **Database**: `vrp-dev-postgres.cfweqeqc2w2k.us-east-1.rds.amazonaws.com:5432`
- **Security**: Private subnets, encrypted storage, monitoring enabled
- **Cost**: $1,000 monthly budget, project-isolated tagging

### 🚧 CURRENT BLOCKERS
- Database in private subnet (correct for security)
- Need bastion host or backend deployment for access
- Temporary dev access added to security group (IP: 75.62.78.122/32)

### 🔄 NEXT STEPS (Priority Order)

#### **Phase 1: FastAPI Backend Setup (2-3 hours)**
1. Create backend project structure
2. Set up dependencies (FastAPI, SQLAlchemy, psycopg2)
3. Database connection & models
4. Basic health check endpoint
5. Test database connectivity

#### **Phase 2: Core Functionality (3-4 hours)**
1. Referrals table model & API
2. CSV import endpoint
3. PII validation logic
4. Basic CRUD operations

#### **Phase 3: Authentication & Security (2-3 hours)**
1. JWT authentication
2. VSA role management
3. RLS integration
4. User management

#### **Phase 4: Outcomes & Reporting (2-3 hours)**
1. Outcomes table & API
2. Status update functionality
3. Basic reporting endpoints
4. Audit logging

### 💡 TECHNICAL DECISIONS MADE

#### **Database Architecture**
- PostgreSQL 15.7 with RLS
- Separate tables: referrals, outcomes, audit_log
- UUID primary keys for security
- Enum types for status/type fields

#### **Security Approach**
- Zero PII in shared systems
- Token-based referral tracking
- Row-Level Security per VSA
- Encrypted storage & connections

#### **API Design**
- RESTful endpoints
- JWT authentication
- Role-based access control
- Comprehensive audit logging

### 🎨 FRONTEND CONSIDERATIONS (Future)
- React + Next.js + Tailwind
- VSA portal for outcome updates
- VA dashboard for reporting
- Responsive design for mobile

### 📊 CSV STRUCTURE (Finalized)
```csv
referral_token,issued_at,vsa_id,program_code,episode_id,referral_type,priority_level,crisis_type,urgency_indicator,expected_contact_date,va_facility_code
```

### 🔐 ENVIRONMENT VARIABLES NEEDED
- Database connection string
- JWT secret key
- AWS credentials (if needed)
- Environment (dev/staging/prod)

### 🚀 DEPLOYMENT STRATEGY
- ECS Fargate in private subnets
- Application Load Balancer
- Auto-scaling based on demand
- Blue-green deployments

### 📝 NOTES & IDEAS
- Consider adding webhook support for real-time updates
- Implement rate limiting per VSA
- Add data export functionality for compliance
- Consider adding SMS/email notifications for urgent referrals

### 🎯 SUCCESS METRICS
- Referral import success rate > 99%
- API response time < 200ms
- Zero PII leaks
- 100% audit trail coverage

### 🚨 RISKS & MITIGATION
- **Risk**: Database performance with high volume
  - **Mitigation**: Proper indexing, connection pooling, monitoring
- **Risk**: PII accidentally included in CSV
  - **Mitigation**: Automated validation, regex checks, entropy analysis
- **Risk**: VSA adoption challenges
  - **Mitigation**: Simple UI, clear documentation, training materials

---
*Last Updated: 2025-08-29*
*Next Review: After Phase 1 completion*
