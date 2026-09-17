import time
import json
import csv
import logging
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

def fetch_page(url, retries=3, delay=2):
    """Fetch URL with retry logic and custom headers."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.text
            logging.warning(f"Status code {response.status_code} received for {url}. Retrying...")
        except requests.RequestException as e:
            logging.warning(f"Request failed: {e}. Attempt {attempt + 1} of {retries}")
        time.sleep(delay)
    return None

def parse_books(html_content):
    """Extract book details from raw HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    books_data = []
    
    articles = soup.find_all("article", class_="product_pod")
    for article in articles:
        # Title
        title = article.h3.a["title"]
        
        # Price (Strip currency symbol '£')
        price_text = article.find("p", class_="price_color").text
        price = float(price_text.replace("£", "").replace("Â", "").strip())
        
        # Availability
        availability = article.find("p", class_="instock availability").text.strip()
        in_stock = "In stock" in availability
        
        # Rating
        rating_class = article.find("p", class_="star-rating")["class"][1]
        rating = RATING_MAP.get(rating_class, 0)
        
        books_data.append({
            "title": title,
            "price_gbp": price,
            "rating": rating,
            "in_stock": in_stock
        })
        
    return books_data

def generate_summary(books):
    """Compute summary statistics."""
    if not books:
        return {}
    
    prices = [b["price_gbp"] for b in books]
    ratings = [b["rating"] for b in books]
    
    summary = {
        "total_books_scraped": len(books),
        "average_price_gbp": round(sum(prices) / len(prices), 2),
        "max_price_gbp": max(prices),
        "min_price_gbp": min(prices),
        "average_rating": round(sum(ratings) / len(ratings), 2),
        "in_stock_count": sum(1 for b in books if b["in_stock"])
    }
    return summary

def main():
    all_books = []
    max_pages = 3  # Scrape first 3 pages
    
    logging.info("Starting Web Scraping Pipeline...")
    
    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page)
        logging.info(f"Scraping page {page}: {url}")
        
        html = fetch_page(url)
        if html:
            books = parse_books(html)
            all_books.extend(books)
            logging.info(f"Extracted {len(books)} books from page {page}")
        
        # Rate limiting: wait 1 second between requests
        time.sleep(1)
        
    # Save to CSV
    csv_filename = "output.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price_gbp", "rating", "in_stock"])
        writer.writeheader()
        writer.writerows(all_books)
    logging.info(f"Exported dataset to {csv_filename}")
    
    # Generate & Save Summary Report
    summary = generate_summary(all_books)
    report_filename = "summary_report.json"
    with open(report_filename, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logging.info(f"Exported summary analytics to {report_filename}")

if __name__ == "__main__":
    main()