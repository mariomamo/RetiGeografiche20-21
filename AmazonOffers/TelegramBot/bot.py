from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, MessageHandler, Filters
from AmazonOffers.TelegramBot.HandlerFunction import HandlerFunction
from AmazonOffers.scraper.Amazon_scraper import Amazon_scraper
from AmazonOffers.scraper.ScraperHelper import ScraperHelper


class Bot:

    __dispatcher = None
    __GROUP_ID = -1001344081506
    __MARIO = 164329086

    __TOKEN = ''
    __enabled_users = [__MARIO]

    __scraper_list = []
    __scraper_helper = None

    def __init__(self, token: str):
        self.__TOKEN = token
        self.__scraper_list.append(Amazon_scraper())
        self.__scraper_helper = ScraperHelper()

    def start_bot(self):
        updater = Updater(token=self.__TOKEN, use_context=True)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        self.__dispatcher = updater.dispatcher

        # Aggiungo i comandi che iniziano con '/'
        command_list = []
        command_list.append(HandlerFunction('start', self.__start))
        command_list.append(HandlerFunction('find_product', self.__find_product))

        self.__register_function(command_list)

        # Aggiungo un handler che ripete tutto
        echo_handler = MessageHandler(Filters.text & (~Filters.command), self.__echo)
        self.__dispatcher.add_handler(echo_handler)
        unknown_handler = MessageHandler(Filters.command, self.__unknown)
        self.__dispatcher.add_handler(unknown_handler)

        updater.start_polling()

    def __register_function(self, functions: list):
        for function in functions:
            if type(function) is not HandlerFunction:
                raise Exception('[ERROR] __register_function take a list of HandlerFunction objects.')
            # Aggiungo gli handler
            self.__dispatcher.add_handler(CommandHandler(function.name, function.callback))

    def __send_message(self, update, context, text='', chat_id=None):
        # Ottengo l'ID e l'username della persona che ha inviato il messaggio
        id = update.message.from_user['id']
        username = update.message.from_user['username']
        # Se la persona è nella lista delle persone abilitate, il messaggio viene inviato
        if id in self.__enabled_users:
            if chat_id is None: chat_id = update.effective_chat.id
            context.bot.send_message(chat_id=chat_id, text=text)
        else:
            # Altrimenti viene comunicato un messaggio di errore
            context.bot.send_message(chat_id=id, text='[{} - {}] You are not enabled to use this bot.'.format(username, id))

    def __start(self, update, context):
        self.__send_message(update, context, 'I\'m a bot, please talk to me!', chat_id=self.__GROUP_ID)
        self.__send_message(update, context, 'Message sendend in group')

    def __echo(self, update, context):
        self.__send_message(update, context, update.message.text)

    def __find_product(self, update, context):
        discount = 0

        for scraper in self.__scraper_list:
            product_list = self.__scraper_helper.screap_from_file2(scraper, 'C:\\Users\\Mario\\Desktop\\Mario\\Progetti\\RetiGeografiche20-21\\AmazonOffers\\amazon_scraper\\amazon_multiple_product_list.txt', selector='multiple')
            product_list = self.__scraper_helper.get_multiple_offers(product_list)
            print('SIZE:', product_list.__len__())
            for product in product_list:
                info_string = self.__scraper_helper.get_info_string(product, product['discount'])
                self.__send_message(update, context, info_string, chat_id=self.__GROUP_ID)
                print('INFO:', info_string)

        self.__send_message(update, context, 'Products sended')

    def __unknown(self, update, context):
        self.__send_message(update, context, 'Sorry, I didn\'t understand that command.')
