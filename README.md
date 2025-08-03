# ClustrMaps Person Search Tool

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-orange)

A Python script for searching and extracting person information from ClustrMaps.com using Selenium and BeautifulSoup.

## Features

- Search for people by first name, last name, and optional state
- Extract detailed information including:
  - Name and age
  - Address and state
  - Associated persons
  - Phone numbers
  - Email addresses
- Save results in CSV format
- Generate HTML debug files for manual inspection
- Human-like delays to avoid detection
- Automatic browser restart to maintain stability

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/airborne-commando/clustrmaps-scraper.git
   cd clustrmaps-scraper
   ```

2. Install the required dependencies:
   ```
   pip install selenium beautifulsoup4
   ```

3. Download ChromeDriver and place it in `/usr/bin/chromedriver` or update the path in the script.

## Usage

1. Create a CSV input file with columns: `first_name`, `last_name`, and optionally `state`.

   Example (`input.csv`):
   ```
   first_name,last_name,state
   John,Smith,CA
   Jane,Doe,NY
   ```

2. Run the script:
   ```
   python clstrmaps.py
   ```

3. When prompted, enter the path to your CSV file.

## Output

The script creates a `results` directory containing:

- `results_[name]_main.csv` - Main search results
- `results_[name]_quickfacts.csv` - Detailed information including emails and phone numbers
- `[name]_details.html` - HTML files for manual inspection
- `clustrmaps_log.txt` - Log file of script activity

### Viewing HTML Files

You can open the generated HTML files in any web browser to:
- Verify the data extraction
- View additional information that might not have been automatically extracted
- Check the structure of the pages for debugging

## Configuration

You can modify the following variables in the script:

- `chrome_driver_path` - Path to your ChromeDriver executable
- Human delay timings in the `human_delay()` function
- Browser restart frequency (currently every 2 searches)

## Notes

- The script includes random delays to mimic human behavior and avoid detection.
- The browser restarts periodically to maintain stability during long scraping sessions.
- Results are saved incrementally, so you can stop and restart the script without losing data.

## License

This project is licensed under the Unlicense - see the [LICENSE](LICENSE) file for details.
