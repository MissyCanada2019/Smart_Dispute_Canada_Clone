import requests
from bs4 import BeautifulSoup

# Base CanLII URL structure
BASE_URL = "https://www.canlii.org/en/"

# Define the jurisdictions (Federal, Provinces, etc.)
jurisdictions = ["federal", "ontario", "british-columbia", "quebec", "alberta", "manitoba", "saskatchewan"]

# Function to fetch cases from CanLII
def fetch_cases(jurisdiction, keyword):
    url = f"{BASE_URL}{jurisdiction}/"
    response = requests.get(url)
    
    # Check if response is successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for relevant case summaries or case listings
        cases = soup.find_all('div', {'class': 'result-summary'})
        
        filtered_cases = []
        for case in cases:
            # Search for cases that match the keyword
            case_title = case.find('a').text
            case_url = case.find('a')['href']
            if keyword.lower() in case_title.lower():
                filtered_cases.append({'title': case_title, 'url': f"{BASE_URL}{case_url}"})
        
        return filtered_cases
    else:
        print(f"Failed to fetch data for jurisdiction: {jurisdiction}")
        return []

# Function to categorize cases by issue (e.g., landlord-tenant, mold issues, etc.)
def categorize_cases(cases, issue_type):
    categorized_cases = []
    
    # Simple keyword matching for categorization
    for case in cases:
        if issue_type.lower() in case['title'].lower():
            categorized_cases.append(case)
    
    return categorized_cases

# Sample usage: Fetching and categorizing landlord-tenant cases for Ontario
keyword = "landlord-tenant"  # Example issue type
jurisdiction = "ontario"

all_cases = []
for juris in jurisdictions:
    cases = fetch_cases(juris, keyword)
    all_cases.extend(cases)

# Now filter cases based on specific issue
filtered_landlord_cases = categorize_cases(all_cases, "landlord")

# Print out the filtered cases
for case in filtered_landlord_cases:
    print(f"Title: {case['title']}, URL: {case['url']}")
