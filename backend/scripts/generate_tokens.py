#!/usr/bin/env python3
"""
Dynamic Token Generation Script
Generates test access tokens for different user roles without hardcoding credentials
"""

import os
import sys
import json
import requests
import getpass
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)


class TokenGenerator:
    """Generates access tokens for Keycloak users"""
    
    def __init__(self):
        # Use localhost for token generation (external access)
        # Extract port from public issuer URL if available
        public_issuer = os.getenv('KEYCLOAK_PUBLIC_ISSUER', 'http://localhost:8082/realms/reconciliation')
        self.keycloak_url = public_issuer.replace('/realms/reconciliation', '')
        
        # Fallback to localhost:8082 if not properly configured
        if 'keycloak:' in self.keycloak_url or not self.keycloak_url.startswith('http'):
            self.keycloak_url = 'http://localhost:8082'
            
        self.realm = os.getenv('KEYCLOAK_REALM', 'reconciliation')
        self.client_id = os.getenv('KEYCLOAK_CLIENT_ID', 'reconciliation-api')
        self.client_secret = os.getenv('KEYCLOAK_CLIENT_SECRET')
        
        # Validate required environment variables
        if not self.client_secret:
            raise ValueError("KEYCLOAK_CLIENT_SECRET environment variable is required")
        
        self.token_endpoint = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
        
        # Set public URLs for consistency
        public_issuer = f"{self.keycloak_url}/realms/{self.realm}"
        public_jwks = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/certs"
        
        # Set environment variables if not already set
        if not os.getenv('KEYCLOAK_PUBLIC_ISSUER'):
            os.environ['KEYCLOAK_PUBLIC_ISSUER'] = public_issuer
        if not os.getenv('KEYCLOAK_PUBLIC_JWKS_URL'):
            os.environ['KEYCLOAK_PUBLIC_JWKS_URL'] = public_jwks
        
        # Default test users (can be overridden by environment)
        self.test_users = {
            'admin': {
                'username': os.getenv('TEST_ADMIN_USER', 'admin'),
                'password': os.getenv('TEST_ADMIN_PASS', 'admin123'),
                'role': 'admin'
            },
            'auditor': {
                'username': os.getenv('TEST_AUDITOR_USER', 'auditor'),
                'password': os.getenv('TEST_AUDITOR_PASS', 'auditor123'),
                'role': 'auditor'
            },
            'operator': {
                'username': os.getenv('TEST_OPERATOR_USER', 'operator'),
                'password': os.getenv('TEST_OPERATOR_PASS', 'operator123'),
                'role': 'operator'
            },
            'viewer': {
                'username': os.getenv('TEST_VIEWER_USER', 'viewer'),
                'password': os.getenv('TEST_VIEWER_PASS', 'viewer123'),
                'role': 'viewer'
            }
        }
    
    def get_token(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Get access token for a user"""
        try:
            payload = {
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': username,
                'password': password,
                'scope': 'openid profile email roles'
            }
            
            response = requests.post(
                self.token_endpoint,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get token for {username}: HTTP {response.status_code}")
                if response.status_code == 401:
                    print("  - Check username/password")
                elif response.status_code == 400:
                    print("  - Check client configuration")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Network error getting token for {username}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error getting token for {username}: {e}")
            return None
    
    def validate_token(self, token: str) -> bool:
        """Validate token by calling userinfo endpoint"""
        try:
            userinfo_endpoint = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/userinfo"
            response = requests.get(
                userinfo_endpoint,
                headers={'Authorization': f'Bearer {token}'},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def generate_all_tokens(self, interactive: bool = False) -> Dict[str, Any]:
        """Generate tokens for all test users"""
        tokens = {
            'generated_at': self._get_timestamp(),
            'keycloak_url': self.keycloak_url,
            'realm': self.realm,
            'client_id': self.client_id,
            'tokens': {}
        }
        
        print(f"Generating tokens for realm '{self.realm}' at {self.keycloak_url}")
        print("=" * 60)
        
        for role, user_info in self.test_users.items():
            username = user_info['username']
            password = user_info['password']
            
            # Interactive mode: prompt for credentials
            if interactive:
                print(f"\nGenerating token for {role.upper()} user:")
                username = input(f"Username [{username}]: ").strip() or username
                password = getpass.getpass(f"Password: ") or password
            
            print(f"Getting token for {role} ({username})...", end=' ')
            
            token_data = self.get_token(username, password)
            if token_data:
                access_token = token_data.get('access_token')
                if access_token and self.validate_token(access_token):
                    tokens['tokens'][f'TOKEN_{role.upper()}'] = {
                        'access_token': access_token,
                        'refresh_token': token_data.get('refresh_token'),
                        'token_type': token_data.get('token_type', 'Bearer'),
                        'expires_in': token_data.get('expires_in'),
                        'username': username,
                        'role': role
                    }
                    print("✓ SUCCESS")
                else:
                    print("✗ INVALID TOKEN")
                    tokens['tokens'][f'TOKEN_{role.upper()}'] = None
            else:
                print("✗ FAILED")
                tokens['tokens'][f'TOKEN_{role.upper()}'] = None
        
        return tokens
    
    def save_tokens(self, tokens: Dict[str, Any], output_file: str) -> bool:
        """Save tokens to JSON file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"\nTokens saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving tokens: {e}")
            return False
    
    def print_summary(self, tokens: Dict[str, Any]) -> None:
        """Print token generation summary"""
        print("\n" + "=" * 60)
        print("TOKEN GENERATION SUMMARY")
        print("=" * 60)
        
        successful = 0
        failed = 0
        
        for token_name, token_data in tokens['tokens'].items():
            if token_data:
                successful += 1
                role = token_data['role']
                username = token_data['username']
                expires_in = token_data.get('expires_in', 'unknown')
                print(f"✓ {token_name}: {role} ({username}) - expires in {expires_in}s")
            else:
                failed += 1
                print(f"✗ {token_name}: FAILED")
        
        print(f"\nResults: {successful} successful, {failed} failed")
        
        if successful > 0:
            print(f"\nTokens are ready for use!")
            print("Environment variables you can set:")
            for token_name, token_data in tokens['tokens'].items():
                if token_data:
                    print(f"export {token_name}='{token_data['access_token'][:20]}...'")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """Main function"""
    try:
        # Parse command line arguments
        interactive = '--interactive' in sys.argv or '-i' in sys.argv
        
        # Determine output file
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        output_file = project_root / 'tmp' / 'tokens.json'
        
        # Override output file if specified
        if '--output' in sys.argv:
            idx = sys.argv.index('--output')
            if idx + 1 < len(sys.argv):
                output_file = Path(sys.argv[idx + 1])
        
        print("Dynamic Token Generator")
        print("=" * 60)
        print(f"Output file: {output_file}")
        print(f"Interactive mode: {'ON' if interactive else 'OFF'}")
        
        # Generate tokens
        generator = TokenGenerator()
        tokens = generator.generate_all_tokens(interactive=interactive)
        
        # Save tokens
        if generator.save_tokens(tokens, str(output_file)):
            generator.print_summary(tokens)
            
            # Exit with error if no tokens were generated
            successful_tokens = sum(1 for t in tokens['tokens'].values() if t is not None)
            if successful_tokens == 0:
                print("\nERROR: No tokens were generated successfully!")
                sys.exit(1)
            else:
                print(f"\nSUCCESS: Generated {successful_tokens} tokens")
                sys.exit(0)
        else:
            print("ERROR: Failed to save tokens")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()