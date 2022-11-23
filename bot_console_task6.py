import pandas as pd
import re
import nltk
import sklearn
import numpy as np

class Bot:
    _stopwords = nltk.corpus.stopwords.words('english')

    def __init__(self, file):
        self.cv = sklearn.feature_extraction.text.CountVectorizer()

        df = pd.read_excel(file)
        df.ffill(axis=0, inplace=True)
        df['Context'] = df['Context'].apply(Bot._prepare_sentence)
        df['Context'] = df['Context'].apply(Bot._normalize_sentence)
        df['Context'] = df['Context'].apply(Bot._remove_stops)

        self.df = df
        self.df_bow = self._make_vectors(df['Context'])


    def answer(self, question, use_cosine = True):
        question = Bot._prepare_sentence(question)
        question = Bot._normalize_sentence(question)
        question = Bot._remove_stops(question)

        Q_bow = self.cv.transform([question]).toarray()
        if use_cosine:
            cosine_value = 1 - sklearn.metrics.pairwise_distances(self.df_bow, Q_bow, metric='cosine')
            ans_ind = cosine_value.argmax()
        else:
            # количество совпадений слов
            dif = self.df_bow & (self.df_bow == Q_bow)
            dif = dif.sum(axis=1)

            # штраф за все несовпадающие слова
            dif = dif - (self.df_bow != Q_bow).sum(axis=1)
            
            ans_ind = dif.argmax()
            
        ans = self.df['Text Response'].loc[ans_ind]
        return ans

    def _prepare_sentence(sent):
        sent = str(sent).lower()
        sent = re.sub(r'[^a-z0-9]', ' ', sent)
        return sent

    def _normalize_sentence(sent):
        tokens = nltk.word_tokenize(sent)
        tags = nltk.pos_tag(tokens)
        lem_list = []
        lemm = nltk.WordNetLemmatizer()

        for word, tag in tags:
            pos_val = Bot._convert_ps(tag)
            lemm_token = lemm.lemmatize(word, pos_val)
            lem_list.append(lemm_token)

        return ' '.join(lem_list)
    
    def _remove_stops(sent):
        tokens = nltk.word_tokenize(sent)
        tokens = [t for t in tokens if t not in Bot._stopwords]
        return ' '.join(tokens)

    def _convert_ps(ps):
        if ps in ['NN', 'NNS', 'NNP']:
            return 'n'
        elif ps in ['JJ', 'JJR', 'JJS']:
            return 'a'
        elif ps in ['VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            return 'v'
        elif ps in ['RB', 'RBR', 'RBS']:
            return 'r'
        else:
            return 'n'
    
    def _make_vectors(self, sents):
        X = self.cv.fit_transform(sents).toarray()
        features = self.cv.get_feature_names_out()
        return pd.DataFrame(X, columns=features)

if __name__ == "__main__":
    bot = Bot('dialog_talk_agent.xlsx')
    question = ''
    while question != 'q':
        print('Ask me:')
        question = input()
        print()
        print(bot.answer(question, False))