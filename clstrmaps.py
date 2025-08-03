from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import os
import csv
import re
import shutil

# Path to ChromeDriver
chrome_driver_path = '/usr/bin/chromedriver'

# State abbreviations to full names mapping
STATE_ABBREVIATIONS = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# Create results directory if it doesn't exist
if not os.path.exists('results'):
    os.makedirs('results')

def expand_state_abbreviation(state):
    """Convert state abbreviation to full name if needed"""
    if not state:
        return None
    state = state.strip().upper()
    return STATE_ABBREVIATIONS.get(state, state)

def human_delay(min=0.5, max=1.5):
    time.sleep(random.uniform(min, max))

def log_message(message):
    with open('results/clustrmaps_log.txt', 'a') as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

def save_details_html(content, filename):
    """Save or append to details HTML file with separator"""
    try:
        if os.path.exists(filename):
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"\n<!-- ====== NEW DETAILS PAGE ====== -->\n")
                f.write(content)
            log_message(f"Appended to details HTML file: {filename}")
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            log_message(f"Created new details HTML file: {filename}")
    except Exception as e:
        log_message(f"Error saving details HTML: {str(e)}")

def read_input_from_file(file_path):
    data = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'first_name' in row and 'last_name' in row:
                    record = {
                        'first_name': row['first_name'].strip(),
                        'last_name': row['last_name'].strip()
                    }
                    if 'state' in row and row['state'].strip():
                        record['state'] = expand_state_abbreviation(row['state'].strip())
                    data.append(record)
        return data
    except Exception as e:
        log_message(f"Error reading input file: {str(e)}")
        return []

def extract_main_page_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    person_entries = soup.find_all('div', itemprop='Person')
    
    for entry in person_entries:
        person_info = {}
        
        # Basic info
        name_tag = entry.find('span', itemprop='name')
        person_info['name'] = name_tag.text if name_tag else 'N/A'
        
        age_tag = entry.find('span', class_='age')
        person_info['age'] = age_tag.text.replace(',', '').strip() if age_tag else 'N/A'
        
        # Address
        street = entry.find('span', itemprop='streetAddress')
        locality = entry.find('span', itemprop='addressLocality')
        state = entry.find('span', itemprop='addressRegion')
        person_info['address'] = f"{street.text}, {locality.text}" if street and locality else 'N/A'
        person_info['state'] = expand_state_abbreviation(state.text) if state else 'N/A'
        
        # Associated persons
        associated = [el.find('span', itemprop='name').text for el in entry.find_all('span', itemprop='relatedTo') if el.find('span', itemprop='name')]
        person_info['associated_persons'] = ' | '.join(associated) if associated else 'N/A'
        
        # Phone
        phone = entry.find('span', itemprop='telephone')
        person_info['phone'] = phone.text if phone else 'N/A'
        
        # Details page URL
        details_link = entry.find('a', class_='btn-success')
        if details_link and 'href' in details_link.attrs:
            person_info['details_url'] = f"https://clustrmaps.com{details_link['href']}"
        
        results.append(person_info)
    
    return results

