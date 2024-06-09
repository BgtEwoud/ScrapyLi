
"""
Created on Sat Jun  8 15:33:27 2024
@author: EwoudBogaert
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os
# LinkedIn credentials
username = "ewoud.bogaert@hotmail.com"
password = "stormvogels3264"

# -*- coding: utf-8 -*-




# Initialize the Selenium WebDriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.linkedin.com/login")

# Log in to LinkedIn
driver.find_element(By.ID, "username").send_keys(username)
driver.find_element(By.ID, "password").send_keys(password)
driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Allow time for login to complete
WebDriverWait(driver, 10).until(EC.url_contains("feed"))

from selenium.common.exceptions import NoSuchElementException

def search_profile(driver, first_name, last_name):
    search_box = driver.find_element(By.XPATH, "//input[@placeholder='Search']")
    search_box.clear()
    search_query = f"{first_name} {last_name}"
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    try:
        # Wait for the search results container to be present
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-container")))
        # Get the HTML of the search results page
        search_results_html = driver.page_source
        return search_results_html
    except NoSuchElementException:
        print("Unable to locate the search results container.")
        return None


# Function to extract profile data from search results using BeautifulSoup
def extract_profile_data(html,person):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        job = soup.select_one('.entity-result__primary-subtitle').get_text(strip=True)
        location = soup.select_one('.entity-result__secondary-subtitle').get_text(strip=True)
        profile_data = {
                'voornaam' : person['Voornaam'],
                'achternaam' : person['Achternaam'],
                'job': job,
                'location': location,
            }
        return profile_data
    except AttributeError:
        print(f"Extraction unsuccessful for {person['Voornaam']} {person['Achternaam']}.")
        profile_data = {
                'voornaam' : person['Voornaam'],
                'achternaam' : person['Achternaam'],
                'job': "not found",
                'location': "not found",
            }  
        return None    

# Read data from Excel file
excel_file = r"C:\Users\EwoudBogaert\OneDrive - Bogaert-Audit\3 - Automatisatie\024. Linkedinscraper\stagairs.xlsx"
people_df = pd.read_excel(excel_file)

# Scrape profiles and collect data
profile_data_list = []


start_row_index = 41
for index, person in people_df.iterrows():
    if index < start_row_index:
        continue
    first_name = person['Voornaam']
    last_name = person['Achternaam']
    search_results_html = search_profile(driver, first_name, last_name)
    if search_results_html:
        profile_data = extract_profile_data(search_results_html, person)
        if profile_data:
            profile_data_list.append(profile_data)

for profile in profile_data_list:
    print(profile)


df = pd.DataFrame(profile_data_list)

# Export DataFrame to Excel
output_excel_file = "enriched_data-v1.xlsx"
df.to_excel(output_excel_file, index=False)

# Open Excel file
os.system("start " + output_excel_file)

# Close the driver
driver.quit()