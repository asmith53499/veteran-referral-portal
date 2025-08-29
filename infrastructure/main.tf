# Veteran Referral Portal - Main Infrastructure Configuration
# This file sets up the AWS provider and main infrastructure components

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration for state management
  # Uncomment and configure when ready to use remote state
  # backend "s3" {
  #   bucket = "vrp-terraform-state-754965642394"
  #   key    = "veteran-referral-portal/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# AWS Provider configuration
provider "aws" {
  region = "us-east-1"
  
  default_tags {
    tags = local.standard_tags
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local variables and tags (imported from tags.tf)
locals {
  # Project identification
  project_name = "veteran-referral-portal"
  project_short = "vrp"
  
  # Environment (change this per deployment)
  environment = "dev"
  
  # Cost allocation
  cost_center = "VRP-2024"
  owner = "asmith53499"
  
  # Standard tags applied to all resources
  standard_tags = {
    Project     = local.project_name
    Environment = local.environment
    Owner       = local.owner
    CostCenter  = local.cost_center
    ManagedBy   = "terraform"
    Purpose     = "Veteran referral outcomes tracking"
    DataClass   = "non-pii"
    Compliance  = "va-standards"
  }
  
  # Naming convention
  name_prefix = "${local.project_short}-${local.environment}"
  
  # Account and region info
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
}

# Outputs
output "project_info" {
  description = "Project information and configuration"
  value = {
    project_name = local.project_name
    environment  = local.environment
    account_id   = local.account_id
    region       = local.region
    name_prefix  = local.name_prefix
  }
}

output "standard_tags" {
  description = "Standard tags applied to all resources"
  value       = local.standard_tags
}
