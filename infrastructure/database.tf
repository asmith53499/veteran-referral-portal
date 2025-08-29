# PostgreSQL RDS Database Configuration
# Sets up the database for Veteran Referral Portal with proper security and RLS support

# Security Group for RDS
resource "aws_security_group" "database" {
  name_prefix = "${local.name_prefix}-database-sg"
  vpc_id      = aws_vpc.main.id
  description = "Security group for PostgreSQL RDS instance"
  
  # Allow PostgreSQL access from private subnets only
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
    description     = "PostgreSQL access from ECS tasks"
  }
  
  # Allow access from bastion host (if needed for dev)
  dynamic "ingress" {
    for_each = var.enable_public_access ? [1] : []
    content {
      from_port       = 5432
      to_port         = 5432
      protocol        = "tcp"
      security_groups = [aws_security_group.bastion.id]
      description     = "PostgreSQL access from bastion host"
    }
  }
  
  # Temporary development access - REMOVE BEFORE PRODUCTION
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["75.62.78.122/32"]
    description = "Temporary development access - REMOVE BEFORE PRODUCTION"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-database-sg"
    Type = "security-group"
  })
}

# Subnet Group for RDS
resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-database-subnet-group"
  subnet_ids = aws_subnet.database[*].id
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-database-subnet-group"
    Type = "subnet-group"
  })
}

# Parameter Group for PostgreSQL
resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "${local.name_prefix}-postgres-params"
  
  # Note: RLS is enabled by default in PostgreSQL 15
  # We don't need to set rls.force_enable parameter
  
  parameter {
    name  = "log_statement"
    value = "all"
  }
  
  parameter {
    name  = "log_connections"
    value = "1"
  }
  
  parameter {
    name  = "log_disconnections"
    value = "1"
  }
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-postgres-params"
    Type = "parameter-group"
  })
}

# Option Group for PostgreSQL
resource "aws_db_option_group" "main" {
  name                     = "${local.name_prefix}-postgres-options"
  engine_name              = "postgres"
  major_engine_version     = "15"
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-postgres-options"
    Type = "option-group"
  })
}

# PostgreSQL RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${local.name_prefix}-postgres"
  
  # Engine configuration
  engine         = "postgres"
  engine_version = "15.7"
  instance_class = var.database_instance_class
  
  # Storage configuration
  allocated_storage     = var.database_allocated_storage
  max_allocated_storage = var.database_allocated_storage * 2
  storage_type          = "gp3"
  storage_encrypted     = true
  
  # Database configuration
  db_name  = var.database_name
  username = var.database_username
  password = random_password.database.result
  
  # Network configuration
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  # Availability and backup
  multi_az               = var.environment == "prod" ? true : false
  backup_retention_period = var.enable_backup_retention ? var.backup_retention_period : 0
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Performance and monitoring
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn
  
  # Security
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment == "prod" ? false : true
  
  # Parameter and option groups
  parameter_group_name = aws_db_parameter_group.main.name
  option_group_name    = aws_db_option_group.main.name
  
  # Public access (dev only)
  publicly_accessible = var.enable_public_access
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-postgres"
    Type = "database"
  })
  
  depends_on = [
    aws_vpc.main,
    aws_subnet.database,
    aws_security_group.database,
    aws_db_subnet_group.main
  ]
}

# Random password for database
resource "random_password" "database" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# IAM Role for RDS monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${local.name_prefix}-rds-monitoring-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-rds-monitoring-role"
    Type = "iam-role"
  })
}

# Attach monitoring policy to role
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Security Group for ECS (referenced by database security group)
resource "aws_security_group" "ecs" {
  name_prefix = "${local.name_prefix}-ecs-sg"
  vpc_id      = aws_vpc.main.id
  description = "Security group for ECS tasks"
  
  # Allow outbound to database
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-ecs-sg"
    Type = "security-group"
  })
}

# Security Group for Bastion (referenced by database security group)
resource "aws_security_group" "bastion" {
  name_prefix = "${local.name_prefix}-bastion-sg"
  vpc_id      = aws_vpc.main.id
  description = "Security group for bastion host"
  
  # Allow SSH access from your IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Restrict to your IP in production
    description = "SSH access"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-bastion-sg"
    Type = "security-group"
  })
}

# Outputs
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "Database master username"
  value       = aws_db_instance.main.username
}

output "database_password" {
  description = "Database master password"
  value       = random_password.database.result
  sensitive   = true
}

output "database_port" {
  description = "Database port"
  value       = aws_db_instance.main.port
}
