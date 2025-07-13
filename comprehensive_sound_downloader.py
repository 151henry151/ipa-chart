#!/usr/bin/env python3
import os
import requests
import re
from urllib.parse import urljoin, urlparse
import time

# Base URL for the UCLA IPA website
BASE_URL = "https://phonetics.ucla.edu/course/chapter1/"

# Headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_page_content(url):
    """Get the content of a webpage"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_sound_links(html_content):
    """Extract all sound file links from HTML content"""
    sound_pattern = r'href=["\']([^"\']*\.(?:aiff|wav))["\']'
    matches = re.findall(sound_pattern, html_content, re.IGNORECASE)
    return matches

def download_file(url, local_path):
    """Download a file from URL to local path"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def convert_aiff_to_wav(aiff_path):
    """Convert AIFF file to WAV using ffmpeg"""
    if not os.path.exists(aiff_path):
        return False
    
    wav_path = aiff_path.replace('.aiff', '.wav').replace('.AIFF', '.wav')
    if os.path.exists(wav_path):
        return True
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-i', aiff_path, wav_path, '-y'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Converted: {aiff_path} -> {wav_path}")
            return True
        else:
            print(f"Error converting {aiff_path}: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running ffmpeg: {e}")
        return False

def main():
    print("Starting comprehensive sound file download...")
    
    # Create ipaSOUNDS directory if it doesn't exist
    os.makedirs("ipaSOUNDS", exist_ok=True)
    
    # List of pages to crawl
    pages = [
        "consonants1.html",
        "consonants2.html", 
        "vowels.html",
        "clicks.html",
        "others.html"
    ]
    
    all_sound_files = set()
    
    # Crawl each page to find sound files
    for page in pages:
        url = urljoin(BASE_URL, page)
        print(f"\nCrawling {url}...")
        
        html_content = get_page_content(url)
        if html_content:
            sound_files = extract_sound_links(html_content)
            all_sound_files.update(sound_files)
            print(f"Found {len(sound_files)} sound files on {page}")
    
    print(f"\nTotal unique sound files found: {len(all_sound_files)}")
    
    # Download all sound files
    downloaded_count = 0
    for sound_file in sorted(all_sound_files):
        # Skip if already exists
        local_path = os.path.join("ipaSOUNDS", os.path.basename(sound_file))
        if os.path.exists(local_path):
            print(f"Already exists: {local_path}")
            continue
        
        # Download the file
        url = urljoin(BASE_URL, sound_file)
        if download_file(url, local_path):
            downloaded_count += 1
        
        # Add small delay to be respectful
        time.sleep(0.1)
    
    print(f"\nDownloaded {downloaded_count} new files")
    
    # Convert all AIFF files to WAV
    print("\nConverting AIFF files to WAV...")
    converted_count = 0
    for filename in os.listdir("ipaSOUNDS"):
        if filename.lower().endswith(('.aiff', '.aif')):
            aiff_path = os.path.join("ipaSOUNDS", filename)
            if convert_aiff_to_wav(aiff_path):
                converted_count += 1
    
    print(f"Converted {converted_count} AIFF files to WAV")
    
    # Generate missing vowel files list
    print("\nChecking for missing vowel files...")
    missing_vowels = []
    for i in range(28):  # Vow-00a to Vow-27a
        for suffix in ['a']:  # Most vowel files are 'a' suffix
            filename = f"Vow-{i:02d}{suffix}.wav"
            if not os.path.exists(os.path.join("ipaSOUNDS", filename)):
                missing_vowels.append(filename)
    
    print(f"Missing vowel files: {len(missing_vowels)}")
    for vowel in missing_vowels[:10]:  # Show first 10
        print(f"  {vowel}")
    if len(missing_vowels) > 10:
        print(f"  ... and {len(missing_vowels) - 10} more")
    
    # Try to download missing vowel files directly
    print("\nAttempting to download missing vowel files...")
    for vowel in missing_vowels:
        url = urljoin(BASE_URL, f"ipaSOUNDS/{vowel}")
        local_path = os.path.join("ipaSOUNDS", vowel)
        if download_file(url, local_path):
            print(f"Successfully downloaded: {vowel}")
        else:
            # Try AIFF version
            aiff_filename = vowel.replace('.wav', '.aiff')
            url = urljoin(BASE_URL, f"ipaSOUNDS/{aiff_filename}")
            local_path = os.path.join("ipaSOUNDS", aiff_filename)
            if download_file(url, local_path):
                convert_aiff_to_wav(local_path)
                print(f"Downloaded and converted: {aiff_filename}")
        
        time.sleep(0.1)  # Be respectful
    
    print("\nComprehensive sound download complete!")

if __name__ == "__main__":
    main() 