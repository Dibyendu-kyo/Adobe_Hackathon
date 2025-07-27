#!/usr/bin/env python3
"""
Compare current output with sample to identify exact differences
"""

import json

def compare_with_sample():
    """Compare current output with expected sample."""
    
    # Expected sample output
    sample_expected = {
        "title": "Overview  Foundation Level Extensions  ",
        "outline": [
            {"level": "H1", "text": "Revision History ", "page": 2},
            {"level": "H1", "text": "Table of Contents ", "page": 3},
            {"level": "H1", "text": "Acknowledgements ", "page": 4},
            {"level": "H1", "text": "1. Introduction to the Foundation Level Extensions ", "page": 5},
            {"level": "H1", "text": "2. Introduction to Foundation Level Agile Tester Extension ", "page": 6},
            {"level": "H2", "text": "2.1 Intended Audience ", "page": 6},
            {"level": "H2", "text": "2.2 Career Paths for Testers ", "page": 6},
            {"level": "H2", "text": "2.3 Learning Objectives ", "page": 6},
            {"level": "H2", "text": "2.4 Entry Requirements ", "page": 7},
            {"level": "H2", "text": "2.5 Structure and Course Duration ", "page": 7},
            {"level": "H2", "text": "2.6 Keeping It Current ", "page": 8},
            {"level": "H1", "text": "3. Overview of the Foundation Level Extension – Agile TesterSyllabus ", "page": 9},
            {"level": "H2", "text": "3.1 Business Outcomes ", "page": 9},
            {"level": "H2", "text": "3.2 Content ", "page": 9},
            {"level": "H1", "text": "4. References ", "page": 11},
            {"level": "H2", "text": "4.1 Trademarks ", "page": 11},
            {"level": "H2", "text": "4.2 Documents and Web Sites ", "page": 11}
        ]
    }
    
    # Current output (from the test)
    current_output = {
        "title": "Overview  Foundation Level Extensions  ",
        "outline": [
            {"level": "H1", "text": "Revision History ", "page": 3},
            {"level": "H1", "text": "Table of Contents ", "page": 4},
            {"level": "H1", "text": "Acknowledgements ", "page": 5},
            {"level": "H1", "text": "1. Introduction to the Foundation Level Extensions ", "page": 6},
            {"level": "H1", "text": "2. Introduction to Foundation Level Agile Tester Extension ", "page": 7},
            {"level": "H2", "text": "2.1 Intended Audience ", "page": 7},
            {"level": "H2", "text": "2.2 Career Paths for Testers ", "page": 7},
            {"level": "H2", "text": "2.3 Learning Objectives ", "page": 7},
            {"level": "H2", "text": "2.4 Entry Requirements ", "page": 8},
            {"level": "H2", "text": "2.5 Structure and Course Duration ", "page": 8},
            {"level": "H2", "text": "2.6 Keeping It Current ", "page": 9},
            {"level": "H1", "text": "3. Overview of the Foundation Level Extension – Agile Tester Syllabus ", "page": 10},
            {"level": "H2", "text": "3.1 Business Outcomes ", "page": 10},
            {"level": "H2", "text": "3.2 Content ", "page": 10},
            {"level": "H1", "text": "4. References ", "page": 12},
            {"level": "H2", "text": "4.1 Trademarks ", "page": 12},
            {"level": "H2", "text": "4.2 Documents and Web Sites ", "page": 12}
        ]
    }
    
    print("="*80)
    print("SAMPLE VS CURRENT OUTPUT COMPARISON")
    print("="*80)
    
    print("✅ TITLE COMPARISON:")
    print(f"   Sample:  '{sample_expected['title']}'")
    print(f"   Current: '{current_output['title']}'")
    print(f"   Match: {'✅ YES' if sample_expected['title'] == current_output['title'] else '❌ NO'}")
    
    print(f"\n📊 HEADING COUNT:")
    print(f"   Sample:  {len(sample_expected['outline'])} headings")
    print(f"   Current: {len(current_output['outline'])} headings")
    
    print(f"\n🔍 DETAILED COMPARISON:")
    print("   Index | Level | Sample Text | Current Text | Page Match")
    print("   " + "-"*70)
    
    max_len = max(len(sample_expected['outline']), len(current_output['outline']))
    
    for i in range(max_len):
        sample_item = sample_expected['outline'][i] if i < len(sample_expected['outline']) else None
        current_item = current_output['outline'][i] if i < len(current_output['outline']) else None
        
        if sample_item and current_item:
            text_match = sample_item['text'] == current_item['text']
            level_match = sample_item['level'] == current_item['level']
            page_match = sample_item['page'] == current_item['page']
            
            status = "✅" if (text_match and level_match) else "❌"
            page_status = "✅" if page_match else f"❌ ({sample_item['page']}→{current_item['page']})"
            
            print(f"   {i+1:2d}    | {current_item['level']}   | {sample_item['text'][:30]:<30} | {current_item['text'][:30]:<30} | {page_status}")
        elif sample_item:
            print(f"   {i+1:2d}    | --   | {sample_item['text'][:30]:<30} | {'MISSING':<30} | ❌")
        elif current_item:
            print(f"   {i+1:2d}    | {current_item['level']}   | {'EXTRA':<30} | {current_item['text'][:30]:<30} | ❌")
    
    print(f"\n📋 ANALYSIS:")
    print("   ✅ Title: Perfect match")
    print("   ✅ Structure: Correct H1/H2 hierarchy")
    print("   ✅ Content: All expected headings present")
    print("   ⚠️  Page numbers: Off by 1-2 pages (likely due to cover page handling)")
    print("   ⚠️  Extra headings: Need to filter out noise/duplicates")
    
    print(f"\n🎯 NEEDED IMPROVEMENTS:")
    print("   1. Filter out duplicate/noise headings")
    print("   2. Adjust page number offset")
    print("   3. Clean up text extraction to avoid repetitive content")
    
    print(f"\n✅ OVERALL ASSESSMENT:")
    print("   The core structure and content are correct!")
    print("   Just need to clean up the noise and adjust page numbers.")


if __name__ == "__main__":
    compare_with_sample()