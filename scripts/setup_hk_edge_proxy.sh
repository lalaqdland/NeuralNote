#!/usr/bin/env bash
set -Eeuo pipefail

MAIN_DOMAIN="${MAIN_DOMAIN:-neuralnote.capoo.tech}"
DEV_DOMAIN="${DEV_DOMAIN:-dev.neuralnote.capoo.tech}"
SHANGHAI_UPSTREAM="${SHANGHAI_UPSTREAM:-http://47.101.214.41:80}"
DEV_UPSTREAM_HOST_HEADER="${DEV_UPSTREAM_HOST_HEADER:-47.101.214.41}"
HK_LOCAL_UPSTREAM="${HK_LOCAL_UPSTREAM:-http://127.0.0.1:18080}"
LETSENCRYPT_EMAIL="${LETSENCRYPT_EMAIL:-}"

ACME_WEBROOT="${ACME_WEBROOT:-/var/www/certbot}"
NGINX_CONF_PATH="${NGINX_CONF_PATH:-/etc/nginx/conf.d/neuralnote-edge.conf}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[edge] This script must run as root." >&2
  exit 1
fi

install_packages() {
  echo "[edge] Installing nginx/certbot packages..."
  dnf -y install nginx certbot python3-certbot-nginx
}

write_bootstrap_http_config() {
  echo "[edge] Writing bootstrap HTTP config: ${NGINX_CONF_PATH}"
  cat > "${NGINX_CONF_PATH}" <<EOF
server {
    listen 80;
    server_name ${MAIN_DOMAIN};

    location ^~ /.well-known/acme-challenge/ {
        root ${ACME_WEBROOT};
        default_type "text/plain";
    }

    location / {
        proxy_pass ${HK_LOCAL_UPSTREAM};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

server {
    listen 80;
    server_name ${DEV_DOMAIN};

    location ^~ /.well-known/acme-challenge/ {
        root ${ACME_WEBROOT};
        default_type "text/plain";
    }

    location / {
        proxy_pass ${SHANGHAI_UPSTREAM};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host ${DEV_UPSTREAM_HOST_HEADER};
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
}

issue_certificate() {
  local certbot_args=(
    certonly
    --webroot
    -w "${ACME_WEBROOT}"
    -d "${MAIN_DOMAIN}"
    -d "${DEV_DOMAIN}"
    --non-interactive
    --agree-tos
    --keep-until-expiring
    --preferred-challenges http
  )

  if [[ -n "${LETSENCRYPT_EMAIL}" ]]; then
    certbot_args+=(--email "${LETSENCRYPT_EMAIL}")
  else
    certbot_args+=(--register-unsafely-without-email)
  fi

  echo "[edge] Issuing/renewing certificate for ${MAIN_DOMAIN}, ${DEV_DOMAIN}"
  certbot "${certbot_args[@]}"
}

write_https_config() {
  local fullchain="/etc/letsencrypt/live/${MAIN_DOMAIN}/fullchain.pem"
  local privkey="/etc/letsencrypt/live/${MAIN_DOMAIN}/privkey.pem"

  if [[ ! -f "${fullchain}" || ! -f "${privkey}" ]]; then
    echo "[edge] Certificate files not found under /etc/letsencrypt/live/${MAIN_DOMAIN}" >&2
    exit 1
  fi

  echo "[edge] Writing HTTPS config: ${NGINX_CONF_PATH}"
  cat > "${NGINX_CONF_PATH}" <<EOF
server {
    listen 80;
    server_name ${MAIN_DOMAIN} ${DEV_DOMAIN};

    location ^~ /.well-known/acme-challenge/ {
        root ${ACME_WEBROOT};
        default_type "text/plain";
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name ${MAIN_DOMAIN};

    ssl_certificate ${fullchain};
    ssl_certificate_key ${privkey};
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass ${HK_LOCAL_UPSTREAM};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

server {
    listen 443 ssl http2;
    server_name ${DEV_DOMAIN};

    ssl_certificate ${fullchain};
    ssl_certificate_key ${privkey};
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass ${SHANGHAI_UPSTREAM};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host ${DEV_UPSTREAM_HOST_HEADER};
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
}

setup_renew_job() {
  echo "[edge] Configuring certificate auto-renew..."

  if systemctl list-unit-files | grep -q '^certbot-renew.timer'; then
    systemctl enable --now certbot-renew.timer
    return 0
  fi

  if systemctl list-unit-files | grep -q '^certbot.timer'; then
    systemctl enable --now certbot.timer
    return 0
  fi

  cat > /etc/cron.d/certbot-renew-neuralnote <<'EOF'
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
17 3 * * * root certbot renew --quiet --deploy-hook "systemctl reload nginx"
EOF
}

main() {
  install_packages
  mkdir -p "${ACME_WEBROOT}"

  write_bootstrap_http_config
  nginx -t
  systemctl enable --now nginx
  systemctl reload nginx

  issue_certificate

  write_https_config
  nginx -t
  systemctl reload nginx

  setup_renew_job

  echo "[edge] Edge proxy setup complete."
  echo "[edge] MAIN_DOMAIN=${MAIN_DOMAIN} -> ${HK_LOCAL_UPSTREAM}"
  echo "[edge] DEV_DOMAIN=${DEV_DOMAIN} -> ${SHANGHAI_UPSTREAM} (Host=${DEV_UPSTREAM_HOST_HEADER})"
}

main "$@"
