import logging
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from utility import FileUtility


class HandlerFunction:

    def __init__(self, name: str, callback):
        self.__name = name
        if callback is None:
            self.__callback = self.__default_callback
        else:
            self.__callback = callback

    @property
    def name(self): return self.__name

    @name.setter
    def name(self, name: str): self.__name = name

    @property
    def callback(self): return self.__callback

    @callback.setter
    def callback(self, callback):
        if callback is None: self.__callback = self.__default_callback
        self.__callback = callback

    def __default_callback(self, update, context):
        id = update.message.from_user['id']
        username = update.message.from_user['username']

        context.bot.send_message(chat_id=id, text='Callback is null')


class Bot:

    __userdata = {}
    __step = {}
    __handler = {}

    __dispatcher = None
    __GROUP_ID = -1001344081506
    __MARIO = 164329086
    __ANTONIO = 397466736

    __TOKEN = ''
    __enabled_users = [__MARIO, __ANTONIO]

    __scraper_list = []
    __scraper_helper = None

    def __init__(self, token: str):
        self.__TOKEN = token
        for id in self.__enabled_users:
            self.__step[id] = 0
            self.__userdata[id] = []

    def start_bot(self):
        updater = Updater(token=self.__TOKEN, use_context=True)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        # Inizializzo le variabili
        self.__initVariables()

        self.__dispatcher = updater.dispatcher
        # Aggiungo i comandi che iniziano con '/'
        command_list = []
        command_list.append(HandlerFunction('insert', self.__insert))
        command_list.append(HandlerFunction('delete', self.__delete))

        self.__register_function(command_list)

        # Aggiungo un handler che ripete tutto
        # echo_handler = MessageHandler(Filters.text & (~Filters.command), self.__echo)
        # self.__dispatcher.add_handler(echo_handler)
        unknown_handler = MessageHandler(Filters.command, self.__unknown)
        self.__dispatcher.add_handler(unknown_handler)
        generic_handler = MessageHandler(Filters.text & (~Filters.command), self.__genericHandler)
        self.__dispatcher.add_handler(generic_handler)
        self.__dispatcher.add_handler(CallbackQueryHandler(self.__genericButton))
        updater.start_polling()

    def __initVariables(self):
        for id in self.__enabled_users:
            self.__cleanVariables(id)

    def __cleanVariables(self, id: int):
        self.__step[id] = 0
        self.__userdata[id] = []
        self.__handler[id] = lambda *args: None

    def __register_function(self, functions: list):
        for function in functions:
            if type(function) is not HandlerFunction:
                raise Exception('[ERROR] __register_function take a list of HandlerFunction objects.')
            # Aggiungo gli handler
            self.__dispatcher.add_handler(CommandHandler(function.name, function.callback))

    def __genericHandler(self, update, context):
        print('IO SONO FORTE')
        id = update.message.from_user['id']
        self.__handler[id](update, context)
        # if self.__handler[id] is not None:
        #     self.__handler[id](update, context)
        # else:
        #     print('L\'handler è None')

    def __insertHandler(self, update, context):
        print("=== INSERT ===")
        id = update.message.from_user['id']
        message = update.message.text
        if id in self.__enabled_users:
            if self.__step[id] == 1:
                self.__userdata[id].append(message)
                txt = "Inserisci il nome del prodotto"
                self.__send_message(update, context, txt, id)
                print(self.__userdata[id])
                self.__step[id] = 2
            elif self.__step[id] == 2:
                self.__userdata[id].append(message)
                print(self.__userdata[id])
                self.__insertintofile(id)
                self.__cleanVariables(id)
                self.__send_message(update, context, "Prodotto inserito correttamente.", id)

    def __insertintofile(self, id):
        input_file = "files/" + self.__userdata[id][0] + "_product_list.txt"
        #print(input_file)
        with open(input_file, "a") as file:
            insertstring = "\n" + self.__userdata[id][1] + "|%!|" + self.__userdata[id][2]
            print(insertstring)
            file.write(insertstring)

    def __genericButton(self, update: Update, context: CallbackContext):
        id = update.callback_query.message.chat.id
        if self.__handler[id] == self.__insertHandler:
            self.__buttonInsert(update, context)
        elif self.__handler[id] == self.__buttonRemove:
            self.__buttonRemove(update, context)

    def __buttonInsert(self, update: Update, context: CallbackContext) -> None:
        id = update.callback_query.message.chat.id
        self.__step[id] = 1
        query = update.callback_query
        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        query.answer()
        self.__userdata[id].append(query.data)
        print(self.__userdata[id])
        query.edit_message_text(text="Inserisci l'url di {}".format(query.data))

    def __buttonRemove(self, update: Update, context: CallbackContext):
        id = update.callback_query.message.chat.id
        query = update.callback_query
        if self.__step[id] == 0:
            # CallbackQueries need to be answered, even if no notification to the user is needed
            # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
            input_file = "files/" + query.data + "_product_list.txt"

            prodotti = FileUtility.readFromFile(input_file)

            reply_markup = InlineKeyboardMarkup(self.__format_keyboard(prodotti, 2))

            bot = context.bot
            bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="Selezionare il prodotto da rimuovere:",
                reply_markup=reply_markup
            )

            #query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(reply_markup))
            #self.__last_message[id].reply_text('Selezionare il prodotto da rimuovere:', reply_markup=reply_markup)
            query.answer()
            self.__userdata[id].append(input_file)
            self.__step[id] = 1
        elif self.__step[id] == 1:
            FileUtility.deleteFromFile(self.__userdata[id][0], query.data)
            query.answer()
            bot = context.bot
            bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="Prodotto eliminato con successo"
            )
            self.__cleanVariables(id)

    def __format_keyboard(self, prodotti, num_elements) -> list:
        keyboard = []

        # Aggiungo i prodotti nella lista a tre alla volta
        element = 0
        tmp_list = []
        for prodotto in prodotti:
            tmp_list.append(InlineKeyboardButton(prodotto.nome, callback_data=prodotto.url))
            element += 1
            if element == num_elements:
                keyboard.append(tmp_list)
                tmp_list = []
                element = 0

        if tmp_list.__len__() != 0:
            keyboard.append(tmp_list)

        return keyboard

    def __insert(self, update, context):
        id = update.message.from_user['id']
        if id in self.__enabled_users:
            self.__handler[id] = self.__insertHandler
            self.__userdata[id] = []
            self.__step[id] = 0
            #self.__send_message(update, context, text="Selezionare l'ecommerce", chat_id=id)
            keyboard = [
                [
                    InlineKeyboardButton("Amazon", callback_data='amazon'),
                    InlineKeyboardButton("Eprice", callback_data='eprice'),
                ],
                [InlineKeyboardButton("Mediaworld", callback_data='mediaworld')],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Selezionare l\'ecommerce:', reply_markup=reply_markup)

    def __delete(self, update, context):
        id = update.message.from_user['id']
        if id in self.__enabled_users:
            self.__handler[id] = self.__buttonRemove
            self.__userdata[id] = []
            self.__step[id] = 0
            # self.__send_message(update, context, text="Selezionare l'ecommerce", chat_id=id)
            keyboard = [
                [
                    InlineKeyboardButton("Amazon", callback_data='amazon'),
                    InlineKeyboardButton("Eprice", callback_data='eprice'),
                ],
                [InlineKeyboardButton("Mediaworld", callback_data='mediaworld')],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Selezionare l\'ecommerce da rimuovere:', reply_markup=reply_markup)

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
            product_list = self.__scraper_helper.screap_from_file2(scraper, 'amazon_scraper\\amazon_multiple_product_list.txt', selector='multiple')
            product_list = self.__scraper_helper.get_multiple_offers(product_list)
            print('SIZE:', product_list.__len__())
            for product in product_list:
                info_string = self.__scraper_helper.get_info_string(product, product['discount'])
                self.__send_message(update, context, info_string, chat_id=self.__GROUP_ID)
                print('INFO:', info_string)

        self.__send_message(update, context, 'Products sended')

    def __unknown(self, update, context):
        self.__send_message(update, context, 'Sorry, I didn\'t understand that command.')


if __name__ == '__main__':
    bot = Bot("1466924804:AAH9TTIz-jwPi0bqDBmAICA-Oygqx9gxr8Y")
    bot.start_bot()
