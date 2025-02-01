import os
import csv
import time
import datetime
from itertools import combinations
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random



# Search criteria
criteria = {
    "postcode": "SO19 9QZ",
    "price_from": "1000",
    "price_to": "100000",
    "radius": "200",
}

# Body types
body_types = [
    "Adventure", "Classic", "Commuter", "Custom Cruiser", "E-Bike",
    "Enduro", "Minibike", "Moped", "Motocrosser", "Naked",
    "Roadster", "Roadster/Retro", "Scooter", "Special",
    "Sports Tourer", "Super Moto", "Super Sports", "Supermoto-Road",
    "Three Wheeler", "Tourer", "Trail (Enduro)", "Trail Bike",
    "Trial Bike", "Trials Bike"
]

# Mileage blocks for search
mileage_blocks = [
    [0, 1000],
    [1000, 5000],
    [5000, 10000],
    [10000, 20000],
    [30000, 40000],
    [50000, 60000],
    [70000, 80000],
    [90000, 250000]
]

def create_directory(base_dir, subfolder_name):
    """Create a directory if it does not exist."""
    folder_path = os.path.join(base_dir, subfolder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def log_error(message):
    """Log errors to a file."""
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - {message}\n")

def scrape_autotrader(criteria):
    """Scrape AutoTrader and handle errors gracefully."""
    chrome_options = Options()
    chrome_options.add_argument("_tt_enable_cookie=1")
    driver = webdriver.Chrome(options=chrome_options)
    data = []

    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        for body_type in body_types:
            print(f"🔎 Scraping listings for: {body_type}")

            for mileage_range in mileage_blocks:
                min_mileage, max_mileage = mileage_range
                print(f"📌 Searching: {body_type} | Mileage: {min_mileage}-{max_mileage}")

                for page_num in range(1, 100):
                    try:
                        url = f"https://www.autotrader.co.uk/bike-search?body-type={body_type}&postcode={criteria['postcode']}&price-from={criteria['price_from']}&price-to={criteria['price_to']}&radius={criteria['radius']}&minimum-mileage={min_mileage}&maximum-mileage={max_mileage}&page={page_num}&sort=most-recent"

                        driver.get(url)
                        print(f"📄 Page {page_num}: {url}")

                        # Wait for elements to load
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, '//*[@data-testid="advertCard"]'))
                            )
                        except:
                            print(f"❌ No listings on page {page_num}. Moving on...")
                            break  

                        # Parse page
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        listings = soup.find_all('div', {'data-testid': 'trader-seller-listing'})

                        if not listings:
                            print(f"⚠️ No results found for {body_type} in {min_mileage}-{max_mileage} miles.")
                            break  

                        for listing in listings:
                            details = {
                                "name": None, "price": None, "year": None, "engine": None,
                                "seller": None, "mileage": None, "owner": None,
                                "dealership_name": None, "body_type": body_type,
                                "min_mileage": min_mileage, "max_mileage": max_mileage,
                                "date_collected": today_date
                            }

                            try:
                                name_tag = listing.find('a', {'data-testid': 'search-listing-title'})
                                if name_tag:
                                    details["name"] = name_tag.find('h3').text.strip()

                                price_tag = listing.find('span', class_='at__sc-1mc7cl3-7 icLPGk')
                                if price_tag:
                                    details["price"] = price_tag.text.strip()

                                dealership_tag = listing.find('span', {'class': 'at__sc-1n64n0d-9 at__sc-1mc7cl3-15 kLylrw ideECV'})
                                if dealership_tag:
                                    details["dealership_name"] = dealership_tag.text.strip()

                                specs = listing.find('ul', {'data-testid': 'search-listing-specs'})
                                if specs:
                                    spec_items = specs.find_all('li')
                                    for spec in spec_items:
                                        if "reg" in spec.text:
                                            details["year"] = spec.text.strip()
                                        elif "cc" in spec.text:
                                            details["engine"] = spec.text.strip()
                                        elif "miles" in spec.text.lower():
                                            details["mileage"] = spec.text.strip()
                                        elif "owner" in spec.text.lower():
                                            details["owner"] = spec.text.strip()

                                seller_tag = listing.find('p', {'data-testid': 'search-listing-seller'})
                                if seller_tag:
                                    details["seller"] = seller_tag.text.strip()

                            except Exception as e:
                                log_error(f"Data extraction error: {e}")

                            data.append(details)

                        time.sleep(random.uniform(1, 10))  

                    except Exception as e:
                        log_error(f"Error on page {page_num} for {body_type}, {min_mileage}-{max_mileage}: {e}")

    except Exception as e:
        log_error(f"General scraping error: {e}")

    finally:
        driver.quit()
        return data  

def create_csv(data):
    """Save scraped data to a CSV file, even if the script fails midway."""
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join("autotrader_raw_data", f"autotrader_data_{today_date}.csv")

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        header = ["Name", "Price", "Year", "Mileage", "Engine", "Owner", "Dealership Name", "Seller", "Body Type", "Min Mileage", "Max Mileage", "Date Collected"]
        writer.writerow(header)

        for row in data:
            writer.writerow([
                row.get("name", ""), row.get("price", ""), row.get("year", ""), row.get("mileage", ""),
                row.get("engine", ""), row.get("owner", ""), row.get("dealership_name", ""),
                row.get("seller", ""), row.get("body_type", ""), row.get("min_mileage", ""),
                row.get("max_mileage", ""), row.get("date_collected", "")
            ])

    print(f"✅ Data saved to {filename}")

if __name__ == "__main__":
    scraped_data = scrape_autotrader(criteria)
    create_csv(scraped_data)
