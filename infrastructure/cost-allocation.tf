# Cost Allocation Tags Configuration
# This ensures all resources are properly tagged for cost tracking and billing separation

# Note: Cost allocation tags are automatically activated when resources are tagged
# We don't need to manually create them - AWS will activate them automatically

# Budget for cost monitoring
resource "aws_budgets_budget" "monthly" {
  name              = "${local.name_prefix}-monthly-budget"
  budget_type       = "COST"
  limit_amount      = "1000"
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"
  
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = ["asmith53499@example.com"]  # Update with real email
  }
  
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = ["asmith53499@example.com"]  # Update with real email
  }
  
  tags = local.standard_tags
}

# Note: Cost and Usage Reports require special AWS permissions
# We'll skip this for now and focus on the core infrastructure
# Cost tracking will still work through tags and budgets

# S3 bucket for cost reports
resource "aws_s3_bucket" "cost_reports" {
  bucket = "${local.name_prefix}-cost-reports-${local.account_id}"
  
  tags = merge(local.standard_tags, {
    Name = "${local.name_prefix}-cost-reports"
    Type = "cost-reports"
  })
}

# S3 bucket versioning for cost reports
resource "aws_s3_bucket_versioning" "cost_reports" {
  bucket = aws_s3_bucket.cost_reports.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket server-side encryption for cost reports
resource "aws_s3_bucket_server_side_encryption_configuration" "cost_reports" {
  bucket = aws_s3_bucket.cost_reports.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket public access block for cost reports
resource "aws_s3_bucket_public_access_block" "cost_reports" {
  bucket = aws_s3_bucket.cost_reports.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