def extract_quick_facts(html_content, source_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    quick_facts = {
        'name': 'N/A',
        'emails': 'N/A',
        'phone_numbers': 'N/A',
        'source_url': source_url
    }

    try:
        # Extract name from the title or heading
        name_tag = soup.find('h1', class_='person-name')
        if name_tag:
            quick_facts['name'] = name_tag.get_text(strip=True)

        # Find the Quick Facts section
        quick_facts_div = soup.find('div', id='intro')
        if quick_facts_div:
            full_text = quick_facts_div.get_text(' ', strip=True)

        # Extract Emails
        emails = set()
        for mail_link in soup.find_all('a', href=lambda x: x and x.startswith('mailto:')):
            email = mail_link.get_text(strip=True)
            if '@' in email:
                emails.add(email)
        if emails:
            quick_facts['emails'] = ' | '.join(sorted(emails))

        # Extract Phone Numbers
        phones = set()
        for tel_link in soup.find_all('a', href=lambda x: x and x.startswith('tel:')):
            phone = tel_link.get_text(strip=True)
            if phone:
                phones.add(phone)
        if phones:
            quick_facts['phone_numbers'] = ' | '.join(sorted(phones))

    except Exception as e:
        log_message(f"Error extracting quick facts: {str(e)}")
    
    return quick_facts

def get_person_url(first_name, last_name, state=None):
    first = '-'.join([part.capitalize() for part in first_name.split('-')])
    last = last_name.replace(' ', '_').capitalize()
    if state:
        # Convert state to proper format for URL (replace spaces with underscores)
        state_url = state.replace(' ', '_')
        return f"https://clustrmaps.com/persons/{first}-{last}/{state_url}"
    return f"https://clustrmaps.com/persons/{first}-{last}"

def save_to_csv(data, filename, fieldnames):
    try:
        filename = f"results/{filename}"
        if not os.path.exists(filename):
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data) if isinstance(data, list) else writer.writerow(data)
            log_message(f"Saved {filename}")
        else:
            log_message(f"File {filename} already exists - skipping")
    except Exception as e:
        log_message(f"Error saving {filename}: {str(e)}")

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(chrome_driver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

def main():
    driver = None
    
    try:
        file_path = input("Enter CSV file path (columns: first_name, last_name, [state]): ").strip()
        input_data = read_input_from_file(file_path)
        
        if not input_data:
            log_message("No valid input data. Exiting.")
            return
        
        driver = create_driver()
        
        for i, person in enumerate(input_data):
            first_name = person['first_name']
            last_name = person['last_name']
            state = person.get('state')
            base_filename = f"{first_name}_{last_name}"
            if state:
                base_filename += f"_{state.replace(' ', '_')}"
            
            log_message(f"\nProcessing {i+1}/{len(input_data)}: {first_name} {last_name}" + 
                       (f" in {state}" if state else ""))
            
            # Skip if all output files exist
            if (os.path.exists(f"results/results_{base_filename}_main.csv") and 
                os.path.exists(f"results/results_{base_filename}_quickfacts.csv")):
                log_message("All output files exist - skipping")
                continue
            
            # Get main profile page
            url = get_person_url(first_name, last_name, state)
            driver.get(url)
            human_delay(2, 4)
            
            # Check for 404
            if "Page Not Found" in driver.title:
                log_message(f"No main profile found at {url}")
                continue
            
            # # Save main debug HTML
            # debug_filename = f'debug_{base_filename}.html'
            # if not os.path.exists(debug_filename):
            #     with open(debug_filename, 'w', encoding='utf-8') as f:
            #         f.write(driver.page_source)
            #     log_message(f"Saved debug HTML to {debug_filename}")
            # else:
            #     log_message(f"Debug file {debug_filename} already exists - skipping")
            
            # Extract main page info
            main_info = extract_main_page_info(driver.page_source)
            save_to_csv(
                main_info,
                f"results_{base_filename}_main.csv",
                ['name', 'age', 'address', 'state', 'associated_persons', 'phone', 'details_url']
            )
            
            # Process details pages
            quick_facts_data = []
            for person_info in main_info:
                if 'details_url' in person_info and person_info['details_url'] != 'N/A':
                    log_message(f"Fetching details page: {person_info['details_url']}")
                    driver.get(person_info['details_url'])
                    human_delay(2, 4)
                    
                    # Save details HTML
                    details_filename = f"results/{base_filename}_details.html"
                    save_details_html(driver.page_source, details_filename)
                    
                    # Extract quick facts
                    quick_facts = extract_quick_facts(driver.page_source, person_info['details_url'])
                    quick_facts['name'] = person_info['name']
                    quick_facts_data.append(quick_facts)
            
            if quick_facts_data:
                save_to_csv(
                    quick_facts_data,
                    f"results_{base_filename}_quickfacts.csv",
                    ['name', 'emails', 'phone_numbers', 'source_url']
                )
            
            # Random delay between searches
            delay = random.uniform(10, 20)
            log_message(f"Waiting {delay:.1f} seconds...")
            time.sleep(delay)
            
            # Restart browser periodically
            if i > 0 and i % 2 == 0:
                log_message("Restarting browser...")
                driver.quit()
                time.sleep(random.uniform(5, 10))
                driver = create_driver()
                
    except Exception as e:
        log_message(f"Fatal error: {str(e)}")
        if driver:
            driver.save_screenshot('error.png')
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()