import pandas as pd
from os import path

import context as c
from x_bots.responders import DefaultResponder
from x_bots.bots import TelegramBot, IBotListener
from x_bots.storages import GSpreadStorage


class SupportListener(IBotListener):
    def __init__(self):
        self.responder = DefaultResponder()
        self.storage = GSpreadStorage()


    def listen_user(self, bot, user_id, username, first_name, last_name, msg_id, text):
        res, prob = self.storage.answer(self.responder, text)

        ans = "Я не знаю ответа, жду пока придёт на помощь человек..."
        # если вероятность достаточно большая
        if prob > 0.7:
            ans = res
        else:
            bot.forward_admin(user_id, msg_id)

        self.storage.save(user_id, username, first_name,
                          last_name, msg_id, text, ans)
        return ans


    def listen_admin_reply(self, bot, username, user_text,
                           admin_username, admin_text):
        self.storage.add_answer(user_text, admin_text)
        return admin_text


if __name__ == "__main__":
    answers_path = path.join(c.DATA_PATH, 'dialog_talk_agent.xlsx')
    df = pd.read_excel(answers_path)

    bot = TelegramBot()
    bot.run(SupportListener())
