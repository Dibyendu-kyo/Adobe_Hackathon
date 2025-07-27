#!/usr/bin/env python3
"""
Startup script for the Adobe Hackathon Web Interface
"""

import os
import sys
import subprocess

def check_models():
    """Check if models are available for Round 1B."""
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    model1_path = os.path.join(models_dir, 'all-MiniLM-L6-v2')
    model2_path = os.path.join(models_dir, 'cross-encoder-ms-marco-MiniLM-L6-v2')
    
    if os.path.exists(model1_path) and os.path.exists(model2_path):
        print("✅ Models found - Round 1B will be available")
        return True
    else:
        print("⚠️  Models not found - Round 1B will be disabled")
        print("   Run 'python download_models.py' from the root directory to enable Round 1B")
        return False

def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def main():
    """Main startup function."""
    print("🚀 Starting Adobe Hackathon Web Interface")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the web_interface directory")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Check models
    models_available = check_models()
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("\n🌐 Starting Flask web server...")
    print("   Access the interface at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()