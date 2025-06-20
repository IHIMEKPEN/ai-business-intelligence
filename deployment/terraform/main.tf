terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
  
  backend "s3" {
    bucket         = "ai-bi-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "ai-bi-terraform-locks"
  }
}

# Provider Configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "ai-business-intelligence"
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = "ai-bi-team"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

# Data Sources
data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Random Resources
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "random_password" "db_password" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
  upper   = true
  lower   = true
  numeric = true
}

resource "random_password" "grafana_password" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# VPC and Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  
  name = "ai-bi-vpc-${random_string.suffix.result}"
  cidr = var.vpc_cidr
  
  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  
  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true
  
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # EKS specific settings
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true
  
  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }
  
  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }
  
  tags = {
    Environment = var.environment
    Project     = "ai-business-intelligence"
  }
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  cluster_endpoint_public_access = true
  
  eks_managed_node_group_defaults = {
    ami_type               = "AL2_x86_64"
    disk_size              = 50
    instance_types         = ["m5.large", "m5.xlarge"]
    vpc_security_group_ids = [aws_security_group.worker_group.id]
    
    # Enable detailed monitoring
    enable_monitoring = true
    
    # Node group IAM role
    iam_role_additional_policies = {
      AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    }
  }
  
  eks_managed_node_groups = {
    # Application nodes
    app = {
      name = "app-node-group"
      
      instance_types = ["m5.xlarge", "m5.2xlarge"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 2
      max_size     = 10
      desired_size = 3
      
      labels = {
        node-type = "application"
      }
      
      taints = [{
        key    = "node-type"
        value  = "application"
        effect = "NO_SCHEDULE"
      }]
      
      tags = {
        ExtraTag = "app-node-group"
      }
    }
    
    # Database nodes
    db = {
      name = "db-node-group"
      
      instance_types = ["r5.large", "r5.xlarge"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 2
      max_size     = 6
      desired_size = 2
      
      labels = {
        node-type = "database"
      }
      
      taints = [{
        key    = "node-type"
        value  = "database"
        effect = "NO_SCHEDULE"
      }]
      
      tags = {
        ExtraTag = "db-node-group"
      }
    }
    
    # Monitoring nodes
    monitoring = {
      name = "monitoring-node-group"
      
      instance_types = ["m5.large"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 1
      max_size     = 3
      desired_size = 1
      
      labels = {
        node-type = "monitoring"
      }
      
      taints = [{
        key    = "node-type"
        value  = "monitoring"
        effect = "NO_SCHEDULE"
      }]
      
      tags = {
        ExtraTag = "monitoring-node-group"
      }
    }
  }
  
  # Cluster security group
  cluster_security_group_additional_rules = {
    ingress_nodes_443 = {
      description                = "Node groups to cluster API"
      protocol                  = "tcp"
      from_port                 = 443
      to_port                   = 443
      type                      = "ingress"
      source_node_security_group = true
    }
  }
  
  # Node security group
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }
    egress_all = {
      description      = "Node all egress"
      protocol         = "-1"
      from_port        = 0
      to_port          = 0
      type             = "egress"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "ai-business-intelligence"
  }
}

# Security Groups
resource "aws_security_group" "worker_group" {
  name_prefix = "ai-bi-worker-group"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    
    cidr_blocks = [
      "10.0.0.0/8",
    ]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "ai-bi-worker-group"
  }
}

# RDS Database (Optional - for production)
resource "aws_db_subnet_group" "ai_bi" {
  count = var.enable_rds ? 1 : 0
  
  name       = "ai-bi-db-subnet-group"
  subnet_ids = module.vpc.private_subnets
  
  tags = {
    Name = "ai-bi-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  count = var.enable_rds ? 1 : 0
  
  name_prefix = "ai-bi-rds"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.worker_group.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "ai-bi-rds"
  }
}

resource "aws_db_instance" "ai_bi" {
  count = var.enable_rds ? 1 : 0
  
  identifier = "ai-bi-postgres"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r5.large"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_name  = "ai_business_intelligence"
  username = "ai_bi_user"
  password = random_password.db_password.result
  
  vpc_security_group_ids = [aws_security_group.rds[0].id]
  db_subnet_group_name   = aws_db_subnet_group.ai_bi[0].name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "ai-bi-final-snapshot-${random_string.suffix.result}"
  
  deletion_protection = var.environment == "production"
  
  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring[0].arn
  
  tags = {
    Name = "ai-bi-postgres"
  }
}

