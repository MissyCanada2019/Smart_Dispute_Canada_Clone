import requests
from bs4 import BeautifulSoup
import json
import os

BASE_URL = "https://stepstojustice.ca"
START_PAGE = "/questions/housing-law/"

def scrape_steps_to_justice():
    url = f"{BASE_URL}{START_PAGE}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    scraped_data = []
    question_links = soup.select("a.teaser__title-link")

    for link in question_links:
        href = link.get("href")
        title = link.get_text(strip=True)
        question_url = f"{BASE_URL}{href}"

        question_response = requests.get(question_url)
        question_soup = BeautifulSoup(question_response.text, "html.parser")

        answer_section = question_soup.select_one("div.field--name-field-answer")
        answer_text = answer_section.get_text(strip=True) if answer_section else "No answer found"

        scraped_data.append({
            "question": title,
            "url": question_url,
            "answer": answer_text
        })

    os.makedirs("scraped_data", exist_ok=True)
    with open("scraped_data/steps_to_justice.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=2)

    print(f"Scraped {len(scraped_data)} entries.")
