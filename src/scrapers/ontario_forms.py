import requests
from bs4 import BeautifulSoup

BASE_URL = "https://ontariocourtforms.on.ca/en/"
HEADERS = {"User-Agent": "SmartDisputeBot/1.0"}

def scrape_ontario_forms():
    forms = []

    res = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    categories = soup.select("section.category-box a")

    for cat in categories:
        cat_name = cat.get_text(strip=True)
        cat_url = cat["href"]

        if not cat_url.startswith("http"):
            cat_url = BASE_URL.rstrip("/") + cat_url

        page = requests.get(cat_url, headers=HEADERS)
        sub_soup = BeautifulSoup(page.text, "html.parser")

        for link in sub_soup.select("a[href$='.doc'], a[href$='.pdf']"):
            form_url = link["href"]
            form_name = link.get_text(strip=True)
            file_type = "pdf" if ".pdf" in form_url else "doc"

            if not form_url.startswith("http"):
                form_url = BASE_URL.rstrip("/") + form_url

            forms.append({
                "name": form_name,
                "court": cat_name,
                "category": cat_name,
                "url": form_url,
                "jurisdiction": "ontario",
                "file_type": file_type
            })

    return forms
