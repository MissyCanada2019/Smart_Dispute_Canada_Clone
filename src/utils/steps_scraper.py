import requests
from bs4 import BeautifulSoup
import json
import os

BASE_URL = "https://stepstojustice.ca/legal-topics/"
OUTPUT_FILE = "steps_to_justice_topics.json"

def scrape_steps_to_justice_topics():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    topics_data = []

    # Find all main topic links
    topic_section = soup.find('div', class_='view-content')
    if not topic_section:
        return []

    topic_links = topic_section.find_all('a', href=True)

    for link in topic_links:
        topic_title = link.get_text(strip=True)
        topic_url = link['href']
        if not topic_url.startswith('http'):
            topic_url = 'https://stepstojustice.ca' + topic_url

        topic_info = {
            'topic': topic_title,
            'url': topic_url,
            'subtopics': []
        }

        # Now go scrape subtopics from the topic's page
        topic_page = requests.get(topic_url)
        topic_soup = BeautifulSoup(topic_page.text, 'html.parser')

        subtopic_links = topic_soup.find_all('a', class_='card--link')
        for sublink in subtopic_links:
            sub_title = sublink.get_text(strip=True)
            sub_url = sublink['href']
            if not sub_url.startswith('http'):
                sub_url = 'https://stepstojustice.ca' + sub_url
            topic_info['subtopics'].append({
                'title': sub_title,
                'url': sub_url
            })

        topics_data.append(topic_info)

    return topics_data

def save_to_json(data):
    folder = os.path.join(os.getcwd(), "data")
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, OUTPUT_FILE)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Scraped data saved to {file_path}")

if __name__ == "__main__":
    data = scrape_steps_to_justice_topics()
    save_to_json(data)
