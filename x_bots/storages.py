import gspread
from os import path
from gspread_dataframe import get_as_dataframe

class IStorage:
    # сощраняет лог о сообщении к боту
    def save(self, user_id, username, first_name,
             last_name, msg_id, text, answer):
        pass


    # передаём бота-ответчика и запрос к нему, возвращает (ответ, вероятность)
    def answer(self, responder, text):
        return "", False


class GSpreadStorage(IStorage):
    def __init__(self):
        try:
            # достаём файл конфигурации таблицы из домашней директории
            filename = path.join(path.expanduser('~'), '.tgbot/gs.json')
            gc = gspread.service_account(filename=filename)

            self.logs = gc.open("BotTable").worksheet('Logs')
            self.answers = gc.open("BotTable").worksheet('Answers')
        except Exception as e:
            raise Exception('Невозможно загрузить конфин google таблицы: ' + e)


    def save(self, user_id, username, first_name,
             last_name, msg_id, text, answer):

        self.logs.append_row([
            user_id, username, first_name, last_name, msg_id, text, answer
        ], value_input_option="USER_ENTERED")


    # обёртка над responder, но на основе хранилища
    def answer(self, responder, text):
        df = get_as_dataframe(self.answers)
        df = df[df['Context'].notna()]
        df.reset_index(inplace=True)
        df = df[['Context', 'Text Response']]
        responder.prepare(df)
        ans, prob = responder.answer(text)
        return ans, prob

    def add_answer(self, context, answer):
        self.answers.append_row([
            context, answer
        ], value_input_option="USER_ENTERED")