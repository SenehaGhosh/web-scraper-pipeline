# Automated Web Scraping & Data Extraction Pipeline

An automated ETL web scraping pipeline using Python, Requests, and BeautifulSoup to extract structured data from online listings.

## Features
* **Polite Scraping**: Custom User-Agent headers, rate limiting (delays), and retry logic.
* **Data Parsing**: Extracts title, price, rating, and stock status into structured data.
* **Storage & Analytics**: Exports datasets to CSV and produces summary analytics in JSON format.

## Setup & Execution

1. Install dependencies:
   ```bash
   pip install -r requirements.txt