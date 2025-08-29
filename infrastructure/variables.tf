# Variables for Veteran Referral Portal Infrastructure
# These can be overridden via terraform.tfvars or command line

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "veteran-referral-portal"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "database_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"  # Small for dev, increase for prod
  
  validation {
    condition     = can(regex("^db\\..*", var.database_instance_class))
    error_message = "Database instance class must start with 'db.'"
  }
}

variable "database_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
  
  validation {
    condition     = var.database_allocated_storage >= 20
    error_message = "Database storage must be at least 20 GB"
  }
}

variable "database_name" {
  description = "Name of the database to create"
  type        = string
  default     = "veteran_referral_portal"
}

variable "database_username" {
  description = "Database master username"
  type        = string
  default     = "vrp_admin"
  
  validation {
    condition     = length(var.database_username) >= 3
    error_message = "Database username must be at least 3 characters"
  }
}

variable "enable_public_access" {
  description = "Enable public access to RDS (for dev only)"
  type        = bool
  default     = false
}

variable "enable_backup_retention" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
  
  validation {
    condition     = var.backup_retention_period >= 1 && var.backup_retention_period <= 35
    error_message = "Backup retention must be between 1 and 35 days"
  }
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
