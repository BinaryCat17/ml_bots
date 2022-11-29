import pandas as pd
from os import path

import context as c
from x_bots.responders import DefaultResponder
from x_bots.bots import TelegramBot, IBotListener

class SupportListener(IBotListener):
    def __init__(self, df):
        self.responder = DefaultResponder()
        self.responder.prepare(df)

    def listen_user(self, bot, user_id, username, first_name, last_name, msg_id, text):
        res, prob = self.responder.answer(text)
        return res


if __name__ == "__main__":
    answers_path = path.join(c.DATA_PATH, 'dialog_talk_agent.xlsx')
    df = pd.read_excel(answers_path)

    bot = TelegramBot()
    bot.run(SupportListener(df))