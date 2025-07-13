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
    # Look for links to .aiff files
    aiff_pattern = r'href=["\']([^"\']*\.aiff)["\']'
    aiff_links = re.findall(aiff_pattern, html_content, re.IGNORECASE)
    
    # Look for links to .wav files
    wav_pattern = r'href=["\']([^"\']*\.wav)["\']'
    wav_links = re.findall(wav_pattern, html_content, re.IGNORECASE)
    
    return aiff_links + wav_links

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
    """Convert .aiff file to .wav using ffmpeg"""
    wav_path = aiff_path.replace('.aiff', '.wav')
    if not os.path.exists(wav_path):
        try:
            import subprocess
            cmd = ['ffmpeg', '-i', aiff_path, wav_path, '-y']
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Converted: {aiff_path} -> {wav_path}")
            return True
        except Exception as e:
            print(f"Error converting {aiff_path}: {e}")
            return False
    return True

def main():
    print("Crawling UCLA IPA website for sound files...")
    
    # Get the main page content
    main_content = get_page_content(BASE_URL)
    if not main_content:
        print("Failed to get main page content")
        return
    
    # Extract sound file links
    sound_links = extract_sound_links(main_content)
    print(f"Found {len(sound_links)} sound file links")
    
    # Download each sound file
    downloaded_count = 0
    for link in sound_links:
        # Convert relative URLs to absolute URLs
        if link.startswith('http'):
            full_url = link
        else:
            full_url = urljoin(BASE_URL, link)
        
        # Determine local path
        filename = os.path.basename(urlparse(full_url).path)
        local_path = os.path.join('ipaSOUNDS', filename)
        
        # Download if file doesn't exist
        if not os.path.exists(local_path):
            if download_file(full_url, local_path):
                downloaded_count += 1
                time.sleep(0.5)  # Be respectful to the server
        else:
            print(f"File already exists: {local_path}")
    
    print(f"Downloaded {downloaded_count} new files")
    
    # Convert all .aiff files to .wav
    print("Converting .aiff files to .wav...")
    for filename in os.listdir('ipaSOUNDS'):
        if filename.endswith('.aiff'):
            aiff_path = os.path.join('ipaSOUNDS', filename)
            convert_aiff_to_wav(aiff_path)
    
    print("Done!")

if __name__ == "__main__":
    main() 