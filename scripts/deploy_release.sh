#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage:
  deploy_release.sh <release_archive_path> <release_id>

Environment variables:
  DEPLOY_ROOT                Deploy root path (default: /opt/neuralnote)
  COMPOSE_FILE               Compose file in release dir (default: docker-compose.prod.yml)
  DEPLOY_MODE                Deploy mode: build | registry (default: build)
  BACKEND_IMAGE              Backend image in registry mode
  FRONTEND_IMAGE             Frontend image in registry mode
  FRONTEND_BIND_ADDR         Frontend bind address (default: 0.0.0.0)
  FRONTEND_BIND_PORT         Frontend bind port (default: 80)
  REGISTRY_HOST              Registry host in registry mode
  REGISTRY_USER              Registry username in registry mode
  REGISTRY_PASSWORD          Registry password in registry mode
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
SHARED_DIR="${DEPLOY_ROOT}/shared"
SHARED_BACKEND_ENV="${SHARED_DIR}/backend.env"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
DEPLOY_MODE="${DEPLOY_MODE:-build}"
BACKEND_IMAGE="${BACKEND_IMAGE:-}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-}"
FRONTEND_BIND_ADDR="${FRONTEND_BIND_ADDR:-0.0.0.0}"
FRONTEND_BIND_PORT="${FRONTEND_BIND_PORT:-80}"
REGISTRY_HOST="${REGISTRY_HOST:-}"
REGISTRY_USER="${REGISTRY_USER:-}"
REGISTRY_PASSWORD="${REGISTRY_PASSWORD:-}"
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
RELEASE_BACKEND_ENV="${RELEASE_DIR}/src/backend/.env"
RELEASE_IMAGES_ENV="${RELEASE_DIR}/.deploy-images.env"

if [[ "${ARCHIVE_PATH}" != "${STORED_ARCHIVE_PATH}" ]]; then
  cp -f "${ARCHIVE_PATH}" "${STORED_ARCHIVE_PATH}"
fi

PREVIOUS_TARGET=""
PREVIOUS_BACKEND_ENV=""
if [[ -e "${CURRENT_LINK}" ]]; then
  PREVIOUS_TARGET="$(readlink -f "${CURRENT_LINK}" || true)"
  if [[ -f "${PREVIOUS_TARGET}/src/backend/.env" ]]; then
    PREVIOUS_BACKEND_ENV="${PREVIOUS_TARGET}/src/backend/.env"
  fi
fi

docker_login_registry() {
  if [[ "${DEPLOY_MODE}" != "registry" ]]; then
    return 0
  fi

  : "${REGISTRY_HOST:?REGISTRY_HOST is required in registry mode}"
  : "${REGISTRY_USER:?REGISTRY_USER is required in registry mode}"
  : "${REGISTRY_PASSWORD:?REGISTRY_PASSWORD is required in registry mode}"

  printf '%s' "${REGISTRY_PASSWORD}" | docker login "${REGISTRY_HOST}" -u "${REGISTRY_USER}" --password-stdin >/dev/null
}

prepare_backend_env() {
  mkdir -p "${SHARED_DIR}"

  if [[ ! -f "${SHARED_BACKEND_ENV}" ]]; then
    if [[ -n "${PREVIOUS_BACKEND_ENV}" ]]; then
      echo "[deploy] Shared backend env missing. Migrating from previous release."
      cp -f "${PREVIOUS_BACKEND_ENV}" "${SHARED_BACKEND_ENV}"
    else
      echo "[deploy] Missing backend env: ${SHARED_BACKEND_ENV}" >&2
      echo "[deploy] Provide /opt/neuralnote/shared/backend.env before first deployment." >&2
      return 1
    fi
  fi

  mkdir -p "$(dirname "${RELEASE_BACKEND_ENV}")"
  ln -sfn "${SHARED_BACKEND_ENV}" "${RELEASE_BACKEND_ENV}"
}

run_compose() {
  local run_dir="$1"

  if [[ "${DEPLOY_MODE}" == "registry" ]]; then
    local images_env="${run_dir}/.deploy-images.env"
    if [[ ! -f "${images_env}" ]]; then
      echo "[deploy] Missing image env file for registry mode: ${images_env}" >&2
      return 1
    fi
    docker_login_registry
    (
      cd "${run_dir}"
      docker compose --env-file "${images_env}" -f "${COMPOSE_FILE}" pull backend frontend
      docker compose --env-file "${images_env}" -f "${COMPOSE_FILE}" up -d --no-build --remove-orphans
    )
  else
    (
      cd "${run_dir}"
      docker compose -f "${COMPOSE_FILE}" up -d --build --remove-orphans
    )
  fi
}

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
      if [[ "${DEPLOY_MODE}" == "registry" && -f "${CURRENT_LINK}/.deploy-images.env" ]]; then
        (
          cd "${CURRENT_LINK}"
          docker_login_registry || true
          docker compose --env-file ".deploy-images.env" -f "${COMPOSE_FILE}" pull backend frontend || true
          docker compose --env-file ".deploy-images.env" -f "${COMPOSE_FILE}" up -d --no-build --remove-orphans
        ) || true
      else
        (
          cd "${CURRENT_LINK}"
          docker compose -f "${COMPOSE_FILE}" up -d --build --remove-orphans
        ) || true
      fi
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

prepare_backend_env

if [[ "${DEPLOY_MODE}" == "registry" ]]; then
  : "${BACKEND_IMAGE:?BACKEND_IMAGE is required in registry mode}"
  : "${FRONTEND_IMAGE:?FRONTEND_IMAGE is required in registry mode}"
  cat > "${RELEASE_IMAGES_ENV}" <<EOF
BACKEND_IMAGE=${BACKEND_IMAGE}
FRONTEND_IMAGE=${FRONTEND_IMAGE}
FRONTEND_BIND_ADDR=${FRONTEND_BIND_ADDR}
FRONTEND_BIND_PORT=${FRONTEND_BIND_PORT}
EOF
fi

echo "[deploy] Switching current symlink -> ${RELEASE_DIR}"
ln -sfn "${RELEASE_DIR}" "${CURRENT_LINK}"

echo "[deploy] Starting services with docker compose (mode: ${DEPLOY_MODE})"
run_compose "${CURRENT_LINK}"

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
  if [[ "${DEPLOY_MODE}" == "registry" && -f ".deploy-images.env" ]]; then
    docker compose --env-file ".deploy-images.env" -f "${COMPOSE_FILE}" ps
  else
    docker compose -f "${COMPOSE_FILE}" ps
  fi
)

trap - ERR
echo "[deploy] Release deployed successfully: ${RELEASE_ID}"
