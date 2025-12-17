#!/usr/bin/env python3
"""
Complete Stack Setup Script
One-command setup for the entire banking reconciliation system
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Tuple


class CompleteStackSetup:
    """Handles complete stack setup and validation"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        self.frontend_dir = project_root / "frontend"
        
    def print_header(self, title: str) -> None:
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str) -> None:
        """Print step"""
        print(f"\n📋 {step}")
        print("-" * 40)
    
    def run_command(self, cmd: List[str], cwd: Path = None, timeout: int = 300) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                print(f"✅ Command succeeded: {' '.join(cmd)}")
                return True, result.stdout
            else:
                print(f"❌ Command failed: {' '.join(cmd)}")
                print(f"Error: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Command timed out: {' '.join(cmd)}")
            return False, "Command timed out"
        except Exception as e:
            print(f"💥 Command error: {e}")
            return False, str(e)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        self.print_step("Checking Prerequisites")
        
        prerequisites = [
            (["docker", "--version"], "Docker"),
            (["docker-compose", "--version"], "Docker Compose"),
            (["python", "--version"], "Python"),
            (["node", "--version"], "Node.js"),
            (["npm", "--version"], "NPM")
        ]
        
        all_good = True
        for cmd, name in prerequisites:
            success, output = self.run_command(cmd, timeout=10)
            if success:
                version = output.strip().split('\n')[0]
                print(f"✅ {name}: {version}")
            else:
                print(f"❌ {name}: Not found or not working")
                all_good = False
        
        return all_good
    
    def setup_backend(self) -> bool:
        """Setup backend environment"""
        self.print_step("Setting up Backend Environment")
        
        # Check if virtual environment exists
        venv_dir = self.backend_dir / "venv"
        if not venv_dir.exists():
            print("Creating Python virtual environment...")
            success, _ = self.run_command(
                ["python", "-m", "venv", "venv"], 
                cwd=self.backend_dir
            )
            if not success:
                return False
        else:
            print("✅ Virtual environment already exists")
        
        # Install Python dependencies
        print("Installing Python dependencies...")
        if os.name == 'nt':  # Windows
            pip_cmd = str(venv_dir / "Scripts" / "pip.exe")
        else:  # Linux/Mac
            pip_cmd = str(venv_dir / "bin" / "pip")
        
        success, _ = self.run_command([
            pip_cmd, "install", "--upgrade", "pip"
        ], cwd=self.backend_dir)
        
        if not success:
            return False
        
        success, _ = self.run_command([
            pip_cmd, "install", "-r", "requirements.txt"
        ], cwd=self.backend_dir)
        
        return success
    
    def setup_frontend(self) -> bool:
        """Setup frontend environment"""
        self.print_step("Setting up Frontend Environment")
        
        # Check if node_modules exists
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            print("Installing Node.js dependencies...")
            success, _ = self.run_command(
                ["npm", "install"], 
                cwd=self.frontend_dir,
                timeout=600  # NPM can be slow
            )
            if not success:
                return False
        else:
            print("✅ Node modules already installed")
        
        return True
    
    def start_security_stack(self) -> bool:
        """Start the complete security stack"""
        self.print_step("Starting Security Stack")
        
        # Use the Python startup script for cross-platform compatibility
        startup_script = self.backend_dir / "scripts" / "start_security_stack.py"
        
        if not startup_script.exists():
            print(f"❌ Startup script not found: {startup_script}")
            return False
        
        print("Starting complete security stack...")
        print("This may take several minutes...")
        
        success, output = self.run_command([
            sys.executable, str(startup_script)
        ], timeout=600)  # 10 minutes timeout
        
        if success:
            print("✅ Security stack started successfully")
            return True
        else:
            print("❌ Security stack startup failed")
            print("Check the output above for details")
            return False
    
    def test_tokens(self) -> bool:
        """Test generated tokens"""
        self.print_step("Testing Generated Tokens")
        
        test_script = self.backend_dir / "scripts" / "test_tokens.py"
        
        if not test_script.exists():
            print(f"❌ Test script not found: {test_script}")
            return False
        
        print("Testing API tokens...")
        success, _ = self.run_command([
            sys.executable, str(test_script)
        ], timeout=60)
        
        return success
    
    def print_final_status(self) -> None:
        """Print final setup status"""
        self.print_header("🎉 SETUP COMPLETE!")
        
        print("Your banking reconciliation system is ready!")
        print()
        print("🌐 Access Points:")
        print("  • API Documentation: http://localhost:8000/docs")
        print("  • API Health: http://localhost:8000/health")

        print("  • Traefik Dashboard: http://localhost:8081")
        print()
        print("🔑 Test Users:")
        print("  • admin/admin123 (Full access)")
        print("  • auditor/auditor123 (Audit access)")
        print("  • operator/operator123 (Operations)")
        print("  • viewer/viewer123 (Read-only)")
        print()
        print("📁 Important Files:")
        print(f"  • Tokens: {self.backend_dir}/tmp/tokens.json")
        print(f"  • Environment: {self.backend_dir}/.env")
        print(f"  • Logs: Check Docker logs")
        print()
        print("🛠️  Development Commands:")
        print("  • Start frontend: cd frontend && npm run dev")
        print("  • View logs: docker-compose logs -f")
        print("  • Stop stack: docker-compose down")
        print()
        print("📚 Next Steps:")
        print("  1. Open http://localhost:8000/docs to explore the API")
        print("  2. Use tokens from tmp/tokens.json for authentication")
        print("  3. Check the README files for detailed documentation")
        print()
        print("🎯 Happy coding!")
    
    def run_complete_setup(self) -> bool:
        """Run the complete setup process"""
        self.print_header("Complete Banking Reconciliation System Setup")
        
        print("This script will set up the complete system including:")
        print("  • Backend API with virtual environment")
        print("  • Frontend dependencies")
        print("  • Docker containers (PostgreSQL, Redis, Traefik)")
        print("  • Mock authentication for development")
        print("  • Health checks and validation")
        print()
        
        # Confirm with user
        try:
            response = input("Continue with setup? [Y/n]: ").strip().lower()
            if response and response not in ['y', 'yes']:
                print("Setup cancelled by user")
                return False
        except KeyboardInterrupt:
            print("\nSetup cancelled by user")
            return False
        
        # Run setup steps
        steps = [
            ("Prerequisites", self.check_prerequisites),
            ("Backend Setup", self.setup_backend),
            ("Frontend Setup", self.setup_frontend),
            ("Security Stack", self.start_security_stack),
            ("Token Testing", self.test_tokens)
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n❌ Setup failed at step: {step_name}")
                    print("Please check the errors above and try again")
                    return False
            except KeyboardInterrupt:
                print(f"\n⏹️  Setup cancelled during: {step_name}")
                return False
            except Exception as e:
                print(f"\n💥 Unexpected error in {step_name}: {e}")
                return False
        
        # Success!
        self.print_final_status()
        return True


def main():
    """Main function"""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # Go up two levels from backend/scripts/
    
    print(f"Project root: {project_root}")
    print(f"Backend dir: {project_root / 'backend'}")
    print(f"Frontend dir: {project_root / 'frontend'}")
    
    # Verify project structure
    if not (project_root / "backend").exists():
        print("❌ Backend directory not found. Are you in the right location?")
        sys.exit(1)
    
    if not (project_root / "frontend").exists():
        print("❌ Frontend directory not found. Are you in the right location?")
        sys.exit(1)
    
    # Run setup
    setup = CompleteStackSetup(project_root)
    success = setup.run_complete_setup()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()