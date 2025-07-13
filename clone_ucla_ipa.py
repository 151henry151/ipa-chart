"""
clone_ucla_ipa.py

Recursively downloads the UCLA IPA chart experience (main chart, all second-level pages, all referenced images and sound files), rewrites links to local, and saves in ipa_clone/.

Usage:
  python clone_ucla_ipa.py

Requirements:
  pip install requests beautifulsoup4

After running, serve with:
  cd ipa_clone && python -m http.server 8000
"""
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://phonetics.ucla.edu/course/chapter1/chapter1.html"
ROOT = "https://phonetics.ucla.edu/course/chapter1/"
CLONE_DIR = "ipa_clone"
SOUNDS_DIR = os.path.join(CLONE_DIR, "ipaSOUNDS")
IMAGES_DIR = os.path.join(CLONE_DIR, "images")

os.makedirs(CLONE_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

session = requests.Session()
visited = set()

def download_file(url, dest):
    if os.path.exists(dest):
        return
    print(f"Downloading {url} -> {dest}")
    r = session.get(url, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

def localize_links(soup, page_url):
    # Images
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src: continue
        img_url = urljoin(page_url, src)
        img_name = os.path.basename(urlparse(img_url).path)
        local_path = f"images/{img_name}"
        download_file(img_url, os.path.join(IMAGES_DIR, img_name))
        img["src"] = local_path
    # Sound files in <area> and <a>
    for tag in soup.find_all(["area", "a"]):
        href = tag.get("href")
        if not href: continue
        if href.endswith(".aiff"):
            sound_url = urljoin(page_url, href)
            sound_name = os.path.basename(urlparse(sound_url).path)
            local_path = f"ipaSOUNDS/{sound_name}"
            download_file(sound_url, os.path.join(SOUNDS_DIR, sound_name))
            tag["href"] = local_path
        elif href.endswith(".html") or href.endswith(".htm"):
            # Will be localized recursively
            tag["href"] = os.path.basename(href)
    return soup

# Only recurse into these chart-relevant pages
CHART_PAGES = {
    "consonants1.html",
    "consonants2.html",
    "vowels.html",
    "clicks.html",
    "others.html",
    "index.html"
}

def clone_page(url, local_name):
    if url in visited:
        return
    visited.add(url)
    print(f"Cloning {url} -> {local_name}")
    try:
        r = session.get(url)
        r.raise_for_status()
    except requests.HTTPError as e:
        print(f"Skipping missing page: {url} ({e})")
        return
    soup = BeautifulSoup(r.text, "html.parser")
    soup = localize_links(soup, url)
    # Only recurse into chart-relevant HTML pages
    for tag in soup.find_all(["area", "a"]):
        href = tag.get("href")
        if href and (href.endswith(".html") or href.endswith(".htm")):
            if os.path.basename(href) in CHART_PAGES:
                next_url = urljoin(url, href)
                next_local = os.path.basename(href)
                clone_page(next_url, next_local)
    # Save localized HTML
    with open(os.path.join(CLONE_DIR, local_name), "w", encoding="utf-8") as f:
        f.write(str(soup))

if __name__ == "__main__":
    print("Starting UCLA IPA chart cloning...")
    clone_page(BASE_URL, "index.html")
    print("Done! All files are in ipa_clone/. Serve with: cd ipa_clone && python -m http.server 8000") 