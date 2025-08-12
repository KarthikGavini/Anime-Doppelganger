import requests
from bs4 import BeautifulSoup
import os
import time

# --- 1. SETUP ---
# ✅ CRAWL CONTROL: Set the page range you want to scrape.
START_PAGE = 129
END_PAGE = 200  # This will scrape pages 1 through 5 (250 characters total)

BASE_URL = "https://myanimelist.net/character.php?limit="
IMAGE_DIR = "mal_character_images"

# Create a directory to save images if it doesn't exist
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# --- 2. LOOP THROUGH PAGES AND SCRAPE DATA ---
# ✅ UPDATED LOOP: Iterates from your defined start page to the end page.
for page_num in range(START_PAGE, END_PAGE + 1):
    # Convert page number to the URL's 'limit' parameter
    # Page 1 -> limit=0, Page 2 -> limit=50, etc.
    page_limit = (page_num - 1) * 50
    current_url = f"{BASE_URL}{page_limit}"
    
    print(f"Scraping Page {page_num}: {current_url}")

    try:
        headers = {'User-Agent': 'MyAnimeList Scraper Bot/1.0'}
        response = requests.get(current_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        character_rows = soup.find_all('tr', class_='ranking-list')

        if not character_rows:
            print("  No more characters found on this page. Stopping.")
            break

        for row in character_rows:
            link_tag = row.find('a', class_='fl-l')
            if not link_tag:
                continue

            img_tag = link_tag.find('img')
            if not img_tag:
                continue

            character_name = img_tag.get('alt', '').strip()
            image_url = img_tag.get('data-src') or img_tag.get('src')

            if character_name and image_url:
                image_url = image_url.replace('/r/50x78', '').replace('/r/42x62', '')
                safe_filename = "".join([c for c in character_name if c.isalnum() or c.isspace()]).strip()
                
                if safe_filename:
                    try:
                        img_response = requests.get(image_url, headers=headers)
                        if img_response.status_code == 200:
                            file_path = os.path.join(IMAGE_DIR, f"{safe_filename}.jpg")
                            with open(file_path, 'wb') as f:
                                f.write(img_response.content)
                            print(f"  Saved: {safe_filename}.jpg")
                    except requests.exceptions.RequestException as img_e:
                        print(f"  Could not download image for {safe_filename}. Reason: {img_e}")

        print("  Page scraped. Waiting 2 seconds before next page...")
        time.sleep(2)

    except requests.exceptions.RequestException as e:
        print(f"  Failed to fetch page {current_url}. Error: {e}")
        continue

print("\nScraping complete!")