from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
import re
from datetime import datetime, timedelta

# Setup Chrome Options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Initializing Chrome WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Define Search Parameters
departure_city = "DAC"
destination_cities = ["JFK", "LHR", "DXB", "JED", "SIN"]

# Generate 3 months of departure dates (February, March, April 2025)
start_date = datetime(2025, 2, 1)
end_date = datetime(2025, 4, 30)

departure_dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end_date - start_date).days + 1)]

# Get the current date for the scrape_date column
scrape_date = datetime.today().strftime('%Y-%m-%d')

# CSV File Setup
csv_filename = "flights_data.csv"
header = ["scrape_date", "departure_from", "destination", "travel_date", "airline_name", "duration", "stoppage", "ticket_price_BDT"]

with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(header)

    for city in destination_cities:
        for date in departure_dates:
            print(f"Scraping: {departure_city} to {city} on {date}")

            # Construct Google Flights URL
            url = f"https://www.google.com/travel/flights?q=Flights%20to%20{city}%20from%20{departure_city}%20on%20{date}&hl=en"
            driver.get(url)
            time.sleep(5)  

            try:
                # Locate the <ul> tag containing all flights
                flight_list = driver.find_element(By.XPATH, "//*[@id='yDmH0d']/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[1]/ul")

                # Get all <li> elements (each flight)
                flights = flight_list.find_elements(By.TAG_NAME, "li")
                print(f"Found {len(flights)} flights for {city} on {date}")

                for flight in flights:
                    try:
                        # Extract flight details
                        airline = flight.find_element(By.XPATH, ".//div/div[2]/div/div[2]/div/div[2]/div[2]/span").text
                        duration = flight.find_element(By.XPATH, ".//div/div[2]/div/div[2]/div/div[3]/div").text
                        stoppage = flight.find_element(By.XPATH, ".//div/div[2]/div/div[2]/div/div[4]/div[1]/span[1]").text
                        price_bdt_text = flight.find_element(By.XPATH, ".//div/div[2]/div/div[2]/div/div[6]/div[1]/div[2]/span").text
                        
                        # Extract numeric price from BDT format
                        price_bdt = int(re.sub(r"[^\d]", "", price_bdt_text))

                        # Write data to CSV (including scrape_date)
                        writer.writerow([scrape_date, departure_city, city, date, airline, duration, stoppage, price_bdt])
                        print(f"Collected: {airline}, {duration}, {stoppage}, BDT {price_bdt}")

                    except Exception as e:
                        print(f"Skipping a flight due to error: {e}")

            except Exception as e:
                print(f"Data not found for {departure_city} to {city} on {date}: {e}")

driver.quit()
print("Scraping complete. Data saved to flights_data.csv.")
