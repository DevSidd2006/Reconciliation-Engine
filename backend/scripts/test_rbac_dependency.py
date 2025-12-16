#!/usr/bin/env python3
"""
Test RBAC Dependency - Check if require_operator is working
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "app"))

def test_rbac_dependency():
    """Test RBAC dependency imports and functionality"""
    
    print("🔍 Testing RBAC Dependency")
    print("=" * 50)
    
    try:
        # Test import
        from security import require_operator, require_admin, require_auditor, require_viewer
        print("✅ RBAC imports successful")
        
        # Check if they are callable
        print(f"require_operator callable: {callable(require_operator)}")
        print(f"require_admin callable: {callable(require_admin)}")
        print(f"require_auditor callable: {callable(require_auditor)}")
        print(f"require_viewer callable: {callable(require_viewer)}")
        
        # Test the function types
        print(f"require_operator type: {type(require_operator)}")
        
    except Exception as e:
        print(f"❌ RBAC import failed: {e}")
        return False
    
    try:
        # Test RBAC manager
        from security.rbac import rbac_manager, RolePermissions
        print("✅ RBAC manager import successful")
        
        # Test role hierarchy
        test_roles = ["admin"]
        required_roles = ["operator"]
        has_access = RolePermissions.has_role(test_roles, required_roles)
        print(f"Admin has operator access: {has_access}")
        
    except Exception as e:
        print(f"❌ RBAC manager test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_rbac_dependency()