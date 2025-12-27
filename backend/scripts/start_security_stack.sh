#!/bin/bash

# =============================================================================
# AUTOMATED SECURITY STACK STARTUP SCRIPT
# =============================================================================
# This script starts the complete security stack with:
# - Keycloak (Identity Provider)
# - Traefik (HTTPS Reverse Proxy)
# - Backend API
# - Redis Cache
# - PostgreSQL Database
# - Automatic realm import
# - Dynamic token generation
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TOKENS_DIR="$PROJECT_ROOT/tmp"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Load environment variables
load_env() {
    local env_file="$PROJECT_ROOT/.env"
    if [[ ! -f "$env_file" ]]; then
        error "Environment file not found: $env_file"
        exit 1
    fi
    
    log "Loading environment variables from $env_file"
    set -a
    source "$env_file"
    set +a
    
    # Validate required variables
    local required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "KEYCLOAK_ADMIN_PASSWORD"
        "KEYCLOAK_SERVER_URL"
        "KEYCLOAK_REALM"
        "KEYCLOAK_CLIENT_ID"
        "KEYCLOAK_CLIENT_SECRET"
        "TRAEFIK_DOMAIN"
        "TRAEFIK_EMAIL"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable not set: $var"
            exit 1
        fi
    done
    
    success "Environment variables loaded successfully"
}

# Check if Docker is running
check_docker() {
    log "Checking Docker availability..."
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running or not accessible"
        exit 1
    fi
    success "Docker is running"
}

# Check if container exists and is running
container_status() {
    local container_name="$1"
    if docker ps -q -f name="$container_name" | grep -q .; then
        echo "running"
    elif docker ps -aq -f name="$container_name" | grep -q .; then
        echo "stopped"
    else
        echo "not_exists"
    fi
}

# Wait for service to be healthy
wait_for_service() {
    local service_name="$1"
    local url="$2"
    local max_attempts="${3:-30}"
    local sleep_time="${4:-5}"
    
    log "Waiting for $service_name to be ready at $url..."
    
    for ((i=1; i<=max_attempts; i++)); do
        if curl -f -s "$url" >/dev/null 2>&1; then
            success "$service_name is ready!"
            return 0
        fi
        
        if [[ $i -eq $max_attempts ]]; then
            error "$service_name failed to start after $((max_attempts * sleep_time)) seconds"
            return 1
        fi
        
        log "Attempt $i/$max_attempts: $service_name not ready yet, waiting ${sleep_time}s..."
        sleep "$sleep_time"
    done
}

# Wait for database to be ready
wait_for_database() {
    log "Waiting for PostgreSQL to be ready..."
    
    local max_attempts=30
    for ((i=1; i<=max_attempts; i++)); do
        if docker exec reconciliation_postgres pg_isready -U postgres >/dev/null 2>&1; then
            success "PostgreSQL is ready!"
            return 0
        fi
        
        if [[ $i -eq $max_attempts ]]; then
            error "PostgreSQL failed to start after $((max_attempts * 2)) seconds"
            return 1
        fi
        
        log "Attempt $i/$max_attempts: PostgreSQL not ready yet, waiting 2s..."
        sleep 2
    done
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    mkdir -p "$TOKENS_DIR"
    mkdir -p "$PROJECT_ROOT/letsencrypt"
    success "Directories created"
}

# Start Docker Compose services
start_services() {
    log "Starting Docker Compose services..."
    
    cd "$PROJECT_ROOT"
    
    # Check if services are already running
    local services_running=true
    local containers=("reconciliation_postgres" "reconciliation_redis" "reconciliation_keycloak" "reconciliation_traefik" "reconciliation_api")
    
    for container in "${containers[@]}"; do
        local status=$(container_status "$container")
        if [[ "$status" != "running" ]]; then
            services_running=false
            break
        fi
    done
    
    if [[ "$services_running" == "true" ]]; then
        warning "All services are already running, skipping Docker Compose start"
    else
        log "Starting services with docker-compose..."
        docker-compose -f docker-compose.traefik.yml up -d
        success "Docker Compose services started"
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Wait for API container to be ready
    local api_status=$(container_status "reconciliation_api")
    if [[ "$api_status" != "running" ]]; then
        error "API container is not running, cannot run migrations"
        return 1
    fi
    
    # Run Alembic migrations
    if docker exec reconciliation_api alembic upgrade head; then
        success "Database migrations completed successfully"
    else
        warning "Migration command failed or no migrations to run"
    fi
}

