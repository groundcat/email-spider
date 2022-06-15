from bs4 import BeautifulSoup
from requests import get
import re
from validate_email import validate_email
import pandas as pd
import datetime
import configparser

# Load the config file config.ini
config = configparser.ConfigParser()
config.read('config.ini')
config.sections()

# Dictionary for storing email and urls
emails_dict = {}

# Read URLs from the file
with open(config['SPIDER']['SOURCE_URLS'], 'r') as f:

    urls = f.readlines()

    for url in urls:

        # Clean the URL
        url = url.strip()

        # Add http:// to the URL if it is missing
        if not re.match(r'^https?://', url):
            url_cleaned = 'http://' + url
        else:
            url_cleaned = url
        url_cleaned = url_cleaned.rstrip('/')

        # Skip if the URL is already in the dictionary
        if url in emails_dict:
            continue

        print(f"Parsing {url_cleaned}")

        # Get the page
        try:
            headers = {
                'User-Agent': config['SPIDER']['USER_AGENT']}
            page = get(url_cleaned, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
            continue

        # Parse the page
        soup = BeautifulSoup(page.text, 'html.parser')
        # webpage_title = soup.title.text

        # Parse the first email address with regex
        emails = re.findall(r'[\w\.-]+@[\w\.-]+(?:\.[\w]+)+', page.text)

        if emails:
            for email in emails:
                # Validate the email address
                is_valid = validate_email(
                    email_address=email,
                    check_format=True,
                    check_blacklist=True,
                    check_dns=True,
                    dns_timeout=10,
                    check_smtp=False)

                if is_valid:
                    print(f"Email found: {email}")
                    # Add the email to the dictionary
                    emails_dict[url] = email
                    break
                else:
                    print(f"Email not valid: {email}")

        else:
            print(f"No email found on {url_cleaned}")

# Create a DataFrame from the dictionary
df = pd.DataFrame.from_dict(emails_dict, orient='index', columns=['email'])

# Timestamp
now = datetime.datetime.now()

# Construct to a CSV file
df.to_csv(f'emails_{now}.csv', index=True)
