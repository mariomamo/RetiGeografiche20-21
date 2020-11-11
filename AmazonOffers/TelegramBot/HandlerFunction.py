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
