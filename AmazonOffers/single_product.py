import requests
from selectorlib import Extractor

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('amazon_Scraper\\amazon_single_selectors.yml')


def scrape(link):
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    r = requests.get(link, headers=headers)

    print(e.extract(r.text))

link = 'https://www.amazon.it/OnePlus-Smartphone-Display-Storage-Warranty/dp/B08BPK5QR4/ref=sr_1_2?dchild=1&keywords=Oneplus+6t&qid=1602096891&sr=8-2'

scrape(link)