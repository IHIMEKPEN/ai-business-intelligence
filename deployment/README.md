# AI Business Intelligence System - Deployment Guide

This directory contains the complete deployment configuration for the AI Business Intelligence system using Kubernetes and Terraform on AWS.

## 🏗️ Architecture Overview

The system is deployed on AWS EKS with the following components:

### Infrastructure (Terraform)
- **EKS Cluster** with multiple node groups (app, db, monitoring)
- **VPC** with public/private subnets across 3 AZs
- **RDS PostgreSQL** (optional for production)
- **ElastiCache Redis** (optional for production)
- **Application Load Balancer** with SSL/TLS
- **Route53 DNS** and ACM certificates
- **CloudWatch** logging and monitoring
- **IAM Roles** and policies for service accounts

### Application (Kubernetes)
- **Multi-agent AI system** with autoscaling
- **PostgreSQL** StatefulSet (if not using RDS)
- **Redis** StatefulSet (if not using ElastiCache)
- **Prometheus & Grafana** monitoring stack
- **Ingress-NGINX** controller with security headers
- **Cert-Manager** for SSL/TLS certificates
- **Network Policies** for security

## 📋 Prerequisites

### Required Tools
- **Terraform** >= 1.0
- **kubectl** >= 1.28
- **helm** >= 3.0
- **aws-cli** >= 2.0
- **docker** >= 20.0

### AWS Requirements
- AWS Account with appropriate permissions
- S3 bucket for Terraform state (create manually)
- DynamoDB table for Terraform locks (create manually)

### API Keys
- Alpha Vantage API key
- Finnhub API key
- OpenAI API key
- Domain name (optional)

## 🚀 Quick Start

### 1. Prepare AWS Infrastructure

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://ai-bi-terraform-state --region us-west-2

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name ai-bi-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-west-2
```

### 2. Configure Terraform

```bash
cd deployment/terraform

# Copy and edit the example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

### 3. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the infrastructure
terraform apply
```

### 4. Build and Push Docker Image

```bash
# Build the application image
docker build -t ai-business-intelligence:latest ../

# Tag for your registry
docker tag ai-business-intelligence:latest your-registry/ai-business-intelligence:latest

# Push to registry
docker push your-registry/ai-business-intelligence:latest
```

### 5. Deploy Application

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name ai-bi-cluster

# Create secrets (replace with your actual values)
kubectl create secret generic ai-bi-secrets \
  --from-literal=DB_PASSWORD=your-db-password \
  --from-literal=JWT_SECRET=your-jwt-secret \
  --from-literal=ALPHA_VANTAGE_API_KEY=your-api-key \
  --from-literal=FINNHUB_API_KEY=your-api-key \
  --from-literal=OPENAI_API_KEY=your-api-key \
  --namespace ai-business-intelligence

# Deploy using Kustomize
kubectl apply -k deployment/kubernetes/
```

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Yes |
| `FINNHUB_API_KEY` | Finnhub API key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `ENVIRONMENT` | Environment name | No |

### Scaling Configuration

The system includes automatic scaling:

- **Horizontal Pod Autoscaler**: Scales based on CPU (70%) and memory (80%) usage
- **Cluster Autoscaler**: Scales node groups based on pod scheduling needs
- **Min/Max Replicas**: 3-20 for application pods

### Security Features

- **Network Policies**: Restrict pod-to-pod communication
- **Security Context**: Non-root containers with dropped capabilities
- **RBAC**: Role-based access control
- **Secrets Management**: Kubernetes secrets with encryption
- **SSL/TLS**: Automatic certificate management with Let's Encrypt
- **Security Headers**: Comprehensive security headers in ingress

## 📊 Monitoring

### Prometheus Metrics

The application exposes metrics on `/metrics` endpoint:

- HTTP request metrics
- Application-specific metrics
- Database connection metrics
- Agent performance metrics

### Grafana Dashboards

Pre-configured dashboards for:

- Application performance
- Database metrics
- Infrastructure monitoring
- Business metrics

### Alerting

Prometheus alerting rules for:

- High CPU/Memory usage
- Pod failures
- Database connection issues
- High error rates
- Slow response times

## 🔒 Security Best Practices

### Network Security
- All pods run in private subnets
- Public access only through ALB
- Network policies restrict communication
- VPC Flow Logs enabled

### Application Security
- Non-root containers
- Read-only root filesystem
- Dropped capabilities
- Security context configured
- Image scanning recommended

### Data Security
- Secrets encrypted at rest
- TLS encryption in transit
- Database encryption enabled
- Backup encryption

## 🛠️ Maintenance

### Updates

```bash
# Update application
kubectl set image deployment/ai-bi-app ai-bi-app=your-registry/ai-business-intelligence:new-version

# Update infrastructure
terraform plan
terraform apply
```

### Backup

```bash
# Database backup (if using RDS)
aws rds create-db-snapshot \
  --db-instance-identifier ai-bi-postgres \
  --db-snapshot-identifier ai-bi-backup-$(date +%Y%m%d)

# Application data backup
kubectl exec -it ai-bi-postgres-0 -- pg_dump -U ai_bi_user ai_business_intelligence > backup.sql
```

### Monitoring

```bash
# Check pod status
kubectl get pods -n ai-business-intelligence

# Check logs
kubectl logs -f deployment/ai-bi-app -n ai-business-intelligence

# Check metrics
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
```

## 🚨 Troubleshooting

### Common Issues

1. **Pod Startup Issues**
   ```bash
   kubectl describe pod <pod-name> -n ai-business-intelligence
   kubectl logs <pod-name> -n ai-business-intelligence
   ```

2. **Database Connection Issues**
   ```bash
   kubectl exec -it ai-bi-postgres-0 -- psql -U ai_bi_user -d ai_business_intelligence
   ```

3. **Ingress Issues**
   ```bash
   kubectl describe ingress ai-bi-ingress -n ai-business-intelligence
   kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx
   ```

4. **Terraform Issues**
   ```bash
   terraform refresh
   terraform plan -refresh-only
   ```

### Health Checks

```bash
# Application health
curl https://your-domain.com/health

# Database health
kubectl exec -it ai-bi-postgres-0 -- pg_isready -U ai_bi_user

# Redis health
kubectl exec -it ai-bi-redis-0 -- redis-cli ping
```

## 📈 Performance Optimization

### Resource Tuning

- **CPU/Memory**: Adjust based on workload
- **Storage**: Use fast-ssd storage class
- **Network**: Optimize pod placement
- **Caching**: Configure Redis appropriately

### Scaling Strategies

- **Horizontal**: Add more pods
- **Vertical**: Increase resource limits
- **Cluster**: Add more nodes
- **Database**: Use read replicas

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to EKS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name ai-bi-cluster
      - name: Deploy
        run: kubectl apply -k deployment/kubernetes/
```

## 📚 Additional Resources

- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Helm Charts](https://helm.sh/docs/)

## 🤝 Support

For issues and questions:

1. Check the troubleshooting section
2. Review application logs
3. Check Kubernetes events
4. Consult the monitoring dashboards
5. Open an issue in the repository

---

**Note**: This deployment is designed for production use with security, scalability, and monitoring in mind. Always test in a staging environment first and ensure all secrets are properly configured. 