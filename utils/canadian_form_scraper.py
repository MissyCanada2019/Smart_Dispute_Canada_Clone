# utils/canadian_form_scraper.py

import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_federal_court_forms():
    url = "https://www.fct-cf.gc.ca/en/pages/forms"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    forms = []

    for link in soup.find_all("a", href=True):
        href = link['href']
        if href.endswith((".pdf", ".docx", ".doc")) and "form" in href.lower():
            form_url = href if href.startswith("http") else f"https://www.fct-cf.gc.ca{href}"
            title = link.text.strip()
            forms.append({
                "title": title,
                "url": form_url,
                "category": "federal",
                "court": "Federal Court of Canada"
            })

    os.makedirs("data", exist_ok=True)
    with open("data/federal_forms.json", "w", encoding="utf-8") as f:
        json.dump(forms, f, indent=2)

    print(f"Scraped {len(forms)} forms from Federal Court.")

if __name__ == "__main__":
    scrape_federal_court_forms()
