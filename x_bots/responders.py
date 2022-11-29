import pandas as pd
import re
import nltk
import sklearn

# Пример интерфейса для ответчика
class IResponder:
    # df - датафрейм, имеющий колонки 'Context' и 'Text Response'
    def prepare(self, df):
        pass

    # question - любой вопрос в виде строки
    # возвращает (ответ, вероятность)
    def answer(self, question):
        return ""
    

# Стандартный ответчик на основе nltk и sklearn
class DefaultResponder(IResponder):
    _stopwords = nltk.corpus.stopwords.words('english')

    def __init__(self, use_cosine = True):
        self.use_cosine = use_cosine
   
    def prepare(self, df):
        self.cv = sklearn.feature_extraction.text.CountVectorizer()

        df.ffill(axis=0, inplace=True)
        df['Context'] = df['Context'].apply(DefaultResponder._prepare_sentence)
        df['Context'] = df['Context'].apply(DefaultResponder._normalize_sentence)
        df['Context'] = df['Context'].apply(DefaultResponder._remove_stops)

        self.df = df
        self.df_bow = self._make_vectors(df['Context'])
    

    def answer(self, question):
        question = DefaultResponder._prepare_sentence(question)
        question = DefaultResponder._normalize_sentence(question)
        question = DefaultResponder._remove_stops(question)

        Q_bow = self.cv.transform([question]).toarray()
        ans_prob = 1
        
        # считаем косинусное расстояние
        if self.use_cosine:
            cosine_value = 1 - sklearn.metrics.pairwise_distances(self.df_bow, Q_bow, metric='cosine')
            ans_ind = cosine_value.argmax()
            ans_prob = cosine_value[cosine_value.argmax()]

         # выбираем по наибольшему количеству совпадающих слов
        else:
            dif = self.df_bow & (self.df_bow == Q_bow)
            dif = dif.sum(axis=1)

            # штраф за все несовпадающие слова
            dif = dif - (self.df_bow != Q_bow).sum(axis=1)
            
            ans_ind = dif.argmax()
            
        ans = self.df['Text Response'].loc[ans_ind]
        return ans, ans_prob

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
            pos_val = DefaultResponder._convert_ps(tag)
            lemm_token = lemm.lemmatize(word, pos_val)
            lem_list.append(lemm_token)

        return ' '.join(lem_list)
    
    def _remove_stops(sent):
        tokens = nltk.word_tokenize(sent)
        tokens = [t for t in tokens if t not in DefaultResponder._stopwords]
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

