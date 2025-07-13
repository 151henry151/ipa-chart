#!/usr/bin/env python3

import re
import os
from pathlib import Path

def extract_audio_files_from_html():
    """Extract all audio file references from HTML files"""
    audio_files = set()
    
    # Search in all HTML files
    for html_file in Path('.').glob('*.html'):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all javascript:playAudio references
        matches = re.findall(r"javascript:playAudio\('ipaSOUNDS/([^']+\.wav)'\)", content)
        audio_files.update(matches)
    
    return audio_files

def check_missing_files():
    """Check which referenced files don't exist"""
    referenced_files = extract_audio_files_from_html()
    existing_files = set()
    
    # Get list of existing .wav files
    ipa_sounds_dir = Path('ipaSOUNDS')
    if ipa_sounds_dir.exists():
        for file in ipa_sounds_dir.glob('*.wav'):
            existing_files.add(file.name)
    
    missing_files = referenced_files - existing_files
    existing_referenced = referenced_files & existing_files
    
    print(f"Total referenced files: {len(referenced_files)}")
    print(f"Existing files: {len(existing_files)}")
    print(f"Missing files: {len(missing_files)}")
    print(f"Files that exist and are referenced: {len(existing_referenced)}")
    
    print("\nMissing files:")
    for file in sorted(missing_files):
        print(f"  {file}")
    
    print("\nFiles that exist and are referenced:")
    for file in sorted(existing_referenced):
        print(f"  {file}")
    
    return missing_files, existing_referenced

if __name__ == "__main__":
    missing, existing = check_missing_files() 