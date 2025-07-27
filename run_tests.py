#!/usr/bin/env python3
"""
Comprehensive test runner for both Round 1A and Round 1B
"""

import os
import sys
import subprocess
import json
import time


def check_prerequisites():
    """Check if all prerequisites are met."""
    
    print("🔍 Checking prerequisites...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    
    # Check for sample PDFs
    sample_pdfs = ["sample.pdf", "sample1.pdf"]
    south_france_pdfs = [f for f in os.listdir('.') if f.startswith('South of France') and f.endswith('.pdf')]
    
    if not any(os.path.exists(pdf) for pdf in sample_pdfs):
        issues.append("No sample PDFs found for Round 1A testing")
    
    if len(south_france_pdfs) < 3:
        issues.append(f"Only {len(south_france_pdfs)} South of France PDFs found (need 3+ for Round 1B)")
    
    # Check models for Round 1B
    if not os.path.exists("models/all-MiniLM-L6-v2"):
        issues.append("Models not found - run 'python download_models.py' first")
    
    # Check Round 1A dependencies
    try:
        import fitz
    except ImportError:
        issues.append("PyMuPDF not installed - run 'pip install PyMuPDF==1.23.14'")
    
    # Check Round 1B dependencies (only if models exist)
    if os.path.exists("models/all-MiniLM-L6-v2"):
        try:
            import torch
            import sentence_transformers
        except ImportError:
            issues.append("Round 1B dependencies missing - run 'pip install -r round1b/requirements.txt'")
    
    if issues:
        print("❌ Prerequisites not met:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    print("✅ All prerequisites met!")
    return True


def test_docker_builds():
    """Test Docker builds for both rounds."""
    
    print("\n🐳 Testing Docker builds...")
    
    # Test Round 1A Docker build
    print("Building Round 1A container...")
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "round1a", "./round1a"],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            print("✅ Round 1A Docker build successful")
        else:
            print(f"❌ Round 1A Docker build failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Round 1A Docker build timed out")
        return False
    except FileNotFoundError:
        print("⚠️  Docker not found - skipping Docker tests")
        return True
    
    # Test Round 1B Docker build
    print("Building Round 1B container...")
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "round1b", "./round1b"],
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            print("✅ Round 1B Docker build successful")
        else:
            print(f"❌ Round 1B Docker build failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Round 1B Docker build timed out")
        return False
    
    return True


def run_python_tests():
    """Run Python-based tests."""
    
    print("\n🐍 Running Python tests...")
    
    # Test Round 1A
    print("Testing Round 1A...")
    try:
        result = subprocess.run([sys.executable, "test_round1a.py"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Round 1A Python test passed")
            print(result.stdout)
        else:
            print(f"❌ Round 1A Python test failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ Round 1A test timed out")
    
    # Test Round 1B (only if models exist)
    if os.path.exists("models/all-MiniLM-L6-v2"):
        print("\nTesting Round 1B...")
        try:
            result = subprocess.run([sys.executable, "test_round1b.py"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ Round 1B Python test passed")
                print(result.stdout)
            else:
                print(f"❌ Round 1B Python test failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("❌ Round 1B test timed out")
    else:
        print("⚠️  Skipping Round 1B test - models not found")


def run_docker_tests():
    """Run Docker-based tests."""
    
    print("\n🐳 Running Docker tests...")
    
    # Prepare test directories
    os.makedirs("test_input", exist_ok=True)
    os.makedirs("test_output", exist_ok=True)
    os.makedirs("test_config", exist_ok=True)
    
    # Test Round 1A with Docker
    print("Testing Round 1A Docker container...")
    
    # Copy a sample PDF to test input
    sample_pdf = None
    for pdf in ["sample.pdf", "sample1.pdf", "South of France - Cities.pdf"]:
        if os.path.exists(pdf):
            sample_pdf = pdf
            break
    
    if sample_pdf:
        import shutil
        shutil.copy(sample_pdf, "test_input/")
        
        try:
            result = subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{os.getcwd()}/test_input:/app/input",
                "-v", f"{os.getcwd()}/test_output:/app/output",
                "round1a"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Round 1A Docker test passed")
                # Check if output file was created
                if os.path.exists("test_output/document_structure.json"):
                    print("✅ Output file created successfully")
                    with open("test_output/document_structure.json", 'r') as f:
                        output = json.load(f)
                        print(f"📄 Title: {output.get('title', 'N/A')}")
                        print(f"📋 Headings: {len(output.get('outline', []))}")
                else:
                    print("❌ Output file not created")
            else:
                print(f"❌ Round 1A Docker test failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("❌ Round 1A Docker test timed out")
        except FileNotFoundError:
            print("⚠️  Docker not available")
    
    # Test Round 1B with Docker (if models exist)
    if os.path.exists("models/all-MiniLM-L6-v2"):
        print("\nTesting Round 1B Docker container...")
        
        # Copy South of France PDFs
        south_pdfs = [f for f in os.listdir('.') if f.startswith('South of France') and f.endswith('.pdf')][:5]
        for pdf in south_pdfs:
            shutil.copy(pdf, "test_input/")
        
        # Create config file
        config = {
            "persona": "Travel Planner",
            "job_to_be_done": "Plan a 4-day trip for college friends"
        }
        with open("test_config/persona_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        try:
            result = subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{os.getcwd()}/test_input:/app/input",
                "-v", f"{os.getcwd()}/test_output:/app/output", 
                "-v", f"{os.getcwd()}/test_config:/app/config",
                "-v", f"{os.getcwd()}/models:/app/models",
                "round1b"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Round 1B Docker test passed")
                # Check if output file was created
                if os.path.exists("test_output/persona_analysis.json"):
                    print("✅ Output file created successfully")
                    with open("test_output/persona_analysis.json", 'r') as f:
                        output = json.load(f)
                        print(f"🎭 Persona: {output['metadata']['persona']}")
                        print(f"📊 Sections: {len(output.get('extracted_sections', []))}")
                else:
                    print("❌ Output file not created")
            else:
                print(f"❌ Round 1B Docker test failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("❌ Round 1B Docker test timed out")
        except FileNotFoundError:
            print("⚠️  Docker not available")


def main():
    """Main test runner."""
    
    print("🧪 Adobe Hackathon - Testing Both Rounds")
    print("="*60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Cannot proceed with tests. Please fix the issues above.")
        return
    
    # Run Python tests
    run_python_tests()
    
    # Test Docker builds
    docker_success = test_docker_builds()
    
    # Run Docker tests if builds succeeded
    if docker_success:
        run_docker_tests()
    
    print("\n" + "="*60)
    print("🏁 Testing completed!")
    print("\nGenerated test files:")
    test_files = [f for f in os.listdir('.') if f.startswith('test_output_')]
    for file in test_files:
        print(f"   📄 {file}")
    
    print("\nTo manually verify outputs:")
    print("   Round 1A: Check test_output_1a_*.json files")
    print("   Round 1B: Check test_output_1b_*.json files")


if __name__ == "__main__":
    main()