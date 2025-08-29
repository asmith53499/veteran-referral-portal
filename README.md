# Veteran Referral Outcomes Portal

A secure, privacy-preserving system designed to bridge the data gap between the Veterans Crisis Line (VCL/988) and Veteran Service Organizations (VSOs/VSAs). The system enables VSAs to log outcomes of referrals in a standardized, secure, non-PII format while providing VA and stakeholders with aggregate, transparent reporting on referral effectiveness.

## 🎯 **Project Overview**

The Veteran Referral Outcomes Portal addresses a critical gap in veteran service coordination by providing a secure platform for tracking referral outcomes without compromising veteran privacy. The system maintains a zero-PII architecture while enabling comprehensive reporting and analytics.

### **Key Features**
- **Zero-PII Architecture**: No personally identifiable information stored in shared systems
- **Token-based Tracking**: Secure referral tracking using UUIDs/HMACs
- **Role-based Access**: VA_ADMIN, VSA_ADMIN, and VSA_USER roles
- **Real-time Analytics**: Dashboard with live statistics and reporting
- **Bulk Operations**: Efficient data import and management
- **Mobile-responsive**: Works on all devices and screen sizes

## 🏗 **Architecture**

### **Technology Stack**
- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Frontend**: React + Next.js with TypeScript
- **Database**: PostgreSQL with Row-Level Security (RLS)
- **Infrastructure**: AWS with Terraform IaC
- **Authentication**: JWT with role-based access control

### **System Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│   Port 3001     │    │   Port 8000     │    │   Port 5432     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JWT Auth      │    │   CORS Config   │    │   RLS Policies  │
│   localStorage  │    │   Rate Limiting │    │   Data Isolation│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- PostgreSQL 13+
- Docker (optional)
- AWS CLI (for deployment)

### **Local Development Setup**

1. **Clone the repository**
```bash
git clone <repository-url>
cd project_bridgepoint
```

2. **Start the backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

3. **Start the frontend**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application**
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### **Demo Credentials**
- **VA Admin**: `va_admin` / `admin123`
- **VSA Admin**: `vsa_admin_2` / `newpassword456`

## 📁 **Project Structure**

```
project_bridgepoint/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── main.py            # Application entry point
│   ├── data/                  # Sample data
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Development server
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── lib/               # Utilities and API
│   │   └── types/             # TypeScript definitions
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.js     # Tailwind configuration
├── infrastructure/             # AWS Terraform
│   ├── main.tf                # Main infrastructure
│   ├── variables.tf           # Variable definitions
│   └── outputs.tf             # Output values
├── docs/                       # Documentation
├── PHASE1_COMPLETE.md         # Phase 1 documentation
├── PHASE2_COMPLETE.md          # Phase 2 documentation
├── PHASE3_COMPLETE.md          # Phase 3 documentation
├── PHASE4_COMPLETE.md          # Phase 4 documentation
├── PROJECT_STATUS.md           # Current project status
└── README.md                   # This file
```

## 🔧 **Configuration**

### **Environment Variables**

#### **Backend (.env)**
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:3001"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# AWS (for production)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

#### **Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 **API Endpoints**

### **Authentication**
- `POST /v1/auth/login` - User login
- `GET /v1/auth/users/me` - Get current user profile
- `POST /v1/auth/users/me/change-password` - Change password

### **Referrals**
- `GET /v1/referrals` - List referrals (with pagination)
- `GET /v1/referrals/{referral_token}` - Get specific referral
- `POST /v1/referrals/import/csv` - Import referrals from CSV
- `GET /v1/referrals/summary/stats` - Get referral statistics

### **Outcomes**
- `GET /v1/outcomes` - List outcomes (with pagination)
- `POST /v1/outcomes` - Create new outcome
- `PUT /v1/outcomes/{outcome_id}` - Update outcome
- `DELETE /v1/outcomes/{outcome_id}` - Soft delete outcome
- `POST /v1/outcomes/bulk` - Create multiple outcomes
- `GET /v1/outcomes/summary/stats` - Get outcome statistics

### **Health**
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API information

## 🔐 **Security Features**

### **Authentication & Authorization**
- **JWT Tokens**: Secure token-based authentication
- **Role-based Access**: Different permissions for different user types
- **Password Hashing**: bcrypt for secure password storage
- **Token Expiration**: Configurable token lifetime

### **Data Protection**
- **Zero-PII Architecture**: No personally identifiable information stored
- **Row-Level Security**: Database-level data isolation
- **CORS Protection**: Cross-origin request protection
- **Input Validation**: Comprehensive data validation

### **API Security**
- **Rate Limiting**: Protection against abuse
- **Request Validation**: Pydantic schema validation
- **Error Handling**: Secure error responses
- **Logging**: Comprehensive audit trail

## 📈 **Data Models**

### **Users**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    vsa_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **Referrals**
```sql
CREATE TABLE referrals (
    referral_token VARCHAR(255) PRIMARY KEY,
    issued_at TIMESTAMP NOT NULL,
    vsa_id VARCHAR(50) NOT NULL,
    program_code VARCHAR(50) NOT NULL,
    episode_id VARCHAR(50),
    referral_type VARCHAR(50) NOT NULL,
    priority_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **Outcomes**
```sql
CREATE TABLE outcomes (
    id VARCHAR(50) PRIMARY KEY,
    referral_token VARCHAR(255) REFERENCES referrals(referral_token),
    vsa_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    reason_code VARCHAR(20),
    first_contact_at TIMESTAMP,
    closed_at TIMESTAMP,
    notes TEXT,
    updated_by VARCHAR(50) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 **Deployment**

### **AWS Deployment**

1. **Configure AWS credentials**
```bash
aws configure
```

2. **Initialize Terraform**
```bash
cd infrastructure
terraform init
```

3. **Plan deployment**
```bash
terraform plan
```

4. **Deploy infrastructure**
```bash
terraform apply
```

### **Docker Deployment**

1. **Build images**
```bash
docker build -t vrp-backend ./backend
docker build -t vrp-frontend ./frontend
```

2. **Run containers**
```bash
docker run -p 8000:8000 vrp-backend
docker run -p 3001:3000 vrp-frontend
```

## 🧪 **Testing**

### **Backend Testing**
```bash
cd backend
python -m pytest tests/
```

### **Frontend Testing**
```bash
cd frontend
npm test
```

### **API Testing**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test login
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=vsa_admin_2&password=newpassword456"
```

## 📚 **Documentation**

- **[Phase 1 Complete](PHASE1_COMPLETE.md)** - Core setup and basic API
- **[Phase 2 Complete](PHASE2_COMPLETE.md)** - Authentication and authorization
- **[Phase 3 Complete](PHASE3_COMPLETE.md)** - Outcomes tracking
- **[Phase 4 Complete](PHASE4_COMPLETE.md)** - Frontend development
- **[Project Status](PROJECT_STATUS.md)** - Current project status
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

For support and questions:
- **Documentation**: Check the docs folder and API documentation
- **Issues**: Create an issue in the repository
- **Email**: Contact the development team

## 🎉 **Acknowledgments**

- **Veterans Crisis Line** for the referral data structure
- **Veteran Service Organizations** for feedback and requirements
- **FastAPI** and **Next.js** communities for excellent documentation
- **AWS** for cloud infrastructure services

---

**Built with ❤️ for veterans and their service organizations**
