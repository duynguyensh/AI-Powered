#!/usr/bin/env python3
"""
Simple test script to verify the AI-Powered Penetration Testing Agent
"""

import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from core.agent import PentestAgent
        print("✓ PentestAgent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PentestAgent: {e}")
        return False
    
    try:
        from modules.reconnaissance.recon_engine import ReconnaissanceEngine
        print("✓ ReconnaissanceEngine imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ReconnaissanceEngine: {e}")
        return False
    
    try:
        from ai.rl_agent.rl_agent import RLAgent
        print("✓ RLAgent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import RLAgent: {e}")
        return False
    
    try:
        from config.safety_manager import SafetyManager
        print("✓ SafetyManager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SafetyManager: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        import yaml
        with open("config/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        required_sections = ["safety", "ai", "scope", "reconnaissance"]
        for section in required_sections:
            if section in config:
                print(f"✓ Configuration section '{section}' found")
            else:
                print(f"✗ Configuration section '{section}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_directory_structure():
    """Test that required directories exist"""
    print("\nTesting directory structure...")
    
    required_dirs = ["core", "modules", "ai", "config", "reporting"]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ Directory '{directory}' exists")
        else:
            print(f"✗ Directory '{directory}' missing")
            return False
    
    return True


def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\nTesting basic functionality...")
    
    try:
        import yaml
        with open("config/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        from config.safety_manager import SafetyManager
        safety_manager = SafetyManager(config)
        
        summary = safety_manager.get_safety_summary()
        if isinstance(summary, dict):
            print("✓ Safety manager working correctly")
        else:
            print("✗ Safety manager not working correctly")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("AI-Powered Penetration Testing Agent - System Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Directory Structure", test_directory_structure),
        ("Configuration", test_configuration),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: python install.py to install dependencies")
        print("2. Run: python example_usage.py to see the system in action")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure all files are in the correct locations")
        print("2. Check that Python 3.8+ is installed")
        print("3. Run: python install.py to install dependencies")
    
    print("=" * 60)


if __name__ == "__main__":
    main() 
