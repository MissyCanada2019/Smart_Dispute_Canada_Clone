from scrapers.steps_to_justice import scrape_steps_to_justice

def run_all_scrapers():
    scrape_steps_to_justice()
    print("All scraping complete.")

if __name__ == "__main__":
    run_all_scrapers()
