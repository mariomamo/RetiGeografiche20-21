from AmazonOffers.scraper.Generic_scraper import Generic_scraper
import sys

class ScraperHelper:
    _separ_char = '|%!|'

    def screap_from_file(self, scraper: Generic_scraper, file_path: str, selector: str = 'single') -> dict:
        print(selector)

        with open(file_path, 'r') as file:
            urls = file.readlines()
            for i in range(urls.__len__()):
                urls[i] = urls[i].splitlines()[0]

            products = scraper.get_offers(urls, selector=selector)

        return products

    def screap_from_file2(self, scraper: Generic_scraper, file_path: str, selector: str = 'single') -> list:
        # print(selector)

        product_list = []

        with open(file_path, 'r') as file:
            urls = file.readlines()
            for i in range(urls.__len__()):
                string = urls[i].splitlines()[0]
                #print("STRING: " + string)

                numero_parametri = string.count(self._separ_char)
                #print('param: ', numero_parametri, string)

                product = []

                # Se si scrivono dei parametri. Es:
                # iphone |%!| https://...
                if numero_parametri > 0:
                    # Prendo di volta in volta un parametro dalla stringa
                    # Modifico la stringa originale rimuovendo il parametro appena letto
                    # Per poter leggere gli altri
                    for j in range(numero_parametri):
                        param = string[0:string.find(self._separ_char) - 1]
                        product.append(param)
                        print("PARAM APPENDED: " + param)
                        string = string[string.find(self._separ_char) + self._separ_char.__len__():string.__len__()]
                        #product.append(string[1:string.__len__()])
                    product.append(string[1:string.__len__()])
                # Se si scrive solo il link. Es:
                # https://...
                elif numero_parametri == 0:
                    param = ''
                    product.append(param)
                    product.append(string[0:string.__len__()])

                product_list.append(product)
                urls[i] = urls[i].splitlines()[0]

        # print(product_list)
        for i in range(product_list.__len__()):
            print("PRODOTTO: ", product_list[i])

        products = scraper.get_offers(product_list, selector=selector)
        print(products)
        return products

    def calculate_percentage_discount(self, original_price: float, selling_price: float):
        if original_price is None:
            original_price = selling_price
        if not isinstance(original_price, float):
            original_price = self._convert_price_to_float(original_price)
        if not isinstance(selling_price, float):
            selling_price = self._convert_price_to_float(selling_price)
        if original_price == 0:
            original_price = 1

        discount = original_price - selling_price
        return (discount / original_price) * 100

    def _convert_price_to_float(self, original_price):
        if original_price is None:
            return 0
        price = str(original_price)
        price = price.replace('\xa0€', '')
        price = price.replace('.', '')
        price = price.replace(',', '.')
        return float(price)

    def save__single_offer(self, product_list: list):
        max = None
        discount = 0
        # print(discount)
        for product in product_list:
            if product['old-price'] is not None:
                new_discount = self.calculate_percentage_discount(product['old-price'], product['price'])
                #  max['price'] > product['price'] or
                if max is None or new_discount > discount:
                    max = product
                    discount = new_discount

        if max is not None:
            self.__print_info(max, discount)
            self.__print_info_to_file('amazonOut.txt', max, discount)
            # print('+ OFFERTA! {} a {} invece di {}\n|--- {}, {}% di sconto ({}€ di sconto)\n|--- {}\n|--- {}'.format(
            #     max['name'], max['price'],
            #     max['old-price'], max['rating'], round(discount, 2), round(risparmio_in_soldi, 2),
            #     'https://www.amazon.it' + max['url'], max['image']))

    def save_multiple_offers(self, product_list: list, discount=True):
        # print(discount)
        # Ottengo la lista con solo gli sconti
        product_list = self.get_multiple_offers(product_list, discount=discount)
        for product in product_list:
            self.__print_info(product, product['discount'])
            self.__print_info_to_file('amazonOut.txt', product, product['discount'])

    def get_multiple_offers(self, product_list: list, discount=True) -> list:
        # print(discount)
        output = []
        for product in product_list:
            # Aggiungi alla lista solo se c'è lo sconto
            if discount and product['old-price'] is not None:
                discount = self.calculate_percentage_discount(product['old-price'], product['price'])
                if discount >= 3:
                    product['discount'] = discount
                    output.append(product)
            elif not discount:
                product['discount'] = discount
                output.append(product)

        return output

    def get_info_string(self, product: dict, discount: float):
        risparmio_in_soldi = (
                    self._convert_price_to_float(product['old-price']) - self._convert_price_to_float(product['price']))

        return '+ OFFERTA! {}\n|--- {} invece di {}\n|--- {}, {}% di sconto ({}€ di sconto)\n|--- {}\n|--- {}'.format(
            product['name'], product['price'],
            product['old-price'], product['rating'], round(discount, 2), round(risparmio_in_soldi, 2),
            'https://www.amazon.it' + product['url'], product['image'])

    def __print_info(self, product: dict, discount: float):
        print(self.get_info_string(product, discount))

    def __print_info_to_file(self, fileName: str, product: dict, discount: float):
        original_stdout = sys.stdout

        with open(fileName, 'a') as file:
            sys.stdout = file
            self.__print_info(product, discount)
            sys.stdout = original_stdout
