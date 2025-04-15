# Production Deployment Guide

This guide provides detailed instructions for deploying the TORONTO AI TEAM AGENT system in a production environment.

## Prerequisites

Before proceeding, ensure you have:
- Reviewed the [Prerequisites](../getting-started/prerequisites.md) document
- Completed the [Installation](../getting-started/installation.md) process
- Tested the system in a [local development environment](./local-deployment.md)

## Hardware Requirements

**Application Servers (3 Primary + 1 Backup)**
- CPU: 16+ cores per server
- RAM: 64GB+ per server
- Storage: 500GB SSD
- Network: 10Gbps connectivity

**Database Servers (3-Node Cluster)**
- CPU: 16+ cores per server
- RAM: 128GB+ per server
- Storage: 2TB SSD (RAID 10 recommended)
- Network: 10Gbps connectivity

**Vector Database Servers**
- CPU: 16+ cores per server
- RAM: 128GB+ per server
- Storage: 1TB SSD
- Network: 10Gbps connectivity

**Load Balancers (2 for redundancy)**
- CPU: 8+ cores per server
- RAM: 32GB+ per server
- Network: 10Gbps connectivity with support for SSL offloading

## Phase 1: Infrastructure Setup

### Environment Provisioning

```bash
# Example using Terraform for infrastructure provisioning
cd /path/to/terraform
terraform init
terraform plan -out=production.tfplan
terraform apply production.tfplan
```

### Kubernetes Cluster Setup

```bash
# Install kubectl
sudo apt-get update && sudo apt-get install -y kubectl

# Set up Kubernetes cluster (example using kubeadm)
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Set up kubectl for the local user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install network plugin (example using Calico)
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# Verify cluster is running
kubectl get nodes
```

### Database Setup

#### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get update && sudo apt-get install -y postgresql-15

# Configure PostgreSQL for production
sudo -u postgres psql -c "CREATE USER toronto_ai WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "CREATE DATABASE toronto_ai_team_agent;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE toronto_ai_team_agent TO toronto_ai;"

# Configure PostgreSQL for high availability
sudo nano /etc/postgresql/15/main/postgresql.conf
# Set appropriate values for shared_buffers, work_mem, etc.

# Configure PostgreSQL for replication
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add replication entries

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Vector Database Setup (ChromaDB Example)

```bash
# Install Docker if not already installed
sudo apt-get update && sudo apt-get install -y docker.io

# Pull ChromaDB Docker image
sudo docker pull chromadb/chroma

# Run ChromaDB container
sudo docker run -d -p 8000:8000 \
  -v /path/to/chroma/data:/chroma/data \
  -e CHROMA_DB_IMPL=duckdb+parquet \
  -e CHROMA_PERSISTENCE_DIRECTORY=/chroma/data \
  --name chromadb \
  chromadb/chroma
```

### Load Balancer Setup

```bash
# Install Nginx
sudo apt-get update && sudo apt-get install -y nginx

# Configure Nginx as load balancer
sudo nano /etc/nginx/nginx.conf

# Example configuration
# http {
#   upstream app_servers {
#     server app1.internal:8001;
#     server app2.internal:8001;
#     server app3.internal:8001;
#   }
#
#   server {
#     listen 80;
#     server_name toronto-ai-team-agent.example.com;
#
#     location / {
#       proxy_pass http://app_servers;
#       proxy_set_header Host $host;
#       proxy_set_header X-Real-IP $remote_addr;
#     }
#   }
# }

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### SSL Certificate Setup

```bash
# Install Certbot
sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d toronto-ai-team-agent.example.com

# Verify automatic renewal
sudo certbot renew --dry-run
```

## Phase 2: Application Deployment

### Code Preparation

```bash
# Clone repository
git clone https://github.com/torontoai/TorontoAITeamAgent.git
cd TorontoAITeamAgent

# Checkout production branch
git checkout production

# Create production configuration
cp config/config.example.yaml config/config.production.yaml
nano config/config.production.yaml
# Update configuration with production values
```

### Docker Image Building

```bash
# Build Docker image
docker build -t torontoai/team-agent:production .

# Tag image with version
docker tag torontoai/team-agent:production torontoai/team-agent:v1.0.0

# Push to container registry
docker push torontoai/team-agent:production
docker push torontoai/team-agent:v1.0.0
```

### Kubernetes Deployment

```bash
# Apply Kubernetes configurations
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml

# Verify deployment
kubectl get pods -n toronto-ai
kubectl get services -n toronto-ai
kubectl get ingress -n toronto-ai
```

### Frontend Deployment

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Copy to web server
sudo cp -r build/* /var/www/toronto-ai-team-agent/
```

## Phase 3: Monitoring and Maintenance

### Set Up Monitoring

```bash
# Install Prometheus and Grafana
kubectl apply -f monitoring/prometheus.yaml
kubectl apply -f monitoring/grafana.yaml

# Set up ELK Stack
kubectl apply -f monitoring/elasticsearch.yaml
kubectl apply -f monitoring/logstash.yaml
kubectl apply -f monitoring/kibana.yaml

# Configure alerts
kubectl apply -f monitoring/alerts.yaml
```

### Backup Configuration

```bash
# Set up database backups
kubectl apply -f backup/database-backup.yaml

# Set up application state backups
kubectl apply -f backup/application-backup.yaml

# Verify backup jobs
kubectl get cronjobs -n toronto-ai
```

### Scaling Configuration

```bash
# Configure horizontal pod autoscaler
kubectl apply -f scaling/hpa.yaml

# Configure vertical pod autoscaler
kubectl apply -f scaling/vpa.yaml

# Verify autoscalers
kubectl get hpa -n toronto-ai
kubectl get vpa -n toronto-ai
```

## Phase 4: Testing and Validation

### Smoke Testing

```bash
# Run smoke tests
kubectl apply -f testing/smoke-tests.yaml

# Check test results
kubectl logs -n toronto-ai -l app=smoke-tests
```

### Load Testing

```bash
# Run load tests
kubectl apply -f testing/load-tests.yaml

# Monitor results
kubectl logs -n toronto-ai -l app=load-tests
```

### Security Testing

```bash
# Run security scans
kubectl apply -f testing/security-scans.yaml

# Check scan results
kubectl logs -n toronto-ai -l app=security-scans
```

## Troubleshooting

For common production issues and solutions, refer to the [Troubleshooting Guide](../troubleshooting/common-issues.md).

## Next Steps

- [Monitoring Guide](../backend/monitoring.md) - For detailed monitoring instructions
- [Backup and Recovery](../backend/backup-recovery.md) - For backup and recovery procedures
- [Scaling Guide](../backend/scaling.md) - For scaling the system to handle increased load
