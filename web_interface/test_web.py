#!/usr/bin/env python3
"""
Test script for the Adobe Hackathon Web Interface
"""

import os
import sys
import requests
import json
import time

def test_web_interface():
    """Test the web interface endpoints."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Adobe Hackathon Web Interface")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print(f"   ❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server. Is it running?")
        print("   💡 Run 'python run_web.py' first")
        return False
    
    # Test 2: Check system status
    print("2. Testing system status...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Round 1A available: {status['round1a_available']}")
            print(f"   ✅ Round 1B available: {status['round1b_available']}")
            print(f"   ✅ Upload limit: {status['upload_limit_mb']}MB")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    # Test 3: Test Round 1A (if sample PDF exists)
    sample_pdf = os.path.join(os.path.dirname(__file__), '..', 'sample.pdf')
    if os.path.exists(sample_pdf):
        print("3. Testing Round 1A processing...")
        try:
            with open(sample_pdf, 'rb') as f:
                files = {'pdf_file': f}
                response = requests.post(f"{base_url}/api/round1a/process", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"   ✅ Processing successful")
                    print(f"   ⏱️  Time: {result['processing_time']:.3f}s")
                    print(f"   📄 Title: {result['title'][:50]}...")
                    print(f"   📋 Headings: {result['headings_count']}")
                    print(f"   🎯 Constraints met: {result['constraints_met']}")
                else:
                    print(f"   ❌ Processing failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Round 1A test error: {e}")
    else:
        print("3. Skipping Round 1A test (sample.pdf not found)")
    
    # Test 4: Test Round 1B (if multiple PDFs exist)
    south_france_pdfs = []
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    for filename in ['South of France - Cities.pdf', 'South of France - Cuisine.pdf', 'South of France - History.pdf']:
        pdf_path = os.path.join(parent_dir, filename)
        if os.path.exists(pdf_path):
            south_france_pdfs.append(pdf_path)
    
    if len(south_france_pdfs) >= 3:
        print("4. Testing Round 1B processing...")
        try:
            files = []
            for pdf_path in south_france_pdfs[:3]:
                files.append(('pdf_files', open(pdf_path, 'rb')))
            
            data = {
                'persona': 'Travel Planner',
                'job_to_be_done': 'Plan a trip for college friends'
            }
            
            response = requests.post(f"{base_url}/api/round1b/process", files=files, data=data)
            
            # Close files
            for _, file_obj in files:
                file_obj.close()
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"   ✅ Processing successful")
                    print(f"   ⏱️  Time: {result['processing_time']:.3f}s")
                    print(f"   📚 Documents: {result['documents_processed']}")
                    print(f"   📊 Sections: {result['extracted_sections']}")
                    print(f"   🎯 Constraints met: {result['constraints_met']}")
                else:
                    print(f"   ❌ Processing failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Round 1B test error: {e}")
    else:
        print("4. Skipping Round 1B test (insufficient South of France PDFs)")
    
    print("\n🎉 Web interface testing completed!")
    print("💡 Access the interface at: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    test_web_interface()