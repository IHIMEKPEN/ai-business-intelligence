#!/bin/bash

# AI Business Intelligence System - Deployment Script
# This script automates the deployment of the AI BI system to AWS EKS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$SCRIPT_DIR/terraform"
KUBERNETES_DIR="$SCRIPT_DIR/kubernetes"

# Default values
ENVIRONMENT="production"
AWS_REGION="us-west-2"
CLUSTER_NAME="ai-bi-cluster"
NAMESPACE="ai-business-intelligence"
DOCKER_REGISTRY=""
DOCKER_IMAGE="ai-business-intelligence"
DOCKER_TAG="latest"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_tools=()
    
    if ! command_exists terraform; then
        missing_tools+=("terraform")
    fi
    
    if ! command_exists kubectl; then
        missing_tools+=("kubectl")
    fi
    
    if ! command_exists helm; then
        missing_tools+=("helm")
    fi
    
    if ! command_exists aws; then
        missing_tools+=("aws-cli")
    fi
    
    if ! command_exists docker; then
        missing_tools+=("docker")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_error "Please install the missing tools and try again."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to check AWS credentials
check_aws_credentials() {
    print_status "Checking AWS credentials..."
    
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured or invalid"
        print_error "Please run 'aws configure' or set appropriate environment variables"
        exit 1
    fi
    
    local aws_account=$(aws sts get-caller-identity --query Account --output text)
    print_success "AWS credentials configured for account: $aws_account"
}

# Function to create S3 backend for Terraform
setup_terraform_backend() {
    print_status "Setting up Terraform backend..."
    
    local bucket_name="ai-bi-terraform-state-$(aws sts get-caller-identity --query Account --output text)"
    local table_name="ai-bi-terraform-locks"
    
    # Create S3 bucket if it doesn't exist
    if ! aws s3 ls "s3://$bucket_name" >/dev/null 2>&1; then
        print_status "Creating S3 bucket: $bucket_name"
        aws s3 mb "s3://$bucket_name" --region "$AWS_REGION"
        aws s3api put-bucket-versioning --bucket "$bucket_name" --versioning-configuration Status=Enabled
        aws s3api put-bucket-encryption --bucket "$bucket_name" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
    fi
    
    # Create DynamoDB table if it doesn't exist
    if ! aws dynamodb describe-table --table-name "$table_name" >/dev/null 2>&1; then
        print_status "Creating DynamoDB table: $table_name"
        aws dynamodb create-table \
            --table-name "$table_name" \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
            --region "$AWS_REGION"
        
        # Wait for table to be active
        aws dynamodb wait table-exists --table-name "$table_name" --region "$AWS_REGION"
    fi
    
    print_success "Terraform backend configured"
}

# Function to build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    if [ -z "$DOCKER_REGISTRY" ]; then
        print_warning "DOCKER_REGISTRY not set, skipping image push"
        return
    fi
    
    local image_name="$DOCKER_REGISTRY/$DOCKER_IMAGE:$DOCKER_TAG"
    
    # Build image
    print_status "Building Docker image: $image_name"
    docker build -t "$image_name" "$PROJECT_ROOT"
    
    # Push image
    print_status "Pushing Docker image to registry..."
    docker push "$image_name"
    
    print_success "Docker image built and pushed: $image_name"
}

# Function to deploy infrastructure with Terraform
deploy_infrastructure() {
    print_status "Deploying infrastructure with Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_status "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Ask for confirmation
    echo
    print_warning "Review the Terraform plan above. Do you want to proceed with the deployment? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled by user"
        exit 0
    fi
    
    # Apply deployment
    print_status "Applying Terraform configuration..."
    terraform apply tfplan
    
    # Clean up plan file
    rm -f tfplan
    
    print_success "Infrastructure deployed successfully"
}

# Function to configure kubectl
configure_kubectl() {
    print_status "Configuring kubectl for EKS cluster..."
    
    aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"
    
    # Verify cluster access
    if ! kubectl cluster-info >/dev/null 2>&1; then
        print_error "Failed to connect to EKS cluster"
        exit 1
    fi
    
    print_success "kubectl configured for EKS cluster"
}

# Function to create Kubernetes secrets
create_kubernetes_secrets() {
    print_status "Creating Kubernetes secrets..."
    
    # Check if secrets already exist
    if kubectl get secret ai-bi-secrets -n "$NAMESPACE" >/dev/null 2>&1; then
        print_warning "Secrets already exist, skipping creation"
        return
    fi
    
    # Prompt for secrets
    echo
    print_status "Please provide the following secrets:"
    
    read -s -p "Database Password: " DB_PASSWORD
    echo
    read -s -p "JWT Secret: " JWT_SECRET
    echo
    read -s -p "Alpha Vantage API Key: " ALPHA_VANTAGE_API_KEY
    echo
    read -s -p "Finnhub API Key: " FINNHUB_API_KEY
    echo
    read -s -p "OpenAI API Key: " OPENAI_API_KEY
    echo
    read -s -p "Grafana Admin Password: " GRAFANA_PASSWORD
    echo
    
    # Create secrets
    kubectl create secret generic ai-bi-secrets \
        --from-literal=DB_PASSWORD="$DB_PASSWORD" \
        --from-literal=JWT_SECRET="$JWT_SECRET" \
        --from-literal=ALPHA_VANTAGE_API_KEY="$ALPHA_VANTAGE_API_KEY" \
        --from-literal=FINNHUB_API_KEY="$FINNHUB_API_KEY" \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --from-literal=GRAFANA_PASSWORD="$GRAFANA_PASSWORD" \
        --namespace "$NAMESPACE"
    
    print_success "Kubernetes secrets created"
}

