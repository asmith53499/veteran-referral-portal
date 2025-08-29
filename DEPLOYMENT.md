# Veteran Referral Outcomes Portal - Deployment Guide

## 🎯 **Overview**

This guide covers deployment of the Veteran Referral Outcomes Portal for both local development and AWS production environments.

## 🏠 **Local Development Deployment**

### **Prerequisites**
- Python 3.13+
- PostgreSQL 15.7+
- Git
- curl (for testing)

### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd project_bridgepoint
```

### **Step 2: Backend Setup**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 3: Database Setup**
```bash
# Create database
createdb veteran_referral_portal

# Apply schema
psql -d veteran_referral_portal -f ../database/schema.sql
psql -d veteran_referral_portal -f ../database/users_schema.sql

# Verify setup
psql -d veteran_referral_portal -c "\dt"
```

### **Step 4: Start Application**
```bash
# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Step 5: Test Deployment**
```bash
# Health check
curl http://localhost:8000/v1/health

# Login test
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=va_admin&password=admin123"

# Import test data
curl -X POST -F "file=@../data/sample_referrals.csv" \
  -F "vsa_id=TEST_VSA_001" \
  http://localhost:8000/v1/referrals/import/csv
```

## ☁️ **AWS Production Deployment**

### **Prerequisites**
- AWS CLI configured with appropriate permissions
- Terraform 1.0+
- Docker (for containerized deployment)

### **Step 1: Infrastructure Deployment**

#### **Configure AWS Credentials**
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

#### **Deploy Infrastructure**
```bash
cd infrastructure

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply infrastructure
terraform apply

# Note the outputs (database endpoint, etc.)
terraform output
```

#### **Infrastructure Components**
- **VPC**: Isolated network environment
- **RDS**: PostgreSQL database in private subnet
- **Security Groups**: Network access controls
- **IAM Roles**: Service permissions
- **Cost Allocation**: Resource tagging for cost tracking

### **Step 2: Database Setup**

#### **Apply Schema**
```bash
# Use the database endpoint from Terraform output
export DB_ENDPOINT=$(terraform output -raw database_endpoint)

# Apply schema
./scripts/init_database.sh
```

#### **Verify Database**
```bash
psql -h $DB_ENDPOINT -U vrp_admin -d veteran_referral_portal -c "\dt"
```

### **Step 3: Application Deployment**

#### **Option A: Docker Deployment**

**Build Docker Image**
```bash
cd backend

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build image
docker build -t veteran-referral-portal:latest .
```

**Deploy to ECS**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name veteran-referral-portal

