# Veteran Referral Outcomes Portal

A secure, privacy-preserving system for tracking veteran referral outcomes between the Veterans Crisis Line (VCL/988) and Veteran Service Organizations (VSOs/VSAs).

## 🎯 **Project Status: Phase 2 Complete**

### ✅ **COMPLETED FEATURES**
- **Infrastructure**: AWS VPC, RDS PostgreSQL, security groups
- **Backend API**: FastAPI with comprehensive endpoints
- **Authentication**: JWT-based auth with role management (VA_ADMIN, VSA_ADMIN, VSA_USER)
- **CSV Import**: Working import with PII detection and validation
- **Statistics**: Real-time analytics and reporting
- **Database**: Complete schema with relationships and constraints

### 🔄 **CURRENT STATUS**
- **Phase 1**: ✅ Complete (Core Setup & Basic API)
- **Phase 2**: ✅ Complete (Authentication & Authorization)
- **Phase 3**: 🔄 Next (Outcomes Tracking)

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.13+
- PostgreSQL 15.7+
- AWS CLI configured
- Terraform 1.0+

### **Local Development Setup**
```bash
# Clone repository
git clone <repository-url>
cd project_bridgepoint

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
createdb veteran_referral_portal
psql -d veteran_referral_portal -f ../database/schema.sql
psql -d veteran_referral_portal -f ../database/users_schema.sql

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Test the API**
```bash
# Health check
curl http://localhost:8000/v1/health

# Login (default VA admin)
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=va_admin&password=admin123"

# Import sample data
curl -X POST -F "file=@../data/sample_referrals.csv" \
  -F "vsa_id=TEST_VSA_001" \
  http://localhost:8000/v1/referrals/import/csv
