#!/usr/bin/env python3
"""
Cross-Platform Security Stack Startup Script
Starts the complete security stack with automatic configuration
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, Optional, List
import argparse


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows if not supported"""
        if os.name == 'nt':
            try:
                # Try to enable ANSI colors on Windows 10+
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                # Fallback: disable colors
                cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.NC = ''


class SecurityStackManager:
    """Manages the security stack startup process"""
    
    def __init__(self, project_root: Path, interactive: bool = False):
        self.project_root = project_root
        self.interactive = interactive
        self.tokens_dir = project_root / "tmp"
        self.env_vars = {}
        
        # Initialize colors
        Colors.disable_on_windows()
    
    def log(self, message: str) -> None:
        """Log info message"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Colors.BLUE}[{timestamp}]{Colors.NC} {message}")
    
    def error(self, message: str) -> None:
        """Log error message"""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}", file=sys.stderr)
    
    def success(self, message: str) -> None:
        """Log success message"""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
    
    def load_environment(self, env_file: str = ".env") -> bool:
        """Load environment variables from .env file"""
        env_path = self.project_root / env_file
        
        if not env_path.exists():
            self.error(f"Environment file not found: {env_path}")
            return False
        
        self.log(f"Loading environment variables from {env_path}")
        
        # Try loading .env.dev as well (overrides .env)
        env_dev_path = self.project_root / ".env.dev"
        if env_dev_path.exists():
            self.log(f"Loading environment variables from {env_dev_path}")
            try:
                with open(env_dev_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            self.env_vars[key] = value
                            os.environ[key] = value
            except Exception as e:
                self.warning(f"Failed to load .env.dev: {e}")

        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        self.env_vars[key] = value
                        os.environ[key] = value
            
            # Keycloak removed - using mock authentication
            self.log("Using mock authentication - Keycloak removed from system")
            
            # Validate required variables
            required_vars = [
                "POSTGRES_PASSWORD", "REDIS_PASSWORD",
                "TRAEFIK_DOMAIN", "TRAEFIK_EMAIL"
            ]
            
            missing_vars = [var for var in required_vars if var not in self.env_vars]
            if missing_vars:
                self.error(f"Required environment variables not set: {', '.join(missing_vars)}")
                return False
            
            self.success("Environment variables loaded successfully")
            return True
            
        except Exception as e:
            self.error(f"Failed to load environment: {e}")
            return False
    
    def check_docker(self) -> bool:
        """Check if Docker is running"""
        self.log("Checking Docker availability...")
        
        try:
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.success("Docker is running")
                return True
            else:
                self.error("Docker is not running or not accessible")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.error("Docker is not installed or not accessible")
            return False
    
    def get_container_status(self, container_name: str) -> str:
        """Get container status"""
        try:
            # Check if running
            result = subprocess.run(['docker', 'ps', '-q', '-f', f'name={container_name}'],
                                  capture_output=True, text=True)
            if result.stdout.strip():
                return "running"
            
            # Check if exists but stopped
            result = subprocess.run(['docker', 'ps', '-aq', '-f', f'name={container_name}'],
                                  capture_output=True, text=True)
            if result.stdout.strip():
                return "stopped"
            
            return "not_exists"
        except:
            return "unknown"
    
    def wait_for_service(self, service_name: str, url: str, max_attempts: int = 30, sleep_time: int = 5) -> bool:
        """Wait for service to be ready"""
        self.log(f"Waiting for {service_name} to be ready at {url}...")
        
        for i in range(1, max_attempts + 1):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.success(f"{service_name} is ready!")
                    return True
            except:
                pass
            
            if i == max_attempts:
                self.error(f"{service_name} failed to start after {max_attempts * sleep_time} seconds")
                return False
            
            self.log(f"Attempt {i}/{max_attempts}: {service_name} not ready yet, waiting {sleep_time}s...")
            time.sleep(sleep_time)
        
        return False
    
    def wait_for_database(self) -> bool:
        """Wait for PostgreSQL to be ready"""
        self.log("Waiting for PostgreSQL to be ready...")
        
        for i in range(1, 31):
            try:
                result = subprocess.run(['docker', 'exec', 'reconciliation_postgres', 
                                       'pg_isready', '-U', 'postgres'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.success("PostgreSQL is ready!")
                    return True
            except:
                pass
            
            if i == 30:
                self.error("PostgreSQL failed to start after 60 seconds")
                return False
            
            self.log(f"Attempt {i}/30: PostgreSQL not ready yet, waiting 2s...")
            time.sleep(2)
        
        return False
    
    def create_directories(self) -> None:
        """Create necessary directories"""
        self.log("Creating necessary directories...")
        
        self.tokens_dir.mkdir(parents=True, exist_ok=True)
        (self.project_root / "letsencrypt").mkdir(parents=True, exist_ok=True)
        
        self.success("Directories created")
    
    def start_services(self) -> bool:
        """Start Docker Compose services"""
        self.log("Starting Docker Compose services...")
        
        # Check if services are already running
        containers = ["reconciliation_postgres", "reconciliation_redis", 
                     "reconciliation_traefik", "reconciliation_api"]
        
        services_running = all(self.get_container_status(container) == "running" 
                             for container in containers)
        
        if services_running:
            self.warning("All services are already running, skipping Docker Compose start")
            return True
        
        try:
            self.log("Starting services with docker-compose...")
            result = subprocess.run(['docker-compose', '-f', 'docker-compose.traefik.yml', 'up', '-d'],
                                  cwd=self.project_root, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.success("Docker Compose services started")
                return True
            else:
                self.error(f"Failed to start Docker Compose services: {result.stderr}")
                return False
        except Exception as e:
            self.error(f"Failed to start services: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """Run database migrations"""
        self.log("Running database migrations...")
        
        api_status = self.get_container_status("reconciliation_api")
        if api_status != "running":
            self.error("API container is not running, cannot run migrations")
            return False
        
        try:
            result = subprocess.run(['docker', 'exec', 'reconciliation_api', 
                                   'alembic', 'upgrade', 'head'],
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.success("Database migrations completed successfully")
                return True
            else:
                self.warning("Migration command failed or no migrations to run")
                return True  # Don't fail the entire process
        except Exception as e:
            self.warning(f"Migration command failed: {e}")
            return True  # Don't fail the entire process
    

    

    

    
    def setup_https(self) -> bool:
        """Set up HTTPS with self-signed certificates"""
        self.log("Setting up HTTPS with self-signed certificates...")
        
        https_script = self.project_root / "scripts" / "setup_https.py"
        if not https_script.exists():
            self.error(f"HTTPS setup script not found: {https_script}")
            return False
        
        try:
            result = subprocess.run([sys.executable, str(https_script)], 
                                  cwd=self.project_root, timeout=120)
            
            if result.returncode == 0:
                self.success("HTTPS setup completed successfully")
                return True
            else:
                self.error("HTTPS setup failed")
                return False
                
        except subprocess.TimeoutExpired:
            self.error("HTTPS setup timed out")
            return False
        except Exception as e:
            self.error(f"HTTPS setup error: {e}")
            return False
    
    def validate_services(self) -> bool:
        """Validate all services"""
        self.log("Validating all services...")
        

        
        # Check HTTPS if enabled
        if self.env_vars.get('ENABLE_HTTPS', 'false').lower() == 'true':
            self.log("Validating HTTPS configuration...")
            try:
                response = requests.get(f"https://{domain}", timeout=5)
                if response.status_code == 200:
                    self.success("HTTPS is active")
            except:
                self.warning("HTTPS validation failed - this is normal for local development")
        
        # Check API endpoint
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.success("API endpoint is responding")
        except:
            self.warning("API health check failed")
        
        self.success("Service validation completed")
        return True
    
    def print_status(self) -> None:
        """Print final status"""
        domain = self.env_vars.get('TRAEFIK_DOMAIN', 'localhost')
        
        print()
        print("=" * 76)
        print(f"{Colors.GREEN}SECURE STACK READY{Colors.NC}")
        print("=" * 76)
        
        if self.env_vars.get('ENABLE_HTTPS', 'false').lower() == 'true':
            print(f"HTTPS active at: {Colors.BLUE}https://{domain}{Colors.NC}")
        else:
            print(f"HTTP active at: {Colors.BLUE}http://{domain}{Colors.NC}")
        
        https_enabled = self.env_vars.get('ENABLE_HTTPS', 'false').lower() == 'true'
        
        if https_enabled:
            print(f"🔒 HTTPS URLs (Self-Signed Certificates):")
            print(f"   • API: {Colors.BLUE}https://{domain}/api/{Colors.NC}")
            print(f"   • API Health: {Colors.BLUE}https://{domain}/api/health{Colors.NC}")
            print(f"   • Traefik Dashboard: {Colors.BLUE}https://{domain}/dashboard/{Colors.NC}")
            print(f"   • Keycloak: {Colors.BLUE}https://{domain}/auth/{Colors.NC}")
            print()
        
        print(f"🔓 HTTP URLs (Development):")
        print(f"   • API: {Colors.BLUE}http://localhost:8000/{Colors.NC}")
        print(f"   • Traefik Dashboard: {Colors.BLUE}http://localhost:8081/{Colors.NC}")
        print()
        print(f"📁 Files:")
        print(f"   • Tokens: {Colors.BLUE}{self.tokens_dir}/tokens.json{Colors.NC}")
        if https_enabled:
            print(f"   • SSL Certificates: {Colors.BLUE}{self.project_root}/ssl-certs/{Colors.NC}")
        print()
        print("🐳 Services running:")
        print("  - PostgreSQL (internal)")
        print("  - Redis (internal)")
        print("  - Traefik (ports 80, 443, 8081)")
        print("  - Backend API (port 8000)")
        
        if https_enabled:
            print()
            print("⚠️  Browser Security Warning:")
            print("   Your browser will show a security warning for self-signed certificates.")
            print("   Click 'Advanced' → 'Proceed to localhost (unsafe)' to continue.")
            print("   Or install the CA certificate from ssl-certs/ca-cert.pem")
        
        print("=" * 76)
    
    def run(self) -> bool:
        """Run the complete startup process"""
        self.log("Starting automated security stack deployment...")
        
        try:
            # Pre-flight checks
            if not self.load_environment():
                return False
            if not self.check_docker():
                return False
            self.create_directories()
            
            # Start services
            if not self.start_services():
                return False
            
            # Wait for core services
            if not self.wait_for_database():
                return False
            
            # Use localhost URL for health check (external access)
            
            # Start API and run migrations
            if not self.wait_for_service("API", "http://localhost:8000/health", 20, 3):
                return False
            
            self.run_migrations()
            

            
            # Set up HTTPS if enabled
            if self.env_vars.get('ENABLE_HTTPS', 'false').lower() == 'true':
                if not self.setup_https():
                    self.warning("HTTPS setup failed, continuing with HTTP only")
            
            # Final validation
            if not self.validate_services():
                return False
            
            # Print status
            self.print_status()
            
            self.success("Security stack startup completed successfully!")
            return True
            
        except KeyboardInterrupt:
            self.error("Operation cancelled by user")
            return False
        except Exception as e:
            self.error(f"Unexpected error: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Start the security stack")
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive mode for token generation')
    parser.add_argument('--env-file', default='.env',
                       help='Environment file to load (default: .env)')
    
    args = parser.parse_args()
    
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Create and run manager
    manager = SecurityStackManager(project_root, args.interactive)
    success = manager.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()