```python
"""
track_cve_2025.py

This script queries an API to find articles related to known exploited vulnerabilities (CVEs) in 2025.
It summarizes the findings and updates the README.md with the results.

Usage:
1. Replace 'YOUR_API_KEY' and 'YOUR_CSE_ID' with your Google Custom Search API key and Custom Search Engine ID.
2. Run the script using Python 3: python scripts/track_cve_2025.py
"""

import requests
import json
import csv
import os
from datetime import datetime

API_KEY = 'YOUR_API_KEY'  # Replace with your Google Custom Search API key
CSE_ID = 'YOUR_CSE_ID'  # Replace with your Custom Search Engine ID
OUTPUT_FILE = 'cve_2025_articles.json'
README_FILE = '../README.md'

def fetch_articles(keywords):
    """Fetch articles from Google Custom Search API."""
    articles = []
    for keyword in keywords:
        url = f"https://www.googleapis.com/customsearch/v1?q={keyword}&key={API_KEY}&cx={CSE_ID}&dateRestrict=y2025"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                articles.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'source': item.get('source'),
                    'publish_date': item.get('published'),
                    'snippet': item.get('snippet')
                })
    return articles

def summarize_articles(articles):
    """Summarize articles per CVE."""
    summary = {}
    for article in articles:
        # Extract CVE from title or snippet
        cve = extract_cve(article['title']) or extract_cve(article['snippet'])
        if cve:
            if cve not in summary:
                summary[cve] = {
                    'article_count': 0,
                    'first_observed_date': None,
                    'victims': set()
                }
            summary[cve]['article_count'] += 1
            # Update first observed date if applicable
            if article['publish_date']:
                publish_date = datetime.strptime(article['publish_date'], '%Y-%m-%d')
                if summary[cve]['first_observed_date'] is None or publish_date < summary[cve]['first_observed_date']:
                    summary[cve]['first_observed_date'] = publish_date
            # Add victims if mentioned
            if 'victim' in article['snippet'].lower():
                summary[cve]['victims'].add(article['snippet'])  # Simplified for demo
    return summary

def extract_cve(text):
    """Extract CVE identifier from text."""
    import re
    match = re.search(r'CVE-\d{4}-\d+', text)
    return match.group(0) if match else None

def update_readme(summary):
    """Update README.md with CVE summary."""
    with open(README_FILE, 'a') as f:
        f.write("\n## CVE Summary for 2025\n")
        f.write("| CVE ID | Article Count | First Observed Date | Victims Mentioned |\n")
        f.write("|--------|---------------|---------------------|-------------------|\n")
        for cve, data in summary.items():
            victims = ', '.join(data['victims'])
            first_date = data['first_observed_date'].strftime('%Y-%m-%d') if data['first_observed_date'] else 'N/A'
            f.write(f"| {cve} | {data['article_count']} | {first_date} | {victims} |\n")

def main():
    keywords = ["CVE-2025", "zero-day", "0day", "exploited in the wild", "known exploited", "victims", "affected"]
    articles = fetch_articles(keywords)
    summary = summarize_articles(articles)
    
    # Save articles to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(articles, f, indent=4)
    
    # Update README
    update_readme(summary)

if __name__ == "__main__":
    main()
```