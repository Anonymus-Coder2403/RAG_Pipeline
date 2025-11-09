#!/bin/bash

##############################################################################
# RAG Chatbot Deployment Script
# Automates deployment on fresh Ubuntu 22.04 server (AWS EC2 or GCP)
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_step() {
    echo -e "${BLUE}===> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run as root. Run as ubuntu user."
    exit 1
fi

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║     RAG Chatbot - Automated Cloud Deployment         ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Update system
print_step "Step 1/8: Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# Step 2: Install Docker
print_step "Step 2/8: Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_success "Docker installed"
else
    print_warning "Docker already installed"
fi

# Step 3: Install Docker Compose
print_step "Step 3/8: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed"
else
    print_warning "Docker Compose already installed"
fi

# Step 4: Setup firewall
print_step "Step 4/8: Configuring firewall..."
if ! command -v ufw &> /dev/null; then
    sudo apt install ufw -y
fi
sudo ufw --force enable
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 8501/tcp comment 'Streamlit'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
print_success "Firewall configured"

# Step 5: Create project directory
print_step "Step 5/8: Setting up project directory..."
PROJECT_DIR="$HOME/rag-chatbot"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR
print_success "Project directory created: $PROJECT_DIR"

# Step 6: Check for .env file
print_step "Step 6/8: Checking environment configuration..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    print_warning ".env file not found!"
    echo ""
    echo "Please create .env file with your configuration:"
    echo ""
    echo "Example .env content:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cat << 'EOF'
ENVIRONMENT=production
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K_RESULTS=4
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
EOF
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Create .env file now? (y/n): " create_env
    if [ "$create_env" = "y" ]; then
        read -p "Enter your Gemini API Key: " api_key
        cat > .env << EOF
ENVIRONMENT=production
GEMINI_API_KEY=$api_key
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K_RESULTS=4
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
EOF
        print_success ".env file created"
    else
        print_error "Cannot proceed without .env file. Exiting."
        exit 1
    fi
else
    print_success ".env file found"
fi

# Step 7: Setup swap space (if needed)
print_step "Step 7/8: Checking swap space..."
SWAP_SIZE=$(free -m | awk '/Swap:/ {print $2}')
if [ "$SWAP_SIZE" -lt 4096 ]; then
    print_warning "Swap space is low ($SWAP_SIZE MB). Creating 8GB swap..."
    sudo fallocate -l 8G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=8192
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    print_success "Swap space created (8GB)"
else
    print_success "Swap space sufficient ($SWAP_SIZE MB)"
fi

# Step 8: Build and start application
print_step "Step 8/8: Building and starting application..."
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found in $PROJECT_DIR"
    print_warning "Please upload your application files to: $PROJECT_DIR"
    exit 1
fi

# Check if Docker group membership is active
if ! groups | grep -q docker; then
    print_warning "Docker group membership not yet active. Please logout and login again."
    print_warning "Then run: cd $PROJECT_DIR && docker-compose up -d"
    exit 0
fi

docker-compose build
docker-compose up -d
print_success "Application started!"

echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║           🎉 DEPLOYMENT SUCCESSFUL! 🎉                ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Application Details:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Project Directory: $PROJECT_DIR"
echo "🌐 Access URL: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_PUBLIC_IP'):8501"
echo ""
echo "Useful Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "View logs:        docker-compose logs -f"
echo "Restart app:      docker-compose restart"
echo "Stop app:         docker-compose down"
echo "Update app:       git pull && docker-compose up -d --build"
echo "Check status:     docker ps"
echo "Check resources:  docker stats"
echo ""
echo "⚡ Monitoring initialization (may take 2-5 minutes)..."
echo "Run: docker-compose logs -f"
echo ""
