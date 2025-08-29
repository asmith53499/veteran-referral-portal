#!/bin/bash

# Veteran Referral Portal - Infrastructure Deployment Script
# This script deploys the AWS infrastructure with proper cost allocation and tagging

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "infrastructure/main.tf" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Get current AWS account info
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)

print_status "Deploying to AWS Account: $ACCOUNT_ID in Region: $REGION"

# Change to infrastructure directory
cd infrastructure

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install Terraform first."
    exit 1
fi

print_status "Initializing Terraform..."
terraform init

print_status "Validating Terraform configuration..."
terraform validate

print_status "Planning Terraform deployment..."
terraform plan -out=tfplan

print_status "Deploying infrastructure..."
terraform apply tfplan

print_status "Infrastructure deployment complete!"

# Get outputs
print_status "Infrastructure outputs:"
terraform output

# Show cost allocation setup
print_status "Setting up cost allocation tags..."
aws resource-groups list-groups --query "Groups[?Name=='Veteran-Referral-Portal']" --output table

print_status "Cost allocation setup complete!"
print_status "You can now view costs by project in AWS Cost Explorer using the 'Project' tag"

# Clean up plan file
rm -f tfplan

print_status "Deployment script completed successfully!"
print_status "Next steps:"
print_status "1. Set up the database schema"
print_status "2. Deploy the FastAPI backend"
print_status "3. Deploy the React frontend"
print_status "4. Test the CSV intake process"
