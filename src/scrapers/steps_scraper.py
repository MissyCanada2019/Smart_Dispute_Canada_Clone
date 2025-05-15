import requests
from bs4 import BeautifulSoup
import os
import json

OUTPUT_FILE = "steps_to_justice_data.json"

def scrape_steps_to_justice():
    base_url = "https://stepstojustice.ca"
    main_url = f"{base_url}/legal-topics/"
    topics_data = []

    try:
        res = requests.get(main_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        topic_links = soup.select("div.view-content a")

        for link in topic_links:
            topic_title = link.get_text(strip=True)
            topic_url = link.get("href")
            if not topic_url.startswith("http"):
                topic_url = base_url + topic_url

            topic_info = {
                'topic': topic_title,
                'url': topic_url,
                'subtopics': []
            }

            # Scrape subtopics from the topic's page
            try:
                topic_page = requests.get(topic_url)
                topic_soup = BeautifulSoup(topic_page.text, 'html.parser')
                subtopic_links = topic_soup.find_all('a', class_='card--link')

                for sublink in subtopic_links:
                    sub_title = sublink.get_text(strip=True)
                    sub_url = sublink['href']
                    if not sub_url.startswith("http"):
                        sub_url = base_url + sub_url
                    topic_info['subtopics'].append({
                        'title': sub_title,
                        'url': sub_url
                    })
            except Exception as inner_e:
                print(f"Failed to scrape subtopics for {topic_title}: {inner_e}")

            topics_data.append(topic_info)

        return topics_data

    except Exception as e:
        print(f"Scraper error: {e}")
        return []

def save_to_json(data):
    folder = os.path.join(os.getcwd(), "data")
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, OUTPUT_FILE)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Scraped data saved to {file_path}")

# Optional standalone run
if __name__ == "__main__":
    data = scrape_steps_to_justice()
    save_to_json(data)
