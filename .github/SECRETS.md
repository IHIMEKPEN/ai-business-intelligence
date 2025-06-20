# GitHub Actions Secrets Configuration

This document lists all the secrets that need to be configured in your GitHub repository for the CI/CD pipelines to work properly.

## 🔐 Required Secrets

### AWS Credentials
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID for EKS deployment | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key for EKS deployment | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |

### Docker Registry
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKER_REGISTRY` | Docker registry URL | `ghcr.io/your-username` or `your-registry.com` |
| `DOCKER_USERNAME` | Docker registry username | `your-username` |
| `DOCKER_PASSWORD` | Docker registry password/token | `your-password-or-token` |

### Terraform Backend
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TERRAFORM_STATE_BUCKET` | S3 bucket name for Terraform state | `ai-bi-terraform-state-123456789012` |
| `TERRAFORM_LOCK_TABLE` | DynamoDB table name for Terraform locks | `ai-bi-terraform-locks` |

### API Keys
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key for financial data | `your-alpha-vantage-key` |
| `FINNHUB_API_KEY` | Finnhub API key for market data | `your-finnhub-key` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-your-openai-key` |

### Application Secrets
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DB_PASSWORD` | Production database password | `your-secure-db-password` |
| `JWT_SECRET` | JWT signing secret | `your-jwt-secret-key` |
| `GRAFANA_PASSWORD` | Grafana admin password | `your-grafana-password` |

### Staging Environment Secrets
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `STAGING_DB_PASSWORD` | Staging database password | `staging-db-password` |
| `STAGING_JWT_SECRET` | Staging JWT secret | `staging-jwt-secret` |
| `STAGING_GRAFANA_PASSWORD` | Staging Grafana password | `staging-grafana-password` |

### Monitoring and Notifications
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SENTRY_DSN` | Sentry DSN for error tracking | `https://your-sentry-dsn` |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | `https://hooks.slack.com/services/...` |

### SMTP Configuration
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password/app password | `your-smtp-password` |

### Webhook Configuration
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `WEBHOOK_URL` | Webhook URL for notifications | `https://your-webhook-url.com/endpoint` |
| `WEBHOOK_SECRET` | Webhook secret for verification | `your-webhook-secret` |

## 🔧 How to Configure Secrets

### 1. Go to Repository Settings
1. Navigate to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click on **Secrets and variables** → **Actions**

### 2. Add Secrets
1. Click **New repository secret**
2. Enter the secret name (exactly as listed above)
3. Enter the secret value
4. Click **Add secret**

### 3. Environment-Specific Secrets
For environment-specific secrets (like staging vs production), you can also configure them at the environment level:

1. Go to **Settings** → **Environments**
2. Create environments: `staging` and `production`
3. Add environment-specific secrets

## 🛡️ Security Best Practices

### 1. Secret Rotation
- Rotate secrets regularly (every 90 days)
- Use different secrets for different environments
- Never commit secrets to the repository

### 2. Access Control
- Use least-privilege IAM roles for AWS credentials
- Use service accounts for Kubernetes access
- Limit who can access repository secrets

### 3. Secret Management
- Consider using AWS Secrets Manager or HashiCorp Vault for production
- Use environment variables for local development
- Never log or display secret values

### 4. Monitoring
- Monitor secret usage and access
- Set up alerts for unusual access patterns
- Regularly audit secret permissions

## 🔍 Verification

### Test Secret Configuration
You can test if secrets are properly configured by running a simple workflow:

```yaml
name: Test Secrets
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test AWS credentials
        run: |
          aws sts get-caller-identity
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: us-west-2
```

### Common Issues

1. **Secret not found**: Make sure the secret name matches exactly (case-sensitive)
2. **Permission denied**: Check IAM permissions for AWS credentials
3. **Invalid format**: Ensure secrets are properly formatted (no extra spaces, correct encoding)

## 📋 Checklist

Before running the CI/CD pipeline, ensure you have configured:

- [ ] AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- [ ] Docker registry credentials (`DOCKER_REGISTRY`, `DOCKER_USERNAME`, `DOCKER_PASSWORD`)
- [ ] Terraform backend configuration (`TERRAFORM_STATE_BUCKET`, `TERRAFORM_LOCK_TABLE`)
- [ ] API keys (`ALPHA_VANTAGE_API_KEY`, `FINNHUB_API_KEY`, `OPENAI_API_KEY`)
- [ ] Application secrets (`DB_PASSWORD`, `JWT_SECRET`, `GRAFANA_PASSWORD`)
- [ ] Staging secrets (if using staging environment)
- [ ] Notification webhooks (`SLACK_WEBHOOK_URL`, `WEBHOOK_URL`)

## 🚨 Emergency Procedures

### If Secrets are Compromised
1. Immediately rotate all affected secrets
2. Revoke and regenerate API keys
3. Check for unauthorized access
4. Update all environments with new secrets
5. Monitor for suspicious activity

### Backup and Recovery
- Keep secure backups of secret values
- Document secret rotation procedures
- Have emergency contact procedures ready 