# Create task definition
aws ecs register-task-definition \
  --family veteran-referral-portal \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 256 \
  --memory 512 \
  --execution-role-arn arn:aws:iam::<account-id>:role/ecsTaskExecutionRole \
  --container-definitions '[
    {
      "name": "veteran-referral-portal",
      "image": "veteran-referral-portal:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://vrp_admin:password@<db-endpoint>:5432/veteran_referral_portal"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/veteran-referral-portal",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]'
```

#### **Option B: EC2 Deployment**

**Launch EC2 Instance**
```bash
# Launch instance with appropriate security group
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.micro \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx
```

**Deploy Application**
```bash
# SSH to instance
ssh -i your-key.pem ec2-user@<instance-ip>

# Install dependencies
sudo yum update -y
sudo yum install -y python3 python3-pip postgresql

# Clone repository
git clone <repository-url>
cd project_bridgepoint/backend

# Install Python dependencies
pip3 install -r requirements.txt

# Start application
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

### **Step 4: Load Balancer Setup**

#### **Create Application Load Balancer**
```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name veteran-referral-portal-alb \
  --subnets subnet-xxxxxxxxx subnet-yyyyyyyy \
  --security-groups sg-xxxxxxxxx

# Create target group
aws elbv2 create-target-group \
  --name veteran-referral-portal-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxxxxxx \
  --target-type ip \
  --health-check-path /v1/health

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn <alb-arn> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<target-group-arn>
```

### **Step 5: Environment Configuration**

#### **Environment Variables**
```bash
# Production environment variables
export DATABASE_URL="postgresql://vrp_admin:password@<db-endpoint>:5432/veteran_referral_portal"
export SECRET_KEY="your-production-secret-key"
export DEBUG=false
export ALLOWED_ORIGINS="https://your-domain.com"
export ALLOWED_HOSTS="your-domain.com"
```

#### **Configuration Files**
```bash
# Create production config
cat > .env.production << EOF
DATABASE_URL=postgresql://vrp_admin:password@<db-endpoint>:5432/veteran_referral_portal
SECRET_KEY=your-production-secret-key
DEBUG=false
ALLOWED_ORIGINS=https://your-domain.com
ALLOWED_HOSTS=your-domain.com
AWS_REGION=us-east-1
EOF
```

## 🔒 **Security Configuration**

### **Database Security**
- **Encryption**: RDS encryption at rest and in transit
- **Network**: Database in private subnet
- **Access**: Security groups restrict access
- **Backup**: Automated backups enabled

### **Application Security**
- **HTTPS**: SSL/TLS encryption
- **Authentication**: JWT tokens with secure expiration
- **Authorization**: Role-based access control
- **Input Validation**: Pydantic schema validation
- **PII Detection**: Built-in sensitive data scanning

### **Network Security**
- **VPC**: Isolated network environment
- **Security Groups**: Restrictive firewall rules
- **NACLs**: Network access control lists
- **WAF**: Web application firewall (optional)

## 📊 **Monitoring & Logging**

### **CloudWatch Setup**
```bash
# Create log group
aws logs create-log-group --log-group-name /aws/veteran-referral-portal

# Create metric filters
aws logs put-metric-filter \
  --log-group-name /aws/veteran-referral-portal \
  --filter-name ErrorCount \
  --filter-pattern "ERROR" \
  --metric-transformations MetricName=ErrorCount,MetricNamespace=VeteranReferralPortal,MetricValue=1
```

### **Health Checks**
```bash
# Test health endpoint
curl https://your-domain.com/v1/health

# Monitor application logs
aws logs tail /aws/veteran-referral-portal --follow
```

### **Performance Monitoring**
- **CloudWatch Metrics**: CPU, memory, network
- **RDS Monitoring**: Database performance
- **Application Metrics**: Response times, error rates
- **Custom Dashboards**: Business metrics

## 🔄 **CI/CD Pipeline**

### **GitHub Actions Workflow**
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy infrastructure
      run: |
        cd infrastructure
        terraform init
        terraform apply -auto-approve
    
    - name: Build and push Docker image
      run: |
        cd backend
        docker build -t veteran-referral-portal .
        docker tag veteran-referral-portal:latest ${{ secrets.ECR_REGISTRY }}/veteran-referral-portal:latest
        docker push ${{ secrets.ECR_REGISTRY }}/veteran-referral-portal:latest
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster veteran-referral-portal --service veteran-referral-portal --force-new-deployment
```

## 🧪 **Testing Deployment**

### **Health Checks**
```bash
# Application health
curl https://your-domain.com/v1/health

# Database connectivity
curl https://your-domain.com/v1/health/detailed

# Authentication
curl -X POST "https://your-domain.com/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=va_admin&password=admin123"
```

### **Load Testing**
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 https://your-domain.com/v1/health
```

### **Security Testing**
```bash
# Test authentication
curl -H "Authorization: Bearer invalid-token" https://your-domain.com/v1/auth/users/me

# Test authorization
curl -H "Authorization: Bearer vsa-token" https://your-domain.com/v1/auth/users
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Database Connection Issues**
```bash
# Check database connectivity
psql -h <db-endpoint> -U vrp_admin -d veteran_referral_portal -c "SELECT 1"

# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
```

#### **Application Startup Issues**
```bash
# Check application logs
aws logs tail /aws/veteran-referral-portal --follow

# Check environment variables
echo $DATABASE_URL
echo $SECRET_KEY
```

#### **Network Issues**
```bash
# Test connectivity
telnet <db-endpoint> 5432

# Check VPC configuration
aws ec2 describe-vpcs --vpc-ids vpc-xxxxxxxxx
```

### **Rollback Procedures**
```bash
# Rollback infrastructure
cd infrastructure
terraform plan -out=rollback.tfplan
terraform apply rollback.tfplan

# Rollback application
aws ecs update-service --cluster veteran-referral-portal --service veteran-referral-portal --task-definition veteran-referral-portal:previous
```

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
- **ECS Auto Scaling**: Scale based on CPU/memory
- **RDS Read Replicas**: Database read scaling
- **ALB**: Load distribution across instances
- **Redis**: Session and cache scaling

### **Vertical Scaling**
- **Instance Types**: Upgrade EC2 instance types
- **RDS Instance**: Upgrade database instance
- **Memory**: Increase application memory allocation

## 💰 **Cost Optimization**

### **Resource Optimization**
- **Spot Instances**: Use spot instances for non-critical workloads
- **Reserved Instances**: Reserve instances for predictable workloads
- **Auto Scaling**: Scale down during low usage
- **Storage Optimization**: Use appropriate storage classes

### **Monitoring Costs**
```bash
# Check current costs
aws ce get-cost-and-usage \
  --time-period Start=2025-08-01,End=2025-08-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

---

**Last Updated**: August 29, 2025  
**Version**: 1.0.0  
**Status**: Ready for Production Deployment
