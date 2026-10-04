#!/bin/bash
set -e

echo "==> Installing Docker..."
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com | sh
fi

echo "==> Configuring firewall..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "==> Preparing .env..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "⚠️  Отредактируйте .env, укажите пароли и email, затем запустите:"
  echo "    bash bootstrap.sh"
  echo ""
  exit 0
fi

echo "==> Starting services..."
docker compose up -d --build

echo "==> Waiting for API to start (10s)..."
sleep 10

echo "==> Requesting SSL certificate..."
docker compose run --rm certbot certonly --webroot \
  -w /var/www/certbot \
  -d "$(grep DOMAIN .env | cut -d= -f2)" \
  -d "www.$(grep DOMAIN .env | cut -d= -f2)" \
  --email "$(grep EMAIL .env | cut -d= -f2)" \
  --agree-tos --no-eff-email || echo "⚠️  SSL не получен, проверьте DNS"

echo "==> Reloading nginx..."
docker compose restart nginx

echo ""
echo "✅ Done! Откройте: https://$(grep DOMAIN .env | cut -d= -f2)/docs"
