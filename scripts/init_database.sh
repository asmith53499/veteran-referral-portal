#!/bin/bash

# Veteran Referral Portal - Database Initialization Script
# This script initializes the PostgreSQL database with schema and sample data

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
if [ ! -f "database/schema.sql" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if psql is available
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL client (psql) is not installed. Please install it first."
    exit 1
fi

# Get database connection details from Terraform output
print_status "Getting database connection details from Terraform..."

cd infrastructure

if [ ! -f "terraform.tfstate" ]; then
    print_error "Terraform state file not found. Please run 'terraform apply' first."
    exit 1
fi

# Extract database connection details
DB_ENDPOINT=$(terraform output -raw database_endpoint 2>/dev/null || echo "")
DB_NAME=$(terraform output -raw database_name 2>/dev/null || echo "")
DB_USERNAME=$(terraform output -raw database_username 2>/dev/null || echo "")
DB_PASSWORD=$(terraform output -raw database_password 2>/dev/null || echo "")
DB_PORT=$(terraform output -raw database_port 2>/dev/null || echo "5432")

cd ..

if [ -z "$DB_ENDPOINT" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USERNAME" ] || [ -z "$DB_PASSWORD" ]; then
    print_error "Could not retrieve database connection details from Terraform output"
    print_error "Please ensure the infrastructure has been deployed successfully"
    exit 1
fi

print_status "Database connection details retrieved:"
print_status "  Endpoint: $DB_ENDPOINT"
print_status "  Database: $DB_NAME"
print_status "  Username: $DB_USERNAME"
print_status "  Port: $DB_PORT"

# Test database connection
print_status "Testing database connection..."
export PGPASSWORD="$DB_PASSWORD"

if ! psql -h "$DB_ENDPOINT" -U "$DB_USERNAME" -d "$DB_NAME" -p "$DB_PORT" -c "SELECT 1;" > /dev/null 2>&1; then
    print_error "Could not connect to database. Please check:"
    print_error "  1. RDS instance is running and accessible"
    print_error "  2. Security groups allow access from your IP"
    print_error "  3. Database credentials are correct"
    exit 1
fi

print_status "Database connection successful!"

# Initialize database schema
print_status "Initializing database schema..."
psql -h "$DB_ENDPOINT" -U "$DB_USERNAME" -d "$DB_NAME" -p "$DB_PORT" -f database/schema.sql

print_status "Database schema initialized successfully!"

# Verify tables were created
print_status "Verifying database setup..."
psql -h "$DB_ENDPOINT" -U "$DB_USERNAME" -d "$DB_NAME" -p "$DB_PORT" -c "
\dt
"

print_status "Database initialization complete!"
print_status "Next steps:"
print_status "1. Test CSV intake with sample data"
print_status "2. Deploy FastAPI backend"
print_status "3. Test VSA portal functionality"
print_status "4. Onboard pilot VSA partners"

# Clean up password from environment
unset PGPASSWORD
