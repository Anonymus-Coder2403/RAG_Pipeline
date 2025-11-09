# 🚀 Production Deployment Guide - RAG Chatbot on Cloud

**Complete step-by-step guide to deploy your RAG chatbot on AWS EC2 or Google Cloud Platform**

---

## 📋 Table of Contents

1. [Cloud Provider Comparison](#cloud-provider-comparison)
2. [Prerequisites](#prerequisites)
3. [AWS EC2 Deployment](#aws-ec2-deployment)
4. [Google Cloud Platform Deployment](#gcp-deployment)
5. [Production Optimizations](#production-optimizations)
6. [Security Best Practices](#security-best-practices)
7. [Monitoring & Maintenance](#monitoring-maintenance)
8. [Cost Estimates](#cost-estimates)
9. [Troubleshooting](#troubleshooting)

---

## 🔍 Cloud Provider Comparison

| Feature | AWS EC2 | Google Cloud (GCP) | Recommendation |
|---------|---------|-------------------|----------------|
| **Ease of Use** | Moderate | Easier | GCP for beginners |
| **GPU Support** | Excellent (P3, G4) | Excellent (T4, V100) | Tie |
| **Free Tier** | 750 hrs/month (12 months) | $300 credit (90 days) | AWS for long-term free |
| **Pricing** | Competitive | Slightly cheaper | GCP |
| **Network Speed** | Fast | Faster | GCP |
| **Documentation** | Extensive | Good | AWS |
| **Best For** | Enterprise, complex | Startups, ML apps | Depends on use case |

**Our Recommendation for RAG Chatbot:**
- **AWS EC2**: If you need GPU (RTX 3050 equivalent), use `g4dn.xlarge` (T4 GPU)
- **GCP Compute Engine**: If running CPU-only, use `e2-standard-2` (cheaper)

---

## ✅ Prerequisites

### **1. Required Accounts**
- [ ] AWS Account OR Google Cloud Account
- [ ] Domain name (optional, for custom URL)
- [ ] Gemini API Key (Google AI Studio)

### **2. Local Setup**
- [ ] Docker installed on your local machine
- [ ] Git installed
- [ ] SSH key pair generated

### **3. Project Files Ready**
```bash
# Verify you have these files:
✅ app.py
✅ config.py
✅ requirement.txt
✅ Dockerfile
✅ docker-compose.yml
✅ .env (with GEMINI_API_KEY)
✅ src/ folder
✅ services/ folder
```

---

## 🔵 AWS EC2 Deployment

### **Step 1: Create an AWS Account**

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click **Create an AWS Account**
3. Enter email, password, AWS account name
4. Choose **Personal** account
5. Enter billing information (required, but won't be charged with free tier)
6. Verify identity with phone number
7. Choose **Free** support plan
8. Wait for account activation (5-10 minutes)

---

### **Step 2: Launch EC2 Instance**

1. **Login to AWS Console**
   - Go to [console.aws.amazon.com](https://console.aws.amazon.com)
   - Search for **EC2** in the search bar
   - Click **EC2** service

2. **Launch Instance**
   - Click **Launch Instance** button

3. **Configure Instance:**

   **Name and Tags:**
   ```
   Name: rag-chatbot-production
   ```

   **Application and OS Images (AMI):**
   - Choose: **Ubuntu Server 22.04 LTS**
   - Architecture: **64-bit (x86)**
   - Free tier eligible ✅

   **Instance Type:**
   - **For CPU-only deployment:**
     - Instance type: `t3.medium` (2 vCPU, 4 GB RAM)
     - Cost: ~$0.04/hour (~$30/month)

   - **For GPU deployment (recommended for large embedding model):**
     - Instance type: `g4dn.xlarge` (4 vCPU, 16 GB RAM, T4 GPU)
     - Cost: ~$0.526/hour (~$380/month)
     - **Note:** GPU instances are NOT in free tier

   **Key Pair (Login):**
   - Click **Create new key pair**
   - Key pair name: `rag-chatbot-key`
   - Key pair type: **RSA**
   - Private key format: `.pem` (for Mac/Linux) or `.ppk` (for Windows PuTTY)
   - Click **Create key pair**
   - **IMPORTANT:** Save the `.pem` file securely (you can't download it again)

   **Network Settings:**
   - Click **Edit**
   - **Auto-assign public IP:** Enable
   - **Firewall (security groups):** Create security group
   - Security group name: `rag-chatbot-sg`
   - Description: `Security group for RAG chatbot`

   **Configure inbound rules:**
   - ✅ SSH (Port 22) - Your IP (for security)
   - ✅ HTTP (Port 80) - Anywhere (0.0.0.0/0)
   - ✅ HTTPS (Port 443) - Anywhere (0.0.0.0/0)
   - ✅ Custom TCP (Port 8501) - Anywhere (0.0.0.0/0) - For Streamlit

   **Storage:**
   - Root volume: **30 GB** gp3 (SSD)
   - (Free tier includes 30GB)

4. **Launch Instance**
   - Review all settings
   - Click **Launch Instance**
   - Wait 2-3 minutes for instance to start

5. **Note Your Instance Details**
   - Go to **Instances** page
   - Find your instance
   - Copy **Public IPv4 address** (e.g., 3.145.23.456)
   - Copy **Public IPv4 DNS** (e.g., ec2-3-145-23-456.compute-1.amazonaws.com)

---

### **Step 3: Connect to Your EC2 Instance**

**For Mac/Linux:**

1. **Set Permissions for Key File**
   ```bash
   chmod 400 ~/Downloads/rag-chatbot-key.pem
   ```

2. **Connect via SSH**
   ```bash
   ssh -i ~/Downloads/rag-chatbot-key.pem ubuntu@YOUR_PUBLIC_IP
   ```
   Replace `YOUR_PUBLIC_IP` with your EC2 public IP

3. **Accept Fingerprint**
   - Type `yes` when prompted

**For Windows (using PuTTY):**

1. Download PuTTY from [putty.org](https://www.putty.org)
2. Convert `.pem` to `.ppk` using PuTTYgen
3. Open PuTTY
4. Host Name: `ubuntu@YOUR_PUBLIC_IP`
5. Connection → SSH → Auth → Browse and select `.ppk` file
6. Click **Open**

---

### **Step 4: Install Docker on EC2**

Once connected via SSH, run these commands:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (no need for sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# IMPORTANT: Logout and login again for group changes to take effect
exit
```

**Reconnect to EC2:**
```bash
ssh -i ~/Downloads/rag-chatbot-key.pem ubuntu@YOUR_PUBLIC_IP
```

**Verify Docker Works:**
```bash
docker run hello-world
```

---

### **Step 5: Deploy Your Application**

1. **Create Project Directory**
   ```bash
   mkdir -p ~/rag-chatbot
   cd ~/rag-chatbot
   ```

2. **Upload Your Code (Option A: Git)**
   ```bash
   # If your code is on GitHub
   git clone https://github.com/YOUR_USERNAME/RAG_upgraded.git .
   ```

   **Upload Your Code (Option B: SCP from local machine)**

   On your **local machine** (not EC2):
   ```bash
   # Navigate to your project folder
   cd d:/RAG_upgraded

   # Upload entire project
   scp -i ~/Downloads/rag-chatbot-key.pem -r . ubuntu@YOUR_PUBLIC_IP:~/rag-chatbot/
   ```

3. **Create .env File on EC2**
   ```bash
   cd ~/rag-chatbot
   nano .env
   ```

   Paste this content:
   ```env
   # Environment
   ENVIRONMENT=production

   # Gemini API
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-2.5-flash

   # Embedding Model
   EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

   # LLM Configuration
   LLM_TEMPERATURE=0.1
   LLM_MAX_TOKENS=4096

   # RAG Configuration
   CHUNK_SIZE=800
   CHUNK_OVERLAP=150
   TOP_K_RESULTS=4

   # File Upload
   MAX_FILE_SIZE_MB=10

   # Logging
   LOG_LEVEL=INFO
   ```

   - Press `Ctrl+X`, then `Y`, then `Enter` to save

4. **Build and Run Docker Container**
   ```bash
   cd ~/rag-chatbot

   # Build the Docker image
   docker-compose build

   # Start the application
   docker-compose up -d

   # Check logs
   docker-compose logs -f
   ```

   **Wait for initialization** (may take 2-5 minutes to download embedding model)

   Press `Ctrl+C` to stop viewing logs (app keeps running)

5. **Verify Application is Running**
   ```bash
   docker ps
   ```

   You should see `rag-chatbot` container with status `Up`

---

### **Step 6: Access Your Application**

1. **Open in Browser:**
   ```
   http://YOUR_PUBLIC_IP:8501
   ```

   Example: `http://3.145.23.456:8501`

2. **Test the Application:**
   - Upload a PDF
   - Ask a question
   - Verify it works!

---

### **Step 7: Setup Domain Name (Optional)**

If you want `https://myragbot.com` instead of `http://3.145.23.456:8501`:

1. **Buy Domain Name**
   - Use Namecheap, GoDaddy, or Google Domains
   - Cost: ~$10-15/year

2. **Point Domain to EC2**
   - Go to your domain registrar
   - Create an **A Record**:
     - Name: `@` (or `www`)
     - Value: Your EC2 Public IP
     - TTL: 300

3. **Install Nginx and SSL Certificate**

   ```bash
   # Install Nginx
   sudo apt install nginx -y

   # Install Certbot for SSL
   sudo apt install certbot python3-certbot-nginx -y

   # Create Nginx config
   sudo nano /etc/nginx/sites-available/rag-chatbot
   ```

   Paste this configuration:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/rag-chatbot /etc/nginx/sites-enabled/

   # Test config
   sudo nginx -t

   # Restart Nginx
   sudo systemctl restart nginx

   # Get SSL certificate (FREE)
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

   Follow prompts, enter email, agree to terms.

   **Now access your app at:** `https://yourdomain.com` 🎉

---

### **Step 8: Setup Auto-Restart on Reboot**

Ensure your app starts automatically if EC2 restarts:

```bash
# Docker already handles this with "restart: unless-stopped" in docker-compose.yml
# But verify:
cd ~/rag-chatbot
docker-compose up -d
```

To start on boot:
```bash
# Enable Docker service
sudo systemctl enable docker

# Create systemd service
sudo nano /etc/systemd/system/rag-chatbot.service
```

Paste:
```ini
[Unit]
Description=RAG Chatbot Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/rag-chatbot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

```bash
# Enable service
sudo systemctl daemon-reload
sudo systemctl enable rag-chatbot
sudo systemctl start rag-chatbot
```

---

## 🔴 Google Cloud Platform (GCP) Deployment

### **Step 1: Create GCP Account**

1. Go to [cloud.google.com](https://cloud.google.com)
2. Click **Get started for free**
3. Sign in with Google account
4. Enter billing information
5. Get **$300 free credit** (valid for 90 days)
6. Activate account

---

### **Step 2: Create a Project**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Project name: `rag-chatbot`
4. Click **Create**
5. Wait for project creation
6. **Select** the project from dropdown

---

### **Step 3: Enable Compute Engine API**

1. In GCP Console, search for **Compute Engine**
2. Click **Enable** (takes 1-2 minutes)

---

### **Step 4: Create VM Instance**

1. **Navigate to VM Instances**
   - Go to **Compute Engine** → **VM instances**
   - Click **Create Instance**

2. **Configure Instance:**

   **Name:**
   ```
   rag-chatbot-vm
   ```

   **Region and Zone:**
   - Region: `us-central1` (Iowa) - cheapest
   - Zone: `us-central1-a`

   **Machine Configuration:**
   - Series: **E2**
   - Machine type: `e2-standard-2` (2 vCPU, 8 GB RAM)
   - Cost: ~$49/month

   **For GPU (optional):**
   - Series: **N1**
   - Machine type: `n1-standard-4` (4 vCPU, 15 GB RAM)
   - Click **Add GPU**
   - GPU type: **NVIDIA T4**
   - Number: 1
   - Cost: ~$300/month

   **Boot Disk:**
   - Click **Change**
   - Operating system: **Ubuntu**
   - Version: **Ubuntu 22.04 LTS**
   - Boot disk type: **Balanced persistent disk**
   - Size: **30 GB**
   - Click **Select**

   **Firewall:**
   - ✅ Allow HTTP traffic
   - ✅ Allow HTTPS traffic

3. **Click Create** (takes 30-60 seconds)

---

### **Step 5: Configure Firewall Rules**

1. **Go to VPC Network** → **Firewall**
2. Click **Create Firewall Rule**
3. Configure:
   - Name: `allow-streamlit`
   - Direction: **Ingress**
   - Targets: **All instances in the network**
   - Source IP ranges: `0.0.0.0/0`
   - Protocols and ports: `tcp:8501`
4. Click **Create**

---

### **Step 6: Connect to VM Instance**

1. **Go to VM Instances page**
2. Find your instance `rag-chatbot-vm`
3. Click **SSH** button (opens browser SSH terminal)
4. Wait for connection

**Alternative: Use gcloud CLI**
```bash
# Install gcloud SDK on your local machine
# Then connect:
gcloud compute ssh rag-chatbot-vm --zone=us-central1-a
```

---

### **Step 7: Install Docker on GCP VM**

In the SSH terminal:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and reconnect
exit
```

**Reconnect** and verify:
```bash
docker --version
docker-compose --version
```

---

### **Step 8: Deploy Application**

Same as AWS steps 5-8:

1. **Create project directory**
   ```bash
   mkdir -p ~/rag-chatbot
   cd ~/rag-chatbot
   ```

2. **Upload code via Git or SCP**
   ```bash
   # Option A: Git
   git clone https://github.com/YOUR_USERNAME/RAG_upgraded.git .

   # Option B: SCP from local
   # On local machine:
   gcloud compute scp --recurse d:/RAG_upgraded/* rag-chatbot-vm:~/rag-chatbot/ --zone=us-central1-a
   ```

3. **Create .env file**
   ```bash
   nano .env
   # (paste environment variables as shown in AWS section)
   ```

4. **Build and run**
   ```bash
   docker-compose build
   docker-compose up -d
   docker-compose logs -f
   ```

5. **Get External IP**
   - Go to VM instances page
   - Copy **External IP**
   - Open: `http://EXTERNAL_IP:8501`

---

## 🛡️ Production Optimizations

### **1. Increase Swap Space (for CPU-only deployments)**

If you get memory errors:

```bash
# Create 8GB swap file
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### **2. Setup Automatic Backups**

**AWS:**
```bash
# Create snapshot schedule in EC2 console
# Go to Elastic Block Store → Snapshots → Create Snapshot
```

**GCP:**
```bash
# Create snapshot schedule
gcloud compute disks create-snapshot rag-chatbot-vm --zone=us-central1-a
```

### **3. Setup Monitoring**

**Install monitoring:**
```bash
# Install monitoring agent
sudo apt install prometheus-node-exporter -y

# Check disk space
df -h

# Check memory
free -h

# Monitor logs
docker-compose logs -f --tail=100
```

### **4. Optimize Docker Image**

Update your `Dockerfile` to use multi-stage builds:

```dockerfile
# First stage: Build dependencies
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirement.txt .
RUN pip install --user --no-cache-dir -r requirement.txt

# Second stage: Runtime
FROM python:3.11-slim
WORKLIT /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 🔒 Security Best Practices

### **1. Secure SSH Access**

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config

# Set these values:
PasswordAuthentication no
PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd
```

### **2. Setup Firewall**

```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH
sudo ufw allow 22/tcp

# Allow Streamlit
sudo ufw allow 8501/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### **3. Secure Environment Variables**

Never commit `.env` to Git:
```bash
echo ".env" >> .gitignore
```

### **4. Regular Updates**

```bash
# Create update script
nano ~/update.sh
```

Paste:
```bash
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
docker system prune -f
```

```bash
chmod +x ~/update.sh

# Run weekly
(crontab -l 2>/dev/null; echo "0 2 * * 0 /home/ubuntu/update.sh") | crontab -
```

---

## 📊 Monitoring & Maintenance

### **Check Application Health**

```bash
# Check if container is running
docker ps

# View logs
docker-compose logs -f

# Check resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### **Restart Application**

```bash
cd ~/rag-chatbot
docker-compose restart
```

### **Update Application**

```bash
cd ~/rag-chatbot

# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 💰 Cost Estimates

### **AWS EC2**

| Configuration | Instance Type | Monthly Cost | Free Tier |
|--------------|--------------|--------------|-----------|
| **Basic (CPU)** | t3.medium | ~$30 | 750 hrs free (12 months) |
| **Recommended** | t3.large | ~$60 | No |
| **GPU** | g4dn.xlarge | ~$380 | No |

**Additional Costs:**
- Storage (30GB): ~$3/month
- Data transfer: $0.09/GB (first 100GB free)
- Elastic IP: Free if associated with running instance

**Total Monthly (CPU-only):** ~$35-65

### **Google Cloud Platform (GCP)**

| Configuration | Machine Type | Monthly Cost | Free Credit |
|--------------|--------------|--------------|-------------|
| **Basic (CPU)** | e2-standard-2 | ~$49 | $300 (90 days) |
| **Recommended** | e2-standard-4 | ~$98 | $300 (90 days) |
| **GPU** | n1-standard-4 + T4 | ~$300 | $300 (90 days) |

**Additional Costs:**
- Storage (30GB): ~$2/month
- Data transfer: First 1TB free per month

**Total Monthly (CPU-only):** ~$50-100

### **Cost Optimization Tips**

1. **Use Spot Instances (AWS) or Preemptible VMs (GCP):** Save 60-90%
2. **Reserved Instances:** Save 30-50% with 1-year commitment
3. **Stop instance when not in use:** Pay only for storage
4. **Use Elastic Load Balancer:** Only if scaling to multiple instances

---

## 🔧 Troubleshooting

### **Problem: Application won't start**

```bash
# Check logs
docker-compose logs

# Check if port is already in use
sudo netstat -tulpn | grep 8501

# Restart Docker
sudo systemctl restart docker
docker-compose up -d
```

### **Problem: Out of memory**

```bash
# Check memory
free -h

# Add swap space (see Production Optimizations)

# Or upgrade instance type
```

### **Problem: Can't access via browser**

1. **Check Security Group/Firewall:**
   - AWS: EC2 → Security Groups → Inbound rules
   - GCP: VPC Network → Firewall rules

2. **Verify application is running:**
   ```bash
   docker ps
   curl http://localhost:8501
   ```

3. **Check public IP:**
   - AWS: EC2 Console → Instance → Public IPv4
   - GCP: Compute Engine → VM instances → External IP

### **Problem: SSL certificate issues**

```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

---

## 🎯 Next Steps

After deployment:

1. ✅ **Test thoroughly** with multiple users
2. ✅ **Setup monitoring alerts** (CloudWatch for AWS, Cloud Monitoring for GCP)
3. ✅ **Create backup strategy** (automated snapshots)
4. ✅ **Document your deployment** (server details, passwords, etc.)
5. ✅ **Plan for scaling** (if you expect high traffic)

---

## 📚 Additional Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [GCP Compute Engine Documentation](https://cloud.google.com/compute/docs)
- [Docker Documentation](https://docs.docker.com/)
- [Streamlit Cloud (Alternative)](https://streamlit.io/cloud)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## 💡 Pro Tips

1. **Use managed services when possible:** Consider AWS Fargate or GCP Cloud Run for serverless deployment
2. **Set up CI/CD:** Use GitHub Actions for automated deployments
3. **Implement rate limiting:** Protect your API from abuse
4. **Use CDN:** CloudFront (AWS) or Cloud CDN (GCP) for faster global access
5. **Monitor costs:** Set up billing alerts to avoid surprises

---

**Need Help?**
- AWS Support: [aws.amazon.com/support](https://aws.amazon.com/support)
- GCP Support: [cloud.google.com/support](https://cloud.google.com/support)
- Community: [Stack Overflow](https://stackoverflow.com/)

---

**🎉 Congratulations! Your RAG chatbot is now live on the cloud!** 🎉
