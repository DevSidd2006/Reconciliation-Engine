#!/usr/bin/env python3
"""
System Status Checker for Banking Reconciliation Engine
"""
import requests
import subprocess
import json
import time

def check_docker_containers():
    """Check if all required Docker containers are running"""
    print("🐳 Checking Docker containers...")
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'json'], 
                              capture_output=True, text=True, check=True)
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))
        
        required_containers = ['kafka-kafka-1', 'kafka-zookeeper-1', 'reconciliation_postgres', 'reconciliation_redis']
        running_containers = [c['Names'] for c in containers]
        
        for container in required_containers:
            if container in running_containers:
                print(f"   ✅ {container}")
            else:
                print(f"   ❌ {container} - NOT RUNNING")
        
        return len([c for c in required_containers if c in running_containers]) == len(required_containers)
    except Exception as e:
        print(f"   ❌ Error checking containers: {e}")
        return False

def check_backend_api():
    """Check if the backend API is responding"""
    print("\n🔧 Checking Backend API...")
    try:
        response = requests.get('http://localhost:8002', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend API: {data.get('message', 'OK')}")
            return True
        else:
            print(f"   ❌ Backend API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend API error: {e}")
        return False

def check_frontend():
    """Check if the frontend is accessible"""
    print("\n🎨 Checking Frontend...")
    try:
        response = requests.get('http://localhost:3001', timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible on http://localhost:3001")
            return True
        else:
            print(f"   ❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
        return False

def main():
    """Main status check function"""
    print("🏦 Banking Reconciliation Engine - System Status Check")
    print("=" * 60)
    
    # Check all components
    docker_ok = check_docker_containers()
    backend_ok = check_backend_api()
    frontend_ok = check_frontend()
    
    print("\n📊 System Status Summary:")
    print("=" * 30)
    print(f"Docker Containers: {'✅ OK' if docker_ok else '❌ ISSUES'}")
    print(f"Backend API:       {'✅ OK' if backend_ok else '❌ ISSUES'}")
    print(f"Frontend:          {'✅ OK' if frontend_ok else '❌ ISSUES'}")
    
    if all([docker_ok, backend_ok, frontend_ok]):
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n🌐 Access Points:")
        print("   • Frontend Dashboard: http://localhost:3001")
        print("   • Backend API:        http://localhost:8002")
        print("   • API Documentation:  http://localhost:8002/docs")
        print("\n🔐 Login Credentials:")
        print("   • Admin:    admin / admin123")
        print("   • Auditor:  auditor / auditor123")
    else:
        print("\n⚠️  SOME SYSTEMS HAVE ISSUES - Check the details above")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()