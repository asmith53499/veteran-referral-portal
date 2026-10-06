# Veteran Referral Portal - Infrastructure

This directory contains the Terraform infrastructure configuration for the Veteran Referral Outcomes Portal project.

## Cost Isolation Strategy

The infrastructure is designed to provide **project-level cost isolation** without requiring separate AWS accounts:

### 1. Resource Groups
- **Veteran-Referral-Portal** resource group automatically organizes all project resources
- Resources are filtered by the `Project` tag

### 2. Cost Allocation Tags
All resources are tagged with:
- `Project: veteran-referral-portal`
- `Environment: dev/staging/prod`
- `CostCenter: VRP-2024`
- `Owner: asmith53499`
- `DataClass: non-pii`
- `Compliance: va-standards`

### 3. Cost Monitoring
- **Monthly budget** with alerts at 80% and 100%
- **Cost and Usage Reports** for detailed billing analysis
- **Cost Explorer** filtering by project tags

## Infrastructure Components

### Network Layer
- **VPC**: `10.0.0.0/16` with isolated subnets
- **Public Subnets**: For ALB and bastion hosts
- **Private Subnets**: For ECS tasks and application services
- **Database Subnets**: For RDS instances

### Security
- **Row-Level Security** (RLS) for multi-tenant data isolation
- **Encrypted storage** for all data at rest
- **Network isolation** with security groups
- **IAM roles** with least-privilege access

### Database
- **PostgreSQL RDS** with RLS policies
- **Multi-AZ deployment** for high availability
- **Automated backups** with configurable retention
- **Performance Insights** for monitoring

## Deployment

### Prerequisites
1. **AWS CLI** configured with appropriate permissions
2. **Terraform** installed (version >= 1.0)
3. **AWS credentials** with infrastructure deployment permissions

### Quick Deploy
```bash
# From project root
./scripts/deploy_infrastructure.sh
```

### Manual Deploy
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

## Cost Tracking

### View Project Costs
1. **AWS Cost Explorer** → Filter by `Project:veteran-referral-portal`
2. **Cost and Usage Reports** → Available in S3 bucket
3. **Budgets** → Monthly budget with email notifications

### Resource Organization
- **Resource Groups** → Veteran-Referral-Portal group
- **Tag Editor** → Bulk tag management
- **Cost Allocation Tags** → Automated tag activation

## Environment Management

### Development
- `environment = "dev"`
- Smaller instance sizes
- Public access enabled for testing
- Minimal backup retention

### Staging
- `environment = "staging"`
- Medium instance sizes
- Private access only
- Standard backup retention

### Production
- `environment = "prod"`
- Production instance sizes
- Private access only
- Extended backup retention
- Multi-AZ deployment

## Security Considerations

### Data Protection
- **Zero PII storage** in shared systems
- **Encrypted connections** (TLS 1.3)
- **Audit logging** for all operations
- **Access controls** by VSA organization

### Network Security
- **Private subnets** for sensitive services
- **Security groups** with minimal required access
- **VPC endpoints** for AWS service access
- **Network ACLs** for additional layer

## Monitoring and Alerting

### CloudWatch
- **Metrics** for all AWS services
- **Logs** for application and infrastructure
- **Alarms** for cost thresholds and performance

### Budget Alerts
- **80% threshold** → Warning notification
- **100% threshold** → Critical notification
- **Email delivery** to project stakeholders

## Cleanup

### Destroy Infrastructure
```bash
cd infrastructure
terraform destroy
```

### Verify Cleanup
- Check **Resource Groups** for remaining resources
- Review **Cost Explorer** for ongoing charges
- Verify **S3 buckets** are empty and deleted

## Next steps

This provisions networking, the database, and cost tracking - not application hosting. After `terraform apply`:
1. Apply `database/schema.sql` and `database/users_schema.sql` against the new RDS instance (`../scripts/init_database.sh`).
2. Run the FastAPI backend somewhere that can reach it (not yet automated - see the root `DEPLOYMENT.md`).
3. Point the frontend's `NEXT_PUBLIC_API_URL` at that backend.
