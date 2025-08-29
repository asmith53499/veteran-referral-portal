# Standard tagging strategy for Veteran Referral Portal project
# This file contains tag-related functions and utilities

# Note: Local variables and outputs are defined in main.tf to avoid duplication
# This file is kept for future tag-related functionality

# Example of how to use the standard tags in other resources:
# tags = merge(local.standard_tags, {
#   Name = "${local.name_prefix}-resource-name"
#   Type = "resource-type"
# })
