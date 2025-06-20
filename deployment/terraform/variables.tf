# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# EKS Configuration
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "ai-bi-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

# Node Group Configuration
variable "app_node_instance_types" {
  description = "Instance types for application nodes"
  type        = list(string)
  default     = ["m5.xlarge", "m5.2xlarge"]
}

variable "db_node_instance_types" {
  description = "Instance types for database nodes"
  type        = list(string)
  default     = ["r5.large", "r5.xlarge"]
}

variable "monitoring_node_instance_types" {
  description = "Instance types for monitoring nodes"
  type        = list(string)
  default     = ["m5.large"]
}

variable "app_node_min_size" {
  description = "Minimum size of application node group"
  type        = number
  default     = 2
}

variable "app_node_max_size" {
  description = "Maximum size of application node group"
  type        = number
  default     = 10
}

variable "app_node_desired_size" {
  description = "Desired size of application node group"
  type        = number
  default     = 3
}

variable "db_node_min_size" {
  description = "Minimum size of database node group"
  type        = number
  default     = 2
}

variable "db_node_max_size" {
  description = "Maximum size of database node group"
  type        = number
  default     = 6
}

variable "db_node_desired_size" {
  description = "Desired size of database node group"
  type        = number
  default     = 2
}

variable "monitoring_node_min_size" {
  description = "Minimum size of monitoring node group"
  type        = number
  default     = 1
}

variable "monitoring_node_max_size" {
  description = "Maximum size of monitoring node group"
  type        = number
  default     = 3
}

variable "monitoring_node_desired_size" {
  description = "Desired size of monitoring node group"
  type        = number
  default     = 1
}

# Database Configuration
variable "enable_rds" {
  description = "Enable RDS PostgreSQL instance"
  type        = bool
  default     = false
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r5.large"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "RDS maximum allocated storage in GB"
  type        = number
  default     = 1000
}

variable "db_backup_retention_period" {
  description = "RDS backup retention period in days"
  type        = number
  default     = 7
}

# Redis Configuration
variable "enable_elasticache" {
  description = "Enable ElastiCache Redis cluster"
  type        = bool
  default     = false
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.r5.large"
}

variable "redis_num_cache_nodes" {
  description = "Number of ElastiCache Redis cache nodes"
  type        = number
  default     = 1
}

# DNS Configuration
variable "enable_dns" {
  description = "Enable Route53 DNS and ACM certificate"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "ai-bi.example.com"
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable monitoring stack (Prometheus, Grafana)"
  type        = bool
  default     = true
}

variable "prometheus_retention_days" {
  description = "Prometheus data retention in days"
  type        = number
  default     = 30
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  default     = ""
  sensitive   = true
}

# Security Configuration
variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

variable "enable_alb_access_logs" {
  description = "Enable ALB access logs"
  type        = bool
  default     = true
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for production resources"
  type        = bool
  default     = true
}

# Tags
variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "ai-business-intelligence"
    ManagedBy   = "terraform"
    Owner       = "ai-bi-team"
  }
}

# API Keys (sensitive)
variable "alpha_vantage_api_key" {
  description = "Alpha Vantage API key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "finnhub_api_key" {
  description = "Finnhub API key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  default     = ""
  sensitive   = true
}

# SMTP Configuration
variable "smtp_host" {
  description = "SMTP host for email notifications"
  type        = string
  default     = ""
}

variable "smtp_port" {
  description = "SMTP port"
  type        = number
  default     = 587
}

variable "smtp_username" {
  description = "SMTP username"
  type        = string
  default     = ""
  sensitive   = true
}

variable "smtp_password" {
  description = "SMTP password"
  type        = string
  default     = ""
  sensitive   = true
}

# Webhook Configuration
variable "webhook_url" {
  description = "Webhook URL for notifications"
  type        = string
  default     = ""
}

variable "webhook_secret" {
  description = "Webhook secret"
  type        = string
  default     = ""
  sensitive   = true
}

# Monitoring Configuration
variable "sentry_dsn" {
  description = "Sentry DSN for error tracking"
  type        = string
  default     = ""
  sensitive   = true
}

variable "prometheus_token" {
  description = "Prometheus authentication token"
  type        = string
  default     = ""
  sensitive   = true
} 