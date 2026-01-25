auth# GCP Deployment Guide for SOTA OCR System
# Complete step-by-step instructions for deploying to Google Cloud Platform

## 🚀 Quick Start

### 1. Prerequisites
- GCP Account with billing enabled
- gcloud CLI installed and configured
- Docker and Docker Compose installed
- Terraform installed (optional, for IaC)

### 2. Project Setup
```bash
# Create new GCP project
gcloud projects create raptorflow-ocr-prod

# Set active project
gcloud config set project raptorflow-ocr-prod

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

### 3. Infrastructure Deployment

#### Option A: Terraform (Recommended)
```bash
# Navigate to deployment directory
cd backend/services/sota_ocr

# Initialize Terraform
terraform init gcp_deployment.tf

# Plan deployment
terraform plan -var="gcp_project_id=raptorflow-ocr-prod" -var="gcp_region=us-central1"

# Apply deployment
terraform apply -var="gcp_project_id=raptorflow-ocr-prod" -var="gcp_region=us-central1"
```

#### Option B: Manual Setup
```bash
# Create VPC network
gcloud compute networks create ocr-network --subnet-mode=custom

# Create subnet
gcloud compute networks subnets create ocr-subnet \
    --network=ocr-network \
    --range=10.0.0.0/24 \
    --region=us-central1

# Create firewall rules
gcloud compute firewall-rules create ocr-firewall \
    --network=ocr-network \
    --allow tcp:22,tcp:80,tcp:443,tcp:8000 \
    --source-ranges=0.0.0.0/0

# Create storage bucket
gsutil mb gs://raptorflow-ocr-storage

# Create service account
gcloud iam service-accounts create ocr-service-account

# Grant permissions
gcloud projects add-iam-policy-binding raptorflow-ocr-prod \
    --member="serviceAccount:ocr-service-account@raptorflow-ocr-prod.iam.gserviceaccount.com" \
    --role="roles/compute.admin"

gcloud projects add-iam-policy-binding raptorflow-ocr-prod \
    --member="serviceAccount:ocr-service-account@raptorflow-ocr-prod.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding raptorflow-ocr-prod \
    --member="serviceAccount:ocr-service-account@raptorflow-ocr-prod.iam.gserviceaccount.com" \
    --role="roles/logging.admin"

gcloud projects add-iam-policy-binding raptorflow-ocr-prod \
    --member="serviceAccount:ocr-service-account@raptorflow-ocr-prod.iam.gserviceaccount.com" \
    --role="roles/monitoring.admin"
```

### 4. Create Compute Instance with GPU
```bash
# Create GPU instance
gcloud compute instances create ocr-instance-1 \
    --zone=us-central1-a \
    --machine-type=n1-standard-8 \
    --accelerator=type=nvidia-tesla-a100,count=1 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB \
    --boot-disk-type=pd-ssd \
    --network=ocr-network \
    --subnet=ocr-subnet \
    --service-account=ocr-service-account@raptorflow-ocr-prod.iam.gserviceaccount.com \
    --metadata-from-file=startup-script=startup-script.sh \
    --tags=ocr-server \
    --maintenance-policy=TERMINATE \
    --restart-on-failure
```

### 5. Deploy Application
```bash
# Wait for instance to be ready
gcloud compute instances describe ocr-instance-1 --zone=us-central1-a

# SSH into instance
gcloud compute ssh ocr-instance-1 --zone=us-central1-a

# Navigate to application directory
cd /opt/ocr

# Build Docker image
docker build -t ocr-api:latest .

# Run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs ocr-api
```

## 🔧 Configuration

### Environment Variables
Create `.env` file with your configuration:
```bash
# GCP Configuration
GCP_PROJECT_ID=raptorflow-ocr-prod
GCP_REGION=us-central1
GCP_ZONE=us-central1-a

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=8.0

# OCR Configuration
OCR_MODELS_ENABLED=chandra_ocr_8b,dots_ocr,deepseek_ocr_3b
OCR_MAX_CONCURRENT_MODELS=2
OCR_ENABLE_ENSEMBLE=true
OCR_ENABLE_QUALITY_CHECK=true
OCR_ENABLE_MONITORING=true

