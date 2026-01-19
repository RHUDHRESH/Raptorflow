#!/bin/bash
# GCP Startup Script for SOTA OCR System
# This script runs on instance startup to configure the environment

set -e

# Log startup
echo "Starting OCR system setup at $(date)" >> /var/log/ocr-startup.log

# Update system packages
echo "Updating system packages..." >> /var/log/ocr-startup.log
apt-get update -y
apt-get upgrade -y

# Install required packages
echo "Installing required packages..." >> /var/log/ocr-startup.log
apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    htop \
    nvidia-driver-470 \
    nvidia-cuda-toolkit \
    nvidia-cuda-dev \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx

# Install NVIDIA Docker runtime
echo "Installing NVIDIA Docker runtime..." >> /var/log/ocr-startup.log
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list

apt-get update -y
apt-get install -y nvidia-docker2
systemctl restart docker

# Create OCR user
echo "Creating OCR user..." >> /var/log/ocr-startup.log
useradd -m -s /bin/bash ocr
usermod -aG docker ocr

# Create application directory
echo "Creating application directory..." >> /var/log/ocr-startup.log
mkdir -p /opt/ocr
chown ocr:ocr /opt/ocr

# Clone repository (replace with your actual repo)
echo "Cloning OCR repository..." >> /var/log/ocr-startup.log
cd /opt/ocr
sudo -u ocr git clone https://github.com/raptorflow/sota-ocr.git .
sudo -u ocr git checkout main

# Create Python virtual environment
echo "Creating Python virtual environment..." >> /var/log/ocr-startup.log
sudo -u ocr python3.9 -m venv /opt/ocr/venv
sudo -u ocr /opt/ocr/venv/bin/pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..." >> /var/log/ocr-startup.log
sudo -u ocr /opt/ocr/venv/bin/pip install -r /opt/ocr/backend/services/sota_ocr/requirements.txt

# Install PyTorch with CUDA support
echo "Installing PyTorch with CUDA support..." >> /var/log/ocr-startup.log
sudo -u ocr /opt/ocr/venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Download OCR models (placeholder - implement actual model download)
echo "Downloading OCR models..." >> /var/log/ocr-startup.log
mkdir -p /opt/ocr/models
cd /opt/ocr/models

# Example: Download Chandra-OCR model
# wget https://models.raptorflow.ai/chandra-ocr-8b.pt
# wget https://models.raptorflow.ai/dots-ocr.pt
# wget https://models.raptorflow.ai/deepseek-ocr-3b.pt

# Create directories for data and logs
echo "Creating data and log directories..." >> /var/log/ocr-startup.log
mkdir -p /opt/ocr/data
mkdir -p /opt/ocr/logs
mkdir -p /opt/ocr/cache
chown -R ocr:ocr /opt/ocr/data
chown -R ocr:ocr /opt/ocr/logs
chown -R ocr:ocr /opt/ocr/cache

# Create environment file
echo "Creating environment file..." >> /var/log/ocr-startup.log
cat > /opt/ocr/.env << EOF
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
OCR_MAX_FILE_SIZE_MB=100
OCR_ENABLE_ENSEMBLE=true
OCR_ENABLE_QUALITY_CHECK=true
OCR_ENABLE_MONITORING=true

# Performance Configuration
GPU_MEMORY_LIMIT_GB=35
OCR_TARGET_THROUGHPUT_PAGES_PER_MINUTE=100
OCR_MAX_LATENCY_SECONDS=30

# Storage Configuration
STORAGE_BUCKET=raptorflow-ocr-storage
REDIS_HOST=10.0.0.5
REDIS_PORT=6379

# Monitoring Configuration
ENABLE_STACKDRIVER=true
LOG_LEVEL=INFO
METRICS_COLLECTION_INTERVAL=60

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RATE_LIMIT=1000
API_TIMEOUT_SECONDS=60

# Security
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
EOF

chown ocr:ocr /opt/ocr/.env

# Create systemd service for OCR API
echo "Creating systemd service..." >> /var/log/ocr-startup.log
cat > /etc/systemd/system/ocr-api.service << EOF
[Unit]
Description=OCR API Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ocr
WorkingDirectory=/opt/ocr
Environment=PATH=/opt/ocr/venv/bin
ExecStart=/opt/ocr/venv/bin/python -m uvicorn services.sota_ocr.api:router --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for OCR Worker
echo "Creating OCR worker service..." >> /var/log/ocr-startup.log
cat > /etc/systemd/system/ocr-worker.service << EOF
[Unit]
Description=OCR Worker Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ocr
WorkingDirectory=/opt/ocr
Environment=PATH=/opt/ocr/venv/bin
ExecStart=/opt/ocr/venv/bin/python -m services.sota_ocr.worker
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for OCR Monitor
echo "Creating OCR monitor service..." >> /var/log/ocr-startup.log
cat > /etc/systemd/system/ocr-monitor.service << EOF
[Unit]
Description=OCR Monitor Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ocr
WorkingDirectory=/opt/ocr
Environment=PATH=/opt/ocr/venv/bin
ExecStart=/opt/ocr/venv/bin/python -m services.sota_ocr.monitor
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "Configuring Nginx..." >> /var/log/ocr-startup.log
cat > /etc/nginx/sites-available/ocr << EOF
server {
    listen 80;
    server_name ocr.raptorflow.ai;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
        
        # File upload size
        client_max_body_size 100M;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

# Enable Nginx site
ln -s /etc/nginx/sites-available/ocr /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Create log rotation configuration
echo "Creating log rotation..." >> /var/log/ocr-startup.log
cat > /etc/logrotate.d/ocr << EOF
/opt/ocr/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ocr ocr
    postrotate
        systemctl reload rsyslog
    endscript
}
EOF