```

## 🏗️ **Architecture**

### **Backend Stack**
- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL 15.7 (AWS RDS)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT tokens with bcrypt
- **Validation**: Pydantic schemas
- **Logging**: Structured logging with structlog

### **Infrastructure**
- **Cloud**: AWS (VPC, RDS, Security Groups)
- **IaC**: Terraform for infrastructure as code
- **Security**: Private subnets, encrypted storage
- **Monitoring**: CloudWatch logs and metrics

### **Security Features**
- **Zero-PII Design**: No personally identifiable information stored
- **Token-Based Tracking**: UUIDs for referral identification
- **Role-Based Access**: VA_ADMIN, VSA_ADMIN, VSA_USER roles
- **Password Security**: bcrypt hashing with salt
- **JWT Authentication**: Secure token-based sessions

## 📊 **Data Model**

### **Core Tables**
- **referrals**: Token-based referral tracking with standardized fields
- **outcomes**: Outcome status and reason tracking
- **users**: Role-based access control
- **organizations**: VSA organization management
- **audit_logs**: WORM-compliant audit trail

### **CSV Import Structure**
```csv
referral_token,issued_at,vsa_id,program_code,episode_id,referral_type,priority_level,crisis_type,urgency_indicator,expected_contact_date,va_facility_code
550e8400-e29b-41d4-a716-446655440000,2024-01-15T10:30:00Z,TEST_VSA_001,CRISIS_INTERVENTION,EP001,CRISIS_HOTLINE,HIGH,SUICIDE_RISK,IMMEDIATE,2025-09-15,VA_ATL
```

## 🔌 **API Endpoints**

### **Authentication**
- `POST /v1/auth/login` - User login
- `GET /v1/auth/users/me` - Current user profile
- `PUT /v1/auth/users/me` - Update user profile
- `POST /v1/auth/users/me/change-password` - Change password

### **Referrals**
- `GET /v1/referrals` - List referrals
- `POST /v1/referrals/import/csv` - Import CSV data
- `GET /v1/referrals/summary/stats` - Get statistics
- `GET /v1/referrals/{referral_token}` - Get specific referral

### **User Management (VA Admin Only)**
- `GET /v1/auth/users` - List all users
- `POST /v1/auth/users` - Create new user
- `GET /v1/auth/users/{user_id}` - Get specific user
- `PUT /v1/auth/users/{user_id}` - Update user

### **Health & Monitoring**
- `GET /v1/health` - Health check
- `GET /docs` - Interactive API documentation

## 🚀 **Deployment**

### **AWS Infrastructure**
```bash
# Deploy infrastructure
cd infrastructure
terraform init
terraform plan
terraform apply
```

### **Database Setup**
```bash
# Apply schema
./scripts/init_database.sh
```

### **Application Deployment**
```bash
# Build and deploy application
cd backend
docker build -t veteran-referral-portal .
docker run -p 8000:8000 veteran-referral-portal
```

## 📈 **Performance**

### **Current Metrics**
- **API Response Time**: < 100ms for most endpoints
- **Database Queries**: Optimized with proper indexes
- **Memory Usage**: Efficient SQLAlchemy session management
- **Concurrent Users**: Tested with multiple simultaneous requests

### **Scalability**
- **Database**: RDS with read replicas for scaling
- **Application**: Stateless design for horizontal scaling
- **Caching**: Redis for session and query caching
- **Load Balancing**: ALB for traffic distribution

## 🔒 **Security**

### **Data Protection**
- **Zero-PII Design**: No personally identifiable information stored
- **Encryption**: Data encrypted at rest and in transit
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete audit trail for compliance

### **Network Security**
- **VPC Isolation**: Private subnets for database
- **Security Groups**: Restrictive firewall rules
- **SSL/TLS**: Encrypted connections throughout
- **IAM Roles**: Least privilege access

## 📋 **Development Phases**

### **✅ Phase 1: Core Setup & Basic API (COMPLETED)**
- Infrastructure setup (AWS VPC, RDS)
- Database schema design
- FastAPI backend with core endpoints
- CSV import functionality
- Statistics and reporting

### **✅ Phase 2: Authentication & Authorization (COMPLETED)**
- JWT token-based authentication
- Role-based access control
- User management system
- Password security
- Authorization enforcement

### **🔄 Phase 3: Outcomes Tracking (NEXT)**
- Outcome creation and management
- Status tracking and validation
- Outcome statistics
- VSA-specific views

### **📋 Phase 4: Frontend Development (PLANNED)**
- React/Next.js application
- User interface design
- Authentication integration
- Responsive design

### **📋 Phase 5: Row-Level Security (PLANNED)**
- Database-level VSA data isolation
- RLS policies implementation
- User context management

### **📋 Phase 6: Reporting & Analytics (PLANNED)**
- Advanced reporting dashboard
- Export functionality
- Custom analytics
- Performance metrics

## 🧪 **Testing**

### **API Testing**
```bash
# Test health endpoint
curl http://localhost:8000/v1/health

# Test authentication
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=va_admin&password=admin123"

# Test CSV import
curl -X POST -F "file=@../data/sample_referrals.csv" \
  -F "vsa_id=TEST_VSA_001" \
  http://localhost:8000/v1/referrals/import/csv
```

### **Database Testing**
```bash
# Connect to database
psql -d veteran_referral_portal

# Check tables
\dt

# Check data
SELECT COUNT(*) FROM referrals;
SELECT COUNT(*) FROM users;
```

## 📚 **Documentation**

- **API Documentation**: `/docs` endpoint when server is running
- **Development Notes**: [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md)
- **Infrastructure**: [infrastructure/README.md](infrastructure/README.md)
- **Database Schema**: [database/schema.sql](database/schema.sql)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 **Support**

For support and questions:
- **Documentation**: See [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md)
- **API Docs**: Available at `/docs` when server is running
- **Issues**: Create an issue in the repository

---

**Last Updated**: August 29, 2025  
**Version**: 1.0.0  
**Status**: Phase 2 Complete - Ready for Phase 3