# Function to deploy application
deploy_application() {
    print_status "Deploying application to Kubernetes..."
    
    # Update image in kustomization if registry is provided
    if [ -n "$DOCKER_REGISTRY" ]; then
        local image_name="$DOCKER_REGISTRY/$DOCKER_IMAGE:$DOCKER_TAG"
        sed -i.bak "s|newName: ai-business-intelligence|newName: $DOCKER_REGISTRY/$DOCKER_IMAGE|g" \
            "$KUBERNETES_DIR/kustomization.yaml"
        sed -i.bak "s|newTag: latest|newTag: $DOCKER_TAG|g" \
            "$KUBERNETES_DIR/kustomization.yaml"
    fi
    
    # Deploy using Kustomize
    kubectl apply -k "$KUBERNETES_DIR"
    
    # Wait for deployment to be ready
    print_status "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/ai-bi-app -n "$NAMESPACE"
    
    print_success "Application deployed successfully"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Check pod status
    print_status "Checking pod status..."
    kubectl get pods -n "$NAMESPACE"
    
    # Check services
    print_status "Checking services..."
    kubectl get services -n "$NAMESPACE"
    
    # Check ingress
    print_status "Checking ingress..."
    kubectl get ingress -n "$NAMESPACE"
    
    # Check if application is responding
    print_status "Checking application health..."
    local ingress_host=$(kubectl get ingress ai-bi-ingress -n "$NAMESPACE" -o jsonpath='{.spec.rules[0].host}')
    
    if [ -n "$ingress_host" ]; then
        print_status "Application should be available at: https://$ingress_host"
    fi
    
    print_success "Deployment verification completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo
    echo "Commands:"
    echo "  deploy     Deploy the complete system (infrastructure + application)"
    echo "  infra      Deploy only infrastructure"
    echo "  app        Deploy only application"
    echo "  verify     Verify deployment status"
    echo "  destroy    Destroy infrastructure (use with caution)"
    echo
    echo "Options:"
    echo "  -e, --environment ENV    Environment name (default: production)"
    echo "  -r, --region REGION      AWS region (default: us-west-2)"
    echo "  -c, --cluster CLUSTER    EKS cluster name (default: ai-bi-cluster)"
    echo "  -d, --docker-registry    Docker registry URL"
    echo "  -i, --image IMAGE        Docker image name (default: ai-business-intelligence)"
    echo "  -t, --tag TAG            Docker image tag (default: latest)"
    echo "  -h, --help               Show this help message"
    echo
    echo "Examples:"
    echo "  $0 deploy                                    # Deploy complete system"
    echo "  $0 -e staging deploy                        # Deploy to staging"
    echo "  $0 -d your-registry.com deploy              # Deploy with custom registry"
    echo "  $0 verify                                   # Verify deployment"
}

# Function to destroy infrastructure
destroy_infrastructure() {
    print_warning "This will destroy all infrastructure. Are you sure? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Destruction cancelled by user"
        exit 0
    fi
    
    print_status "Destroying infrastructure..."
    cd "$TERRAFORM_DIR"
    terraform destroy -auto-approve
    
    print_success "Infrastructure destroyed"
}

# Main function
main() {
    local command=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -r|--region)
                AWS_REGION="$2"
                shift 2
                ;;
            -c|--cluster)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            -d|--docker-registry)
                DOCKER_REGISTRY="$2"
                shift 2
                ;;
            -i|--image)
                DOCKER_IMAGE="$2"
                shift 2
                ;;
            -t|--tag)
                DOCKER_TAG="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            deploy|infra|app|verify|destroy)
                command="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    if [ -z "$command" ]; then
        print_error "No command specified"
        show_usage
        exit 1
    fi
    
    # Execute command
    case $command in
        deploy)
            check_prerequisites
            check_aws_credentials
            setup_terraform_backend
            build_and_push_image
            deploy_infrastructure
            configure_kubectl
            create_kubernetes_secrets
            deploy_application
            verify_deployment
            print_success "Complete deployment finished successfully!"
            ;;
        infra)
            check_prerequisites
            check_aws_credentials
            setup_terraform_backend
            deploy_infrastructure
            print_success "Infrastructure deployment finished successfully!"
            ;;
        app)
            check_prerequisites
            check_aws_credentials
            build_and_push_image
            configure_kubectl
            create_kubernetes_secrets
            deploy_application
            verify_deployment
            print_success "Application deployment finished successfully!"
            ;;
        verify)
            check_prerequisites
            check_aws_credentials
            configure_kubectl
            verify_deployment
            ;;
        destroy)
            check_prerequisites
            check_aws_credentials
            destroy_infrastructure
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 