# Check if Keycloak realm exists
check_realm_exists() {
    local keycloak_url="$1"
    local realm="$2"
    
    log "Checking if realm '$realm' exists..."
    
    # Get admin token
    local admin_token
    admin_token=$(curl -s -X POST \
        "$keycloak_url/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$KEYCLOAK_ADMIN" \
        -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
        -d "grant_type=password" \
        -d "client_id=admin-cli" | \
        python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
    
    if [[ -z "$admin_token" ]]; then
        error "Failed to get admin token from Keycloak"
        return 1
    fi
    
    # Check if realm exists
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $admin_token" \
        "$keycloak_url/admin/realms/$realm")
    
    if [[ "$response_code" == "200" ]]; then
        return 0  # Realm exists
    else
        return 1  # Realm doesn't exist
    fi
}

# Import Keycloak realm
import_realm() {
    local keycloak_url="$KEYCLOAK_SERVER_URL"
    local realm="$KEYCLOAK_REALM"
    
    if check_realm_exists "$keycloak_url" "$realm"; then
        success "Realm '$realm' already exists, skipping import"
        return 0
    fi
    
    log "Importing Keycloak realm '$realm'..."
    
    # Get admin token
    local admin_token
    admin_token=$(curl -s -X POST \
        "$keycloak_url/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$KEYCLOAK_ADMIN" \
        -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
        -d "grant_type=password" \
        -d "client_id=admin-cli" | \
        python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
    
    if [[ -z "$admin_token" ]]; then
        error "Failed to get admin token for realm import"
        return 1
    fi
    
    # Import realm from JSON file
    local realm_file="$PROJECT_ROOT/keycloak/realm-export.json"
    if [[ ! -f "$realm_file" ]]; then
        error "Realm export file not found: $realm_file"
        return 1
    fi
    
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST \
        -H "Authorization: Bearer $admin_token" \
        -H "Content-Type: application/json" \
        -d "@$realm_file" \
        "$keycloak_url/admin/realms")
    
    if [[ "$response_code" == "201" ]]; then
        success "Realm '$realm' imported successfully"
    else
        error "Failed to import realm (HTTP $response_code)"
        return 1
    fi
}

# Generate test tokens
generate_tokens() {
    log "Generating test access tokens..."
    
    local python_script="$SCRIPT_DIR/generate_tokens.py"
    if [[ ! -f "$python_script" ]]; then
        error "Token generation script not found: $python_script"
        return 1
    fi
    
    # Generate tokens using Python script
    if python3 "$python_script"; then
        success "Test tokens generated successfully"
    else
        error "Failed to generate test tokens"
        return 1
    fi
}

# Validate services
validate_services() {
    log "Validating all services..."
    
    local keycloak_url="$KEYCLOAK_SERVER_URL"
    local realm="$KEYCLOAK_REALM"
    local domain="${TRAEFIK_DOMAIN:-localhost}"
    
    # Check Keycloak
    if ! wait_for_service "Keycloak" "$keycloak_url/realms/$realm" 10 3; then
        error "Keycloak validation failed"
        return 1
    fi
    
    # Check if HTTPS is enabled
    if [[ "${ENABLE_HTTPS:-false}" == "true" ]]; then
        log "Validating HTTPS configuration..."
        if curl -f -s "https://$domain" >/dev/null 2>&1; then
            success "HTTPS is active"
        else
            warning "HTTPS validation failed - this is normal for local development"
        fi
    fi
    
    # Check API endpoint
    if curl -f -s "http://localhost:8000/health" >/dev/null 2>&1; then
        success "API endpoint is responding"
    else
        warning "API health check failed"
    fi
    
    success "Service validation completed"
}

# Print final status
print_status() {
    local domain="${TRAEFIK_DOMAIN:-localhost}"
    
    echo ""
    echo "============================================================================"
    echo -e "${GREEN}SECURE STACK READY${NC}"
    echo "============================================================================"
    
    if [[ "${ENABLE_HTTPS:-false}" == "true" ]]; then
        echo -e "HTTPS active at: ${BLUE}https://$domain${NC}"
    else
        echo -e "HTTP active at: ${BLUE}http://$domain${NC}"
    fi
    
    echo -e "Keycloak admin: ${BLUE}http://localhost:8080${NC}"
    echo -e "API endpoint: ${BLUE}http://localhost:8000${NC}"
    echo -e "Traefik dashboard: ${BLUE}http://localhost:8081${NC}"
    echo -e "Tokens stored at: ${BLUE}$TOKENS_DIR/tokens.json${NC}"
    echo ""
    echo "Services running:"
    echo "  - PostgreSQL (internal)"
    echo "  - Redis (internal)"
    echo "  - Keycloak (port 8080)"
    echo "  - Traefik (ports 80, 443, 8081)"
    echo "  - Backend API (port 8000)"
    echo "============================================================================"
}

# Main execution
main() {
    log "Starting automated security stack deployment..."
    
    # Pre-flight checks
    load_env
    check_docker
    create_directories
    
    # Start services
    start_services
    
    # Wait for core services
    wait_for_database
    wait_for_service "Redis" "redis://localhost:6379" 10 2 || true  # Redis might not respond to HTTP
    wait_for_service "Keycloak" "$KEYCLOAK_SERVER_URL" 30 5
    
    # Configure Keycloak
    import_realm
    
    # Start API and run migrations
    wait_for_service "API" "http://localhost:8000/health" 20 3
    run_migrations
    
    # Generate tokens
    generate_tokens
    
    # Final validation
    validate_services
    
    # Print status
    print_status
    
    success "Security stack startup completed successfully!"
}

# Trap errors
trap 'error "Script failed at line $LINENO"' ERR

# Run main function
main "$@"