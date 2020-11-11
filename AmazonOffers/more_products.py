import requests
from selectorlib import Extractor

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('amazon_scraper\\amazon_multiple_selectors.yml')


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

    p = e.extract(r.text)

    for product in p['products']:
        print(type(product))
        print('+++', product['name'])
        print('   -', product['old-price'])
        print('   -', product['price'])
        print('   -', product['url'])
        print('   -', product['image'])

    print(e.extract(r.text))

link = 'https://www.amazon.it/s?k=Oneplus+6t'

scrape(link)