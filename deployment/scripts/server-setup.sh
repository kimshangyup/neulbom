#!/bin/bash

# Neulbom Server Initial Setup Script
# This script sets up a fresh DigitalOcean droplet for hosting Neulbom

set -e  # Exit on error

echo "========================================="
echo "Neulbom Server Setup"
echo "========================================="

# Update system packages
echo "[1/12] Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Python 3.8 and dependencies
echo "[2/12] Installing Python 3.8..."
apt-get install -y python3.8 python3.8-venv python3.8-dev python3-pip

# Install MySQL 8.0
echo "[3/12] Installing MySQL 8.0..."
apt-get install -y mysql-server mysql-client libmysqlclient-dev

# Install Nginx
echo "[4/12] Installing Nginx..."
apt-get install -y nginx

# Install system dependencies
echo "[5/12] Installing system dependencies..."
apt-get install -y git gcc pkg-config

# Install Let's Encrypt for SSL
echo "[6/12] Installing Certbot for SSL..."
apt-get install -y certbot python3-certbot-nginx

# Create project directory
echo "[7/12] Creating project directory..."
mkdir -p /var/www/neulbom
chown -R www-data:www-data /var/www/neulbom

# Create log directory
echo "[8/12] Creating log directories..."
mkdir -p /var/log/neulbom
mkdir -p /var/log/uwsgi
chown -R www-data:www-data /var/log/neulbom
chown -R www-data:www-data /var/log/uwsgi

# Clone repository (will need to configure git credentials)
echo "[9/12] Clone repository manually after this script completes:"
echo "  cd /var/www && sudo -u www-data git clone <repository-url> neulbom"

# Setup MySQL database
echo "[10/12] Setting up MySQL database..."
echo "Run the following MySQL commands manually:"
echo "  CREATE DATABASE neulbom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "  CREATE USER 'neulbom_user'@'localhost' IDENTIFIED BY 'your_password';"
echo "  GRANT ALL PRIVILEGES ON neulbom.* TO 'neulbom_user'@'localhost';"
echo "  FLUSH PRIVILEGES;"

# Setup firewall
echo "[11/12] Configuring firewall..."
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw --force enable

# Install fail2ban for security
echo "[12/12] Installing fail2ban..."
apt-get install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban

echo ""
echo "========================================="
echo "Server setup completed!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Clone the repository to /var/www/neulbom"
echo "2. Create Python virtual environment:"
echo "   cd /var/www/neulbom"
echo "   python3.8 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "3. Create .env file with production settings"
echo "4. Setup MySQL database (see commands above)"
echo "5. Run migrations: python manage.py migrate"
echo "6. Collect static files: python manage.py collectstatic"
echo "7. Copy deployment files to system locations:"
echo "   cp deployment/nginx/neulbom.conf /etc/nginx/sites-available/"
echo "   ln -s /etc/nginx/sites-available/neulbom.conf /etc/nginx/sites-enabled/"
echo "   cp deployment/uwsgi.ini /etc/uwsgi/apps-enabled/"
echo "   cp deployment/systemd/neulbom.service /etc/systemd/system/"
echo "8. Get SSL certificate:"
echo "   certbot --nginx -d seoul.zep.us -d www.seoul.zep.us"
echo "9. Start services:"
echo "   systemctl daemon-reload"
echo "   systemctl enable neulbom"
echo "   systemctl start neulbom"
echo "   systemctl restart nginx"
echo ""
