import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Simulated scraped Steps to Justice topics
def scrape_steps_to_justice():
    base_url = "https://stepstojustice.ca/legal-topics/"
    try:
        res = requests.get(base_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        topic_links = soup.select("div.view-content a")

        topics = []
        for link in topic_links:
            title = link.get_text(strip=True)
            href = link.get("href")
            url = href if href.startswith("http") else f"https://stepstojustice.ca{href}"
            topics.append({
                "title": title,
                "url": url,
                "source": "Steps to Justice"
            })

        return topics
    except Exception as e:
        print("Steps scrape error:", e)
        return []

# Simulated CanLII scraper returning static examples (replace later)
def fetch_canlii_cases(issue, province="ontario"):
    dummy_cases = [
        {"title": "Tenant rights in Ontario", "url": "https://www.canlii.org/en/on/onltb/doc/2022/2022canlii1234/2022canlii1234.html", "source": "CanLII"},
        {"title": "Small claims procedure", "url": "https://www.canlii.org/en/on/onsc/doc/2021/2021onsc4567/2021onsc4567.html", "source": "CanLII"},
    ]
    return dummy_cases

# NLP-powered matching
def match_relevant_content(user_issue, scraped_data, top_n=5):
    texts = [item["title"] for item in scraped_data]
    vectorizer = TfidfVectorizer().fit_transform([user_issue] + texts)
    similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()
    
    scored_items = []
    for i, score in enumerate(similarities):
        item = scraped_data[i]
        item["relevance"] = float(score)
        scored_items.append(item)

    # Sort by relevance
    return sorted(scored_items, key=lambda x: x["relevance"], reverse=True)[:top_n]

# Unified fetch function for SmartDispute
def fetch_all_relevant_help(issue, province="ontario"):
    steps_data = scrape_steps_to_justice()
    canlii_data = fetch_canlii_cases(issue, province)
    combined = steps_data + canlii_data
    return match_relevant_content(issue, combined)
