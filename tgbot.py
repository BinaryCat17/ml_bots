import telebot
from bot_console_task6 import Bot
from os import path

cmd_bot = Bot('dialog_talk_agent.xlsx')

try:
    userhome = path.expanduser('~')
    token_file = open(path.join(userhome, '.tgbot/token.txt'))
    bot = telebot.TeleBot(token_file.read())
    token_file.close()
except Exception as e:
    print('Невозможно запустить бота, проверьте файл конфигурации:', e)
    exit()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda message: True)
def echo_all(message): 
    print(message.text)
    res = cmd_bot.answer(message.text, False)
    print(res)
    bot.reply_to(message, res)

bot.infinity_polling()