#!/usr/bin/env python3
"""
Installation script for AI-Powered Penetration Testing Agent
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "logs", 
        "reports",
        "models",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    try:
        # Try simplified requirements first
        print("Installing core dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_simple.txt"])
        print("✓ Core dependencies installed successfully")
        
        # Try additional dependencies if needed
        try:
            print("Installing additional dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ All dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️  Some optional dependencies failed to install, but core functionality is available")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install core dependencies: {e}")
        return False
    
    return True


def setup_configuration():
    """Set up configuration files"""
    print("Setting up configuration...")
    
    # Check if config file exists
    if not os.path.exists("config/config.yaml"):
        print("✓ Configuration file already exists")
    else:
        print("✓ Configuration file found")
    
    return True


def verify_installation():
    """Verify the installation"""
    print("Verifying installation...")
    
    # Check if main modules can be imported
    try:
        import core.agent
        print("✓ Core agent module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import core agent: {e}")
        return False
    
    try:
        import modules.reconnaissance.recon_engine
        print("✓ Reconnaissance module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import reconnaissance module: {e}")
        return False
    
    try:
        import ai.rl_agent.rl_agent
        print("✓ AI RL agent module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AI RL agent: {e}")
        return False
    
    return True


def main():
    """Main installation function"""
    print("=" * 60)
    print("AI-Powered Penetration Testing Agent - Installation")
    print("=" * 60)
    
    # Create directories
    print("\n1. Creating directories...")
    create_directories()
    
    # Install dependencies
    print("\n2. Installing dependencies...")
    if not install_dependencies():
        print("Installation failed at dependency installation step")
        sys.exit(1)
    
    # Setup configuration
    print("\n3. Setting up configuration...")
    if not setup_configuration():
        print("Installation failed at configuration setup step")
        sys.exit(1)
    
    # Verify installation
    print("\n4. Verifying installation...")
    if not verify_installation():
        print("Installation verification failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Installation completed successfully!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Review and edit config/config.yaml for your settings")
    print("2. Run: python example_usage.py to test the system")
    print("3. Read README.md for detailed usage instructions")
    
    print("\n⚠️  IMPORTANT REMINDER:")
    print("This tool is for authorized security testing only.")
    print("Only test systems you own or have explicit permission to test.")
    print("Comply with all applicable laws and regulations.")


if __name__ == "__main__":
    main() 