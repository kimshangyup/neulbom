#!/bin/bash

# Neulbom Production Deployment Script
# This script automates the deployment process to DigitalOcean

set -e  # Exit on error

echo "========================================="
echo "Neulbom Production Deployment"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/neulbom"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/neulbom"

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

# Navigate to project directory
cd $PROJECT_DIR

# 1. Pull latest code
print_info "Pulling latest code from repository..."
sudo -u www-data git pull origin main

# 2. Activate virtual environment
print_info "Activating virtual environment..."
source $VENV_DIR/bin/activate

# 3. Install/update dependencies
print_info "Installing dependencies..."
pip install -r requirements.txt --upgrade

# 4. Run database migrations
print_info "Running database migrations..."
python manage.py migrate --noinput

# 5. Collect static files
print_info "Collecting static files..."
python manage.py collectstatic --noinput

# 6. Restart services
print_info "Restarting uWSGI service..."
systemctl restart neulbom

print_info "Reloading Nginx..."
systemctl reload nginx

# 7. Wait for services to start
sleep 5

# 8. Health check
print_info "Performing health check..."
if curl -f -s https://seoul.zep.us/health/ > /dev/null; then
    print_info "Health check passed! ✓"
else
    print_error "Health check failed! ✗"
    print_warning "Checking service status..."
    systemctl status neulbom
    exit 1
fi

# 9. Display service status
print_info "Deployment completed successfully!"
echo ""
echo "Service Status:"
systemctl status neulbom --no-pager | head -n 10
echo ""
print_info "Application is running at: https://seoul.zep.us"

exit 0
