#!/usr/bin/env python3
import os
import requests
import re
from urllib.parse import urljoin, urlparse
import time

# URLs to download
CARDINAL_URL = "https://phonetics.ucla.edu/course/chapter9/cardinal/cardinal.html"
WELLS_URL = "https://phonetics.ucla.edu/course/chapter1/wells/wells.html"

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

def extract_audio_links(html_content, base_url):
    """Extract all audio file links from HTML content"""
    audio_pattern = r'href=[\'"]([^\'"]*\.(?:wav|aiff))[\'"]'
    matches = re.findall(audio_pattern, html_content, re.IGNORECASE)
    
    audio_links = []
    for match in matches:
        if match.startswith('http'):
            audio_links.append(match)
        else:
            audio_links.append(urljoin(base_url, match))
    
    return audio_links

def extract_image_links(html_content, base_url):
    """Extract all image file links from HTML content"""
    img_pattern = r'<img[^>]+src=[\'"]([^\'"]+)[\'"]'
    matches = re.findall(img_pattern, html_content, re.IGNORECASE)
    
    img_links = []
    for match in matches:
        if match.startswith('http'):
            img_links.append(match)
        else:
            img_links.append(urljoin(base_url, match))
    
    return img_links

def download_file(url, local_path):
    """Download a file from URL to local path"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    print("Downloading Cardinal Vowels page...")
    cardinal_content = get_page_content(CARDINAL_URL)
    if cardinal_content:
        # Save the HTML
        with open('cardinal.html', 'w', encoding='utf-8') as f:
            f.write(cardinal_content)
        print("Saved cardinal.html")
        
        # Extract and download audio files
        cardinal_base = "https://phonetics.ucla.edu/course/chapter9/cardinal/"
        audio_links = extract_audio_links(cardinal_content, cardinal_base)
        for audio_url in audio_links:
            filename = os.path.basename(urlparse(audio_url).path)
            local_path = f"ipaSOUNDS/{filename}"
            download_file(audio_url, local_path)
        
        # Extract and download images
        img_links = extract_image_links(cardinal_content, cardinal_base)
        for img_url in img_links:
            filename = os.path.basename(urlparse(img_url).path)
            local_path = filename
            download_file(img_url, local_path)
    
    print("\nDownloading Wells page...")
    wells_content = get_page_content(WELLS_URL)
    if wells_content:
        # Save the HTML
        with open('wells.html', 'w', encoding='utf-8') as f:
            f.write(wells_content)
        print("Saved wells.html")
        
        # Extract and download audio files
        wells_base = "https://phonetics.ucla.edu/course/chapter1/wells/"
        audio_links = extract_audio_links(wells_content, wells_base)
        for audio_url in audio_links:
            filename = os.path.basename(urlparse(audio_url).path)
            local_path = f"ipaSOUNDS/{filename}"
            download_file(audio_url, local_path)
        
        # Extract and download images
        img_links = extract_image_links(wells_content, wells_base)
        for img_url in img_links:
            filename = os.path.basename(urlparse(img_url).path)
            local_path = filename
            download_file(img_url, local_path)

if __name__ == "__main__":
    main() 