# Storage Configuration
STORAGE_BUCKET=raptorflow-ocr-storage
REDIS_HOST=redis
REDIS_PORT=6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RATE_LIMIT=1000
API_TIMEOUT_SECONDS=60

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
```

### Model Configuration
Update model configurations in `config.py`:
```python
# GCP-specific model paths
MODEL_CONFIGS = {
    "chandra_ocr_8b": {
        "model_path": "/app/models/chandra-ocr-8b.pt",
        "api_url": "https://chandra-ocr.raptorflow.ai/api",
        "api_key": os.getenv("CHANDRA_OCR_API_KEY"),
        "gpu_memory_gb": 16,
        "batch_size": 4
    },
    "dots_ocr": {
        "model_path": "/app/models/dots-ocr.pt",
        "api_url": "https://dots.ocr.raptorflow.ai/api",
        "api_key": os.getenv("DOTS_OCR_API_KEY"),
        "gpu_memory_gb": 8,
        "batch_size": 8
    },
    "deepseek_ocr_3b": {
        "model_path": "/app/models/deepseek-ocr-3b.pt",
        "api_url": "https://deepseek-ocr.raptorflow.ai/api",
        "api_key": os.getenv("DEEPSEEK_OCR_API_KEY"),
        "gpu_memory_gb": 6,
        "batch_size": 16
    }
}
```

## 📊 Monitoring Setup

### 1. Cloud Monitoring
```bash
# Create monitoring workspace
gcloud monitoring workspaces create ocr-monitoring

# Create alert policies
gcloud monitoring policies create --policy-from-file=alert-policies.json

# Create dashboards
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

### 2. Log-Based Metrics
```bash
# Create log-based metrics
gcloud logging metrics create ocr_processing_time \
    --description="OCR processing time metric" \
    --log-filter='resource.type="gce_instance" AND logName="projects/raptorflow-ocr-prod/logs/ocr-service"' \
    --metric-type=custom.googleapis.com/ocr/processing_time
```

### 3. Custom Monitoring
```bash
# Install monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
bash add-google-cloud-ops-agent-repo.sh --also-install

# Configure monitoring
sudo systemctl restart google-cloud-ops-agent
```

## 🔒 Security Configuration

### 1. SSL/TLS Setup
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d ocr.raptorflow.ai

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Network Security
```bash
# Configure VPC Service Controls
gcloud access-context-manager policies create \
    --title="OCR Policy" \
    --organization=YOUR_ORG_ID

# Configure IAM conditions
gcloud projects add-iam-policy-binding raptorflow-ocr-prod \
    --member="serviceAccount:ocr-service-account@raptorflow-ocr-prod.iam.gserviceaccount.com" \
    --role="roles/compute.admin" \
    --condition="title=OCR Access,expression=request.time.startsWith(timestamp('2024-01-01T00:00:00Z'))"
```

### 3. Encryption
```bash
# Enable customer-managed encryption keys
gcloud kms keyrings create ocr-keyring --location=us-central1
gcloud kms keys create ocr-key --location=us-central1 --keyring=ocr-keyring --purpose=encryption

# Use CMEK for storage
gsutil kms encryption -k projects/raptorflow-ocr-prod/locations/us-central1/keyRings/ocr-keyring/cryptoKeys/ocr-key
```

## 🚀 Scaling and Autoscaling

### 1. Instance Group
```bash
# Create instance template
gcloud compute instance-templates create ocr-template \
    --machine-type=n1-standard-8 \
    --accelerator=type=nvidia-tesla-a100,count=1 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB \
    --boot-disk-type=pd-ssd \
    --network=ocr-network \
    --subnet=ocr-subnet \
    --service-account=ocr-service-account@raptorflow-ocr-prod.iam.gserviceaccount.com \
    --metadata-from-file=startup-script=startup-script.sh

# Create managed instance group
gcloud compute instance-groups managed create ocr-instance-group \
    --zone=us-central1-a \
    --template=ocr-template \
    --size=1

# Configure autoscaling
gcloud compute instance-groups managed set-autoscaling ocr-instance-group \
    --zone=us-central1-a \
    --max-num-replicas=5 \
    --min-num-replicas=1 \
    --target-cpu-utilization=0.7 \
    --cool-down-period=60
```

