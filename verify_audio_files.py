#!/usr/bin/env python3
import os
import re
from pathlib import Path

def extract_audio_references(html_content):
    """Extract all audio file references from HTML content"""
    # Look for javascript:playAudio references
    js_pattern = r"playAudio\('([^']*\.(?:aiff|wav))'\)"
    js_matches = re.findall(js_pattern, html_content, re.IGNORECASE)
    
    # Look for direct href references
    href_pattern = r'href=["\']([^"\']*\.(?:aiff|wav))["\']'
    href_matches = re.findall(href_pattern, html_content, re.IGNORECASE)
    
    # Combine and normalize paths
    all_references = set()
    for ref in js_matches + href_matches:
        # Normalize the path to always start with ipaSOUNDS/
        if ref.startswith('ipaSOUNDS/'):
            normalized = ref
        else:
            normalized = f"ipaSOUNDS/{ref}"
        all_references.add(normalized)
    
    return sorted(all_references)

def check_file_exists(file_path):
    """Check if a file exists, with case-insensitive fallback"""
    if os.path.exists(file_path):
        return True
    
    # Try case-insensitive matching
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    if os.path.exists(directory):
        for existing_file in os.listdir(directory):
            if existing_file.lower() == filename.lower():
                return True
    
    return False

def main():
    print("Verifying audio file references...")
    print("=" * 50)
    
    # HTML files to check
    html_files = [
        'consonants1.html',
        'consonants2.html', 
        'vowels.html',
        'clicks.html',
        'others.html',
        'ucla_ipa.html'
    ]
    
    all_references = set()
    missing_files = []
    existing_files = []
    
    # Check each HTML file
    for html_file in html_files:
        if not os.path.exists(html_file):
            print(f"Warning: {html_file} not found")
            continue
            
        print(f"\nChecking {html_file}...")
        
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        references = extract_audio_references(content)
        print(f"  Found {len(references)} audio references")
        
        for ref in references:
            all_references.add(ref)
            if check_file_exists(ref):
                existing_files.append(ref)
                print(f"    ✅ {ref}")
            else:
                missing_files.append(ref)
                print(f"    ❌ {ref} - MISSING")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total unique audio references: {len(all_references)}")
    print(f"Existing files: {len(existing_files)}")
    print(f"Missing files: {len(missing_files)}")
    
    if missing_files:
        print(f"\nMISSING FILES ({len(missing_files)}):")
        for file in sorted(missing_files):
            print(f"  - {file}")
    else:
        print("\n✅ All audio files exist!")
    
    # Check for unused files
    print(f"\nChecking for unused files in ipaSOUNDS/...")
    if os.path.exists('ipaSOUNDS'):
        all_audio_files = []
        for file in os.listdir('ipaSOUNDS'):
            if file.lower().endswith(('.wav', '.aiff', '.aif')):
                all_audio_files.append(f"ipaSOUNDS/{file}")
        
        unused_files = []
        for file in all_audio_files:
            if file not in all_references:
                unused_files.append(file)
        
        if unused_files:
            print(f"Unused audio files ({len(unused_files)}):")
            for file in sorted(unused_files)[:10]:  # Show first 10
                print(f"  - {file}")
            if len(unused_files) > 10:
                print(f"  ... and {len(unused_files) - 10} more")
        else:
            print("✅ All audio files are referenced in HTML pages")

if __name__ == "__main__":
    main() 