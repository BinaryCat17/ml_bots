import telebot
from os import path
import json

# Использую классический ООП подход, вместо декораторов
class IBotListener:
    def welcome(self, bot, user_id, username, first_name,
                last_name, msg_id, text):
        return f'{first_name}, {last_name}, я ваш верный слуга!\nВаш ID - {user_id}'

    # принимаем информацию о сообщении, возвращаем ответ
    def listen_user(self, bot, user_id, username, first_name,
                    last_name, msg_id, text):
        return ""

    def listen_admin_reply(self, bot, username, user_text,
                           admin_username, admin_text):
        return ""


# Любой бот (не только телеграмм, который умеет работать с IListener)
class IBot:
    # Уходит в бесконечный цикл и запускает бота
    def run(self, listener):
        pass


class TelegramBot(IBot):
    def __init__(self):
        try:
            # загружаем конфиг из домашней директории
            # {token: "...", admin: "username"}
            userhome = path.expanduser('~')
            with open(path.join(userhome, '.tgbot/config.json')) as token_file:
                self.cfg = json.load(token_file)
                self.bot = telebot.TeleBot(self.cfg['token'])
        except Exception as e:
            raise Exception(
                'Невозможно запустить бота, проверьте файл конфигурации: ' + e)

    def forward_admin(self, user_id, message_id):
        print(self.cfg['admin'], user_id)
        self.bot.forward_message(self.cfg['admin'], user_id, message_id)

    def run(self, listener):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            ans = listener.welcome(self, *self._parse(message))
            if ans:
                self.bot.reply_to(message, ans)

        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            if (str(message.from_user.id) == self.cfg['admin'] and
               message.reply_to_message is not None):

                rep = message.reply_to_message
                ans = listener.listen_admin_reply(
                    self, rep.from_user.username, rep.text,
                    message.from_user.username, message.text)
                if ans:
                    self.bot.send_message(rep.forward_from.id, ans)
            else:
                ans = listener.listen_user(self, *self._parse(message))
                if ans:
                    self.bot.reply_to(message, ans)

        self.bot.infinity_polling()

    def _parse(self, message):
        user = message.from_user
        return (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            message.message_id,
            message.text)