### 2. Load Balancer
```bash
# Create HTTP load balancer
gcloud compute url-maps create ocr-lb
gcloud compute url-maps add-path-matcher ocr-lb \
    --default-service=ocr-backend

# Create backend service
gcloud compute backend-services create ocr-backend \
    --protocol=HTTP \
    --port-name=http \
    --health-checks=ocr-health-check \
    --enable-cdn

# Create health check
gcloud compute health-checks create http ocr-health-check \
    --port=8000 \
    --request-path=/health

# Create forwarding rule
gcloud compute forwarding-rules create ocr-forwarding-rule \
    --global \
    --url-map=ocr-lb \
    --ports=443
```

## 💰 Cost Optimization

### 1. Preemptible Instances
```bash
# Create preemptible instance template
gcloud compute instance-templates create ocr-template-preemptible \
    --machine-type=n1-standard-8 \
    --accelerator=type=nvidia-tesla-a100,count=1 \
    --preemptible \
    --restart-on-failure

# Use for batch processing
gcloud compute instance-groups managed create ocr-batch-group \
    --zone=us-central1-a \
    --template=ocr-template-preemptible \
    --size=0
```

### 2. Committed Use Discounts
```bash
# Purchase committed use discounts
gcloud compute commitments create ocr-commitment \
    --region=us-central1 \
    --resource-type=compute \
    --plan=12-month \
    --type=accelerated-optimized \
    --amount=1 \
    --accelerator-type=nvidia-tesla-a100 \
    --accelerator-count=1
```

### 3. Budget Alerts
```bash
# Create budget
gcloud billing budgets create ocr-budget \
    --billing-account=YOUR_BILLING_ACCOUNT \
    --display-name="OCR Monthly Budget" \
    --budget-amount=5000USD

# Create budget alerts
gcloud billing budgets alert-policies create \
    --billing-account=YOUR_BILLING_ACCOUNT \
    --budget-display-name="OCR Monthly Budget" \
    --threshold-percent=90
```

## 🔄 Backup and Disaster Recovery

### 1. Automated Backups
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_$DATE"

# Create backup
gsutil -m cp -r gs://raptorflow-ocr-storage gs://raptorflow-ocr-backups/$BACKUP_DIR

# Clean old backups (keep 30 days)
gsutil ls -d gs://raptorflow-ocr-backups/backup_* | tail -n +31 | xargs -I {} gsutil rm -r {}
EOF

chmod +x backup.sh

# Schedule backup
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

### 2. Multi-Region Deployment
```bash
# Deploy to secondary region
gcloud config set project raptorflow-ocr-backup
gcloud config set region us-east1

# Repeat deployment steps
# ...

# Configure cross-region replication
gsutil rsync -r gs://raptorflow-ocr-storage gs://raptorflow-ocr-backup
```

## 🧪 Testing

### 1. Health Check
```bash
# Test API health
curl -f http://EXTERNAL_IP:8000/health

# Test OCR processing
curl -X POST http://EXTERNAL_IP:8000/api/v1/ocr/process \
  -F "file=@test_document.pdf" \
  -F "strategy=ensemble"
```

### 2. Load Testing
```bash
# Install k6
curl https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz -o k6.tar.gz
tar -xzf k6.tar.gz

# Create load test script
cat > load-test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  const response = http.post('http://EXTERNAL_IP:8000/api/v1/ocr/process', {
    file: open('test_document.pdf', 'rb')
  });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5000ms': (r) => r.timings.duration < 5000,
  });
  
  sleep(1);
}
EOF

# Run load test
./k6 run --vus 10 --duration 30s load-test.js
```

## 📱 Monitoring Dashboard

Access monitoring dashboards:
- **Grafana**: http://EXTERNAL_IP:3000 (admin/admin)
- **Prometheus**: http://EXTERNAL_IP:9090
- **cAdvisor**: http://EXTERNAL_IP:8080
- **Node Exporter**: http://EXTERNAL_IP:9100

## 🚨 Troubleshooting

### Common Issues
1. **GPU not detected**: Check NVIDIA driver installation
2. **Out of memory**: Reduce batch size or use smaller models
3. **Slow processing**: Check GPU utilization and network latency
4. **API errors**: Check logs in Cloud Logging

### Debug Commands
```bash
# Check GPU status
nvidia-smi

# Check service status
docker-compose ps
docker-compose logs ocr-api

# Check system resources
htop
df -h
free -h

# Check network
curl -I http://localhost:8000/health
```

## 📞 Support

For issues:
1. Check Cloud Logging for error messages
2. Review monitoring dashboards
3. Consult GCP documentation
4. Contact support at support@raptorflow.ai