# Create monitoring script
echo "Creating monitoring script..." >> /var/log/ocr-startup.log
cat > /opt/ocr/scripts/monitor.sh << 'EOF'
#!/bin/bash
# Monitoring script for OCR system

# Check GPU status
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits > /tmp/gpu_status

# Check service status
systemctl is-active ocr-api.service > /tmp/api_status
systemctl is-active ocr-worker.service > /tmp/worker_status
systemctl is-active ocr-monitor.service > /tmp/monitor_status

# Check disk usage
df -h /opt/ocr > /tmp/disk_usage

# Check memory usage
free -h > /tmp/memory_usage

# Upload to Cloud Monitoring (placeholder)
# gcloud monitoring metrics create --type=custom.googleapis.com/ocr/gpu_utilization ...
EOF

chmod +x /opt/ocr/scripts/monitor.sh
chown ocr:ocr /opt/ocr/scripts/monitor.sh

# Create backup script
echo "Creating backup script..." >> /var/log/ocr-startup.log
cat > /opt/ocr/scripts/backup.sh << 'EOF'
#!/bin/bash
# Backup script for OCR system

BACKUP_DIR="/opt/ocr/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup configuration
cp /opt/ocr/.env $BACKUP_DIR/
cp -r /opt/ocr/config $BACKUP_DIR/

# Backup models
cp -r /opt/ocr/models $BACKUP_DIR/

# Backup logs
cp -r /opt/ocr/logs $BACKUP_DIR/

# Upload to Cloud Storage
gsutil -m cp -r $BACKUP_DIR gs://raptorflow-ocr-storage/backups/

# Clean up local backups (keep last 7 days)
find /opt/ocr/backups -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x /opt/ocr/scripts/backup.sh
chown ocr:ocr /opt/ocr/scripts/backup.sh

# Create cron jobs
echo "Setting up cron jobs..." >> /var/log/ocr-startup.log
cat > /tmp/ocr_cron << EOF
# OCR System Monitoring
*/5 * * * * /opt/ocr/scripts/monitor.sh

# OCR System Backup
0 2 * * * /opt/ocr/scripts/backup.sh

# Log Rotation
0 0 * * * logrotate /etc/logrotate.d/ocr

# Health Check
*/1 * * * * curl -f http://localhost:8000/health || systemctl restart ocr-api.service
EOF

crontab -u ocr /tmp/ocr_cron
rm /tmp/ocr_cron

# Enable and start services
echo "Enabling and starting services..." >> /var/log/ocr-startup.log
systemctl daemon-reload
systemctl enable ocr-api.service
systemctl enable ocr-worker.service
systemctl enable ocr-monitor.service
systemctl start ocr-api.service
systemctl start ocr-worker.service
systemctl start ocr-monitor.service

# Start Nginx
systemctl enable nginx
systemctl start nginx

# Configure firewall
echo "Configuring firewall..." >> /var/log/ocr-startup.log
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Install SSL certificate (placeholder - requires domain validation)
# certbot --nginx -d ocr.raptorflow.ai

# Create startup complete marker
echo "OCR system setup completed at $(date)" >> /var/log/ocr-startup.log
touch /opt/ocr/.setup_complete

# Display system information
echo "=== OCR System Information ===" >> /var/log/ocr-startup.log
echo "GPU Information:" >> /var/log/ocr-startup.log
nvidia-smi >> /var/log/ocr-startup.log
echo "" >> /var/log/ocr-startup.log
echo "Service Status:" >> /var/log/ocr-startup.log
systemctl status ocr-api.service --no-pager >> /var/log/ocr-startup.log
systemctl status ocr-worker.service --no-pager >> /var/log/ocr-startup.log
systemctl status ocr-monitor.service --no-pager >> /var/log/ocr-startup.log
echo "" >> /var/log/ocr-startup.log
echo "Network Information:" >> /var/log/ocr-startup.log
ip addr show >> /var/log/ocr-startup.log
echo "" >> /var/log/ocr-startup.log
echo "=== Setup Complete ===" >> /var/log/ocr-startup.log

echo "OCR system setup completed successfully!"
echo "API is available at: http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip):8000"
echo "Health check: http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip):8000/health"
