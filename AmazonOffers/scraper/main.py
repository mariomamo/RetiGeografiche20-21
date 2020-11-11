from AmazonOffers.TelegramBot.bot import Bot

TOKEN = '1392773235:AAF9OHQvdm9xAA0DU2DOvw_ivkmtL-gAYN8'

if __name__ == '__main__':
    bot = Bot(token=TOKEN)
    bot.start_bot()
    # amazonScraper = Amazon_scraper()
    # helper = ScraperHelper()
    # product_list = helper.screap_from_file2(amazonScraper, 'amazon_scraper\\amazon_multiple_product_list.txt', selector='multiple')
    # print(type(product_list))
    # print(product_list)
    # try:
    #     print('result:', type(product_list), 'content:', type(product_list[0]))
    # except IndexError as ex:
    #     print('EXCEPTION:', ex)

    print('\n=============\n')

    # helper.save_multiple_offers(product_list)
    # helper.save__single_offer(product_list)

    # for product in product_list:
    #     print(type(product))
    #     print('+++', product['name'])
    #     print('   -', product['old-price'])
    #     print('   -', product['price'])
    #     print('   -', product['url'])
    #     print('   -', product['image'])

    # product_list = screap_from_file2(amazonScraper, 'amazon_scraper\\amazon_multiple_product_list.txt')
    # diz = screap_from_file(amazonScraper, 'amazon_scraper\\amazon_single_product_list.txt')
    # print(type(diz))
    # print(diz)
    #
    # for product in product_list:
    #     print(type(product))
    #     print('+++', product['name'])
    #     print('   -', product['price'])
    #     print('   -', product['url'])
    #     print('   -', product['image'])