# RDS Monitoring Role
resource "aws_iam_role" "rds_monitoring" {
  count = var.enable_rds ? 1 : 0
  
  name = "ai-bi-rds-monitoring-role"
  
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
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.enable_rds ? 1 : 0
  
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ElastiCache Redis (Optional - for production)
resource "aws_elasticache_subnet_group" "ai_bi" {
  count = var.enable_elasticache ? 1 : 0
  
  name       = "ai-bi-redis-subnet-group"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  count = var.enable_elasticache ? 1 : 0
  
  name_prefix = "ai-bi-redis"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.worker_group.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "ai-bi-redis"
  }
}

resource "aws_elasticache_cluster" "ai_bi" {
  count = var.enable_elasticache ? 1 : 0
  
  cluster_id           = "ai-bi-redis"
  engine               = "redis"
  node_type            = "cache.r5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  
  subnet_group_name          = aws_elasticache_subnet_group.ai_bi[0].name
  security_group_ids         = [aws_security_group.redis[0].id]
  transit_encryption_enabled = true
  
  tags = {
    Name = "ai-bi-redis"
  }
}

# Application Load Balancer
resource "aws_lb" "ai_bi" {
  name               = "ai-bi-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
  
  enable_deletion_protection = var.environment == "production"
  
  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    prefix  = "alb-logs"
    enabled = true
  }
  
  tags = {
    Name = "ai-bi-alb"
  }
}

resource "aws_security_group" "alb" {
  name_prefix = "ai-bi-alb"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "ai-bi-alb"
  }
}

# S3 Bucket for ALB Logs
resource "aws_s3_bucket" "alb_logs" {
  bucket = "ai-bi-alb-logs-${random_string.suffix.result}"
}

resource "aws_s3_bucket_versioning" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  
  rule {
    id     = "log_rotation"
    status = "Enabled"
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 365
    }
  }
}

# Route53 DNS
resource "aws_route53_zone" "ai_bi" {
  count = var.enable_dns ? 1 : 0
  
  name = var.domain_name
  
  tags = {
    Name = "ai-bi-zone"
  }
}

resource "aws_route53_record" "ai_bi" {
  count = var.enable_dns ? 1 : 0
  
  zone_id = aws_route53_zone.ai_bi[0].zone_id
  name    = var.domain_name
  type    = "A"
  
  alias {
    name                   = aws_lb.ai_bi.dns_name
    zone_id                = aws_lb.ai_bi.zone_id
    evaluate_target_health = true
  }
}

# ACM Certificate
resource "aws_acm_certificate" "ai_bi" {
  count = var.enable_dns ? 1 : 0
  
  domain_name       = var.domain_name
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Name = "ai-bi-certificate"
  }
}

resource "aws_route53_record" "cert_validation" {
  count = var.enable_dns ? 1 : 0
  
  for_each = {
    for dvo in aws_acm_certificate.ai_bi[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.ai_bi[0].zone_id
}

resource "aws_acm_certificate_validation" "ai_bi" {
  count = var.enable_dns ? 1 : 0
  
  certificate_arn         = aws_acm_certificate.ai_bi[0].arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation[0] : record.fqdn]
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "ai_bi_app" {
  name              = "/aws/eks/ai-bi/app"
  retention_in_days = 30
  
  tags = {
    Name = "ai-bi-app-logs"
  }
}

resource "aws_cloudwatch_log_group" "ai_bi_db" {
  name              = "/aws/eks/ai-bi/db"
  retention_in_days = 30
  
  tags = {
    Name = "ai-bi-db-logs"
  }
}

# Outputs
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "db_endpoint" {
  description = "RDS endpoint"
  value       = var.enable_rds ? aws_db_instance.ai_bi[0].endpoint : null
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = var.enable_elasticache ? aws_elasticache_cluster.ai_bi[0].cache_nodes[0].address : null
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.ai_bi.dns_name
}

output "domain_name" {
  description = "Domain name"
  value       = var.enable_dns ? var.domain_name : null
} 