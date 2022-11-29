import pandas as pd
from os import path

import context as c
from x_bots.responders import DefaultResponder

if __name__ == "__main__":
    answers_path = path.join(c.DATA_PATH, 'dialog_talk_agent.xlsx')
    df = pd.read_excel(answers_path)

    bot = DefaultResponder(use_cosine=False)
    bot.prepare(df)
    
    question = ''
    while question != 'q':
        print('Ask me:')
        question = input()
        print()
        print(bot.answer(question)[0])