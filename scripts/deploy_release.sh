#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage:
  deploy_release.sh <release_archive_path> <release_id>

Environment variables:
  DEPLOY_ROOT                Deploy root path (default: /opt/neuralnote)
  COMPOSE_FILE               Compose file in release dir (default: docker-compose.prod.yml)
  HEALTHCHECK_FRONTEND_URL   Frontend health URL (default: http://127.0.0.1/)
  HEALTHCHECK_BACKEND_URL    Backend health URL (default: http://127.0.0.1/api/v1/health/ping)
  HEALTHCHECK_ATTEMPTS       Health retry count (default: 36)
  HEALTHCHECK_INTERVAL       Health retry interval seconds (default: 5)
EOF
}

if [[ $# -ne 2 ]]; then
  usage
  exit 1
fi

ARCHIVE_INPUT="$1"
RELEASE_ID="$2"

DEPLOY_ROOT="${DEPLOY_ROOT:-/opt/neuralnote}"
RELEASES_DIR="${DEPLOY_ROOT}/releases"
CURRENT_LINK="${DEPLOY_ROOT}/current"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
HEALTHCHECK_FRONTEND_URL="${HEALTHCHECK_FRONTEND_URL:-http://127.0.0.1/}"
HEALTHCHECK_BACKEND_URL="${HEALTHCHECK_BACKEND_URL:-http://127.0.0.1/api/v1/health/ping}"
HEALTHCHECK_ATTEMPTS="${HEALTHCHECK_ATTEMPTS:-36}"
HEALTHCHECK_INTERVAL="${HEALTHCHECK_INTERVAL:-5}"

if [[ ! -f "${ARCHIVE_INPUT}" ]]; then
  echo "[deploy] Archive not found: ${ARCHIVE_INPUT}" >&2
  exit 1
fi

mkdir -p "${RELEASES_DIR}"

ARCHIVE_PATH="$(readlink -f "${ARCHIVE_INPUT}")"
ARCHIVE_NAME="$(basename "${ARCHIVE_PATH}")"
STORED_ARCHIVE_PATH="${RELEASES_DIR}/${ARCHIVE_NAME}"
RELEASE_DIR="${RELEASES_DIR}/${RELEASE_ID}"

if [[ "${ARCHIVE_PATH}" != "${STORED_ARCHIVE_PATH}" ]]; then
  cp -f "${ARCHIVE_PATH}" "${STORED_ARCHIVE_PATH}"
fi

PREVIOUS_TARGET=""
if [[ -e "${CURRENT_LINK}" ]]; then
  PREVIOUS_TARGET="$(readlink -f "${CURRENT_LINK}" || true)"
fi

ROLLED_BACK=0
rollback() {
  local exit_code="${1:-1}"
  trap - ERR
  if [[ "${ROLLED_BACK}" -eq 1 ]]; then
    return
  fi
  ROLLED_BACK=1

  if [[ -n "${PREVIOUS_TARGET}" && -d "${PREVIOUS_TARGET}" ]]; then
    echo "[deploy] Rolling back to: ${PREVIOUS_TARGET}"
    ln -sfn "${PREVIOUS_TARGET}" "${CURRENT_LINK}"
    if [[ -f "${CURRENT_LINK}/${COMPOSE_FILE}" ]]; then
      (
        cd "${CURRENT_LINK}"
        docker compose -f "${COMPOSE_FILE}" up -d --build --remove-orphans
      ) || true
    fi
  else
    echo "[deploy] Skip rollback: previous release not found."
  fi

  exit "${exit_code}"
}

trap 'rollback $?' ERR

echo "[deploy] Preparing release directory: ${RELEASE_DIR}"
rm -rf "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}"
tar -xzf "${STORED_ARCHIVE_PATH}" -C "${RELEASE_DIR}"

if [[ ! -f "${RELEASE_DIR}/${COMPOSE_FILE}" ]]; then
  echo "[deploy] Compose file not found in release: ${RELEASE_DIR}/${COMPOSE_FILE}" >&2
  exit 1
fi

echo "[deploy] Switching current symlink -> ${RELEASE_DIR}"
ln -sfn "${RELEASE_DIR}" "${CURRENT_LINK}"

echo "[deploy] Starting services with docker compose"
(
  cd "${CURRENT_LINK}"
  docker compose -f "${COMPOSE_FILE}" up -d --build --remove-orphans
)

wait_for_url() {
  local name="$1"
  local url="$2"
  local attempt=1
  while [[ "${attempt}" -le "${HEALTHCHECK_ATTEMPTS}" ]]; do
    if curl -fsS "${url}" >/dev/null; then
      echo "[deploy] ${name} health check passed: ${url}"
      return 0
    fi
    echo "[deploy] Waiting for ${name} (${attempt}/${HEALTHCHECK_ATTEMPTS}): ${url}"
    sleep "${HEALTHCHECK_INTERVAL}"
    attempt=$((attempt + 1))
  done
  echo "[deploy] ${name} health check failed: ${url}" >&2
  return 1
}

wait_for_url "frontend" "${HEALTHCHECK_FRONTEND_URL}"
wait_for_url "backend" "${HEALTHCHECK_BACKEND_URL}"

(
  cd "${CURRENT_LINK}"
  docker compose -f "${COMPOSE_FILE}" ps
)

trap - ERR
echo "[deploy] Release deployed successfully: ${RELEASE_ID}"
