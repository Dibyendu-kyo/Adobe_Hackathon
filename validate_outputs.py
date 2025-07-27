#!/usr/bin/env python3
"""
Output validation script for both Round 1A and Round 1B
"""

import os
import json
import sys
from datetime import datetime


def validate_round1a_output(filepath):
    """Validate Round 1A output format."""
    
    print(f"🔍 Validating Round 1A output: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        return False
    
    # Check structure
    checks = []
    
    # Required keys
    checks.append(("Has 'title' key", 'title' in data))
    checks.append(("Has 'outline' key", 'outline' in data))
    
    if 'title' in data:
        checks.append(("Title is string", isinstance(data['title'], str)))
        checks.append(("Title not empty", len(data['title'].strip()) > 0))
    
    if 'outline' in data:
        outline = data['outline']
        checks.append(("Outline is list", isinstance(outline, list)))
        
        if isinstance(outline, list):
            checks.append(("Has headings", len(outline) > 0))
            
            for i, heading in enumerate(outline):
                if isinstance(heading, dict):
                    checks.append((f"Heading {i+1} has 'level'", 'level' in heading))
                    checks.append((f"Heading {i+1} has 'text'", 'text' in heading))
                    checks.append((f"Heading {i+1} has 'page'", 'page' in heading))
                    
                    if 'level' in heading:
                        checks.append((f"Heading {i+1} level valid", heading['level'] in ['H1', 'H2', 'H3']))
                    
                    if 'page' in heading:
                        checks.append((f"Heading {i+1} page valid", isinstance(heading['page'], int) and heading['page'] > 0))
    
    # Print results
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    print(f"\n📊 Validation result: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ Round 1A output format is VALID")
        
        # Show summary
        print(f"📄 Title: {data.get('title', 'N/A')}")
        print(f"📋 Total headings: {len(data.get('outline', []))}")
        
        # Show heading distribution
        if 'outline' in data:
            levels = {}
            for heading in data['outline']:
                level = heading.get('level', 'Unknown')
                levels[level] = levels.get(level, 0) + 1
            
            print("📊 Heading distribution:")
            for level in ['H1', 'H2', 'H3']:
                if level in levels:
                    print(f"   {level}: {levels[level]}")
        
        return True
    else:
        print("❌ Round 1A output format is INVALID")
        return False


def validate_round1b_output(filepath):
    """Validate Round 1B output format."""
    
    print(f"🔍 Validating Round 1B output: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        return False
    
    # Check structure
    checks = []
    
    # Top-level keys
    required_keys = ['metadata', 'extracted_sections', 'subsection_analysis']
    for key in required_keys:
        checks.append((f"Has '{key}' key", key in data))
    
    # Check metadata
    if 'metadata' in data:
        metadata = data['metadata']
        metadata_keys = ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp']
        
        for key in metadata_keys:
            checks.append((f"Metadata has '{key}'", key in metadata))
        
        if 'input_documents' in metadata:
            checks.append(("Input documents is list", isinstance(metadata['input_documents'], list)))
            checks.append(("Has input documents", len(metadata['input_documents']) > 0))
        
        if 'processing_timestamp' in metadata:
            # Try to parse timestamp
            try:
                datetime.fromisoformat(metadata['processing_timestamp'].replace('Z', '+00:00'))
                checks.append(("Timestamp format valid", True))
            except:
                checks.append(("Timestamp format valid", False))
    
    # Check extracted_sections
    if 'extracted_sections' in data:
        sections = data['extracted_sections']
        checks.append(("Extracted sections is list", isinstance(sections, list)))
        checks.append(("Has extracted sections", len(sections) > 0))
        
        if isinstance(sections, list):
            section_keys = ['document', 'section_title', 'importance_rank', 'page_number']
            
            for i, section in enumerate(sections):
                if isinstance(section, dict):
                    for key in section_keys:
                        checks.append((f"Section {i+1} has '{key}'", key in section))
                    
                    if 'importance_rank' in section:
                        checks.append((f"Section {i+1} rank valid", isinstance(section['importance_rank'], int) and section['importance_rank'] > 0))
    
    # Check subsection_analysis
    if 'subsection_analysis' in data:
        analysis = data['subsection_analysis']
        checks.append(("Subsection analysis is list", isinstance(analysis, list)))
        checks.append(("Has subsection analysis", len(analysis) > 0))
        
        if isinstance(analysis, list):
            analysis_keys = ['document', 'refined_text', 'page_number']
            
            for i, item in enumerate(analysis):
                if isinstance(item, dict):
                    for key in analysis_keys:
                        checks.append((f"Analysis {i+1} has '{key}'", key in item))
    
    # Print results
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    print(f"\n📊 Validation result: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ Round 1B output format is VALID")
        
        # Show summary
        if 'metadata' in data:
            metadata = data['metadata']
            print(f"🎭 Persona: {metadata.get('persona', 'N/A')}")
            print(f"🎯 Job: {metadata.get('job_to_be_done', 'N/A')}")
            print(f"📚 Documents: {len(metadata.get('input_documents', []))}")
        
        print(f"📊 Extracted sections: {len(data.get('extracted_sections', []))}")
        print(f"📝 Subsection analysis: {len(data.get('subsection_analysis', []))}")
        
        # Show top sections
        sections = data.get('extracted_sections', [])
        if sections:
            print("🏆 Top sections:")
            for section in sections[:3]:
                print(f"   {section.get('importance_rank', '?')}. {section.get('section_title', 'N/A')} ({section.get('document', 'N/A')})")
        
        return True
    else:
        print("❌ Round 1B output format is INVALID")
        return False


def main():
    """Main validation function."""
    
    print("🔍 Output Validation Tool")
    print("="*50)
    
    # Find output files
    round1a_files = [f for f in os.listdir('.') if f.startswith('test_output_1a_') and f.endswith('.json')]
    round1b_files = [f for f in os.listdir('.') if f.startswith('test_output_1b_') and f.endswith('.json')]
    
    # Also check standard output locations
    if os.path.exists('test_output/document_structure.json'):
        round1a_files.append('test_output/document_structure.json')
    
    if os.path.exists('test_output/persona_analysis.json'):
        round1b_files.append('test_output/persona_analysis.json')
    
    # Validate Round 1A outputs
    if round1a_files:
        print("\n📄 ROUND 1A OUTPUTS:")
        print("-" * 30)
        for file in round1a_files:
            validate_round1a_output(file)
            print()
    else:
        print("\n⚠️  No Round 1A output files found")
    
    # Validate Round 1B outputs
    if round1b_files:
        print("\n📊 ROUND 1B OUTPUTS:")
        print("-" * 30)
        for file in round1b_files:
            validate_round1b_output(file)
            print()
    else:
        print("\n⚠️  No Round 1B output files found")
    
    # Summary
    total_files = len(round1a_files) + len(round1b_files)
    if total_files == 0:
        print("❌ No output files found. Run tests first:")
        print("   python run_tests.py")
        print("   python test_round1a.py")
        print("   python test_round1b.py")
    else:
        print(f"✅ Validated {total_files} output files")


if __name__ == "__main__":
    main()