# ⚡ Quick Deploy Cheat Sheet

**5-Minute Cloud Deployment Reference**

---

## 🚀 AWS EC2 - Quick Commands

### **1. Connect to EC2**
```bash
ssh -i ~/path/to/key.pem ubuntu@YOUR_IP
```

### **2. Install Docker (One-liner)**
```bash
curl -fsSL https://get.docker.com | sh && \
sudo usermod -aG docker $USER && \
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
sudo chmod +x /usr/local/bin/docker-compose && \
exit
```

### **3. Deploy App**
```bash
# Reconnect and run:
mkdir ~/rag-chatbot && cd ~/rag-chatbot
git clone YOUR_REPO_URL .
nano .env  # Add GEMINI_API_KEY
docker-compose up -d
```

### **4. Check Status**
```bash
docker ps
docker-compose logs -f
```

**Access:** `http://YOUR_IP:8501`

---

## 🚀 GCP - Quick Commands

### **1. Connect to VM**
```bash
gcloud compute ssh INSTANCE_NAME --zone=ZONE
```

### **2. Install Docker (Same as AWS)**
```bash
curl -fsSL https://get.docker.com | sh && \
sudo usermod -aG docker $USER && \
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
sudo chmod +x /usr/local/bin/docker-compose && \
exit
```

### **3. Deploy App (Same as AWS)**
```bash
mkdir ~/rag-chatbot && cd ~/rag-chatbot
git clone YOUR_REPO_URL .
nano .env  # Add GEMINI_API_KEY
docker-compose up -d
```

**Access:** `http://EXTERNAL_IP:8501`

---

## 🛠️ Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart app
docker-compose restart

# Stop app
docker-compose down

# Update app
git pull && docker-compose up -d --build

# Check resources
docker stats
free -h
df -h

# Check processes
docker ps -a
```

---

## 🔒 Security Checklist

```bash
# Setup firewall
sudo ufw allow 22/tcp
sudo ufw allow 8501/tcp
sudo ufw enable

# Disable password SSH
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

---

## 💰 Cost Comparison

| Provider | Instance | RAM | Cost/Month | Free Tier |
|----------|----------|-----|------------|-----------|
| AWS | t3.medium | 4GB | $30 | 750 hrs (12 mo) |
| AWS | t3.large | 8GB | $60 | No |
| GCP | e2-standard-2 | 8GB | $49 | $300 credit (90 days) |
| GCP | e2-standard-4 | 16GB | $98 | $300 credit (90 days) |

---

## 📝 .env Template

```env
ENVIRONMENT=production
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K_RESULTS=4
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
```

---

## 🌐 Setup Domain + SSL (Nginx)

```bash
# Install Nginx + Certbot
sudo apt install nginx certbot python3-certbot-nginx -y

# Create config
sudo nano /etc/nginx/sites-available/rag-chatbot
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable and get SSL
sudo ln -s /etc/nginx/sites-available/rag-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🚨 Troubleshooting

**App won't start:**
```bash
docker-compose logs
docker-compose down
docker-compose up -d --build
```

**Out of memory:**
```bash
# Add 8GB swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Can't connect:**
1. Check security group/firewall allows port 8501
2. Check `docker ps` shows container running
3. Verify public IP is correct

---

## 📞 Quick Links

- **AWS Console:** https://console.aws.amazon.com
- **GCP Console:** https://console.cloud.google.com
- **Full Guide:** See `CLOUD_DEPLOYMENT_GUIDE.md`
