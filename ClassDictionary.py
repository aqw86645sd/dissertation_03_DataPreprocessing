from Entrance import Entrance
import nltk
from collections import Counter
from nltk.util import ngrams


class ClassDictionary(Entrance):
    def __init__(self):
        super().__init__()
        """
        使用 Entrance 的 __init__
        """
        print('執行 ClassDictionary start')
        self.coll_original_Zacks = self.client['python_getStockNews']['original_Zacks']
        self.coll_original_SeekingAlpha = self.client['python_getStockNews']['original_SeekingAlpha']

    def run(self):
        text_Zacks = ""
        text_SeekingAlpha = ""

        """ 將 Zacks 全部資料都合成一筆字串 """
        db_data_Zacks = self.coll_original_Zacks.find()
        news_data_list_Zacks = [row_data for row_data in db_data_Zacks]
        for news_data in news_data_list_Zacks:
            text_Zacks += news_data["content"]

        """ 將 SeekingAlpha 全部資料都合成一筆字串 """
        # db_data_SeekingAlpha = self.coll_original_SeekingAlpha.find()
        # news_data_list_SeekingAlpha = [row_data for row_data in db_data_SeekingAlpha]
        # for news_data in news_data_list_SeekingAlpha:
        #     soup = BeautifulSoup(news_data["content"], "html.parser")
        #     text_SeekingAlpha += soup.text

        text = text_Zacks + text_SeekingAlpha
        print('執行 ClassDictionary : text')

        # 去掉無意義詞彙
        text = self.replace_special_word(text)
        print('執行 ClassDictionary : 去掉無意義詞彙')

        # 轉小寫
        text = text.lower()
        print('執行 ClassDictionary : 轉小寫')

        # Word Segmentation (斷詞)
        token_list = nltk.tokenize.word_tokenize(text)
        print('執行 ClassDictionary : 斷詞')

        # POS (詞性標記)
        pos_list = nltk.pos_tag(token_list)
        print('執行 ClassDictionary : 詞性標記')

        # Lemmatization (字型還原）
        lemmatization_list = [self.lemmatize_by_pos(token, pos) for token, pos in pos_list]
        print('執行 ClassDictionary : 字型還原')

        # clean old data
        self.coll_analyze_dictionary.drop()
        print('執行 ClassDictionary : clean')

        news_unigrams = ngrams(lemmatization_list, 1)
        news_unigrams_freq = Counter(news_unigrams)
        dictionary = news_unigrams_freq.most_common(self.dictionary_size)
        print('執行 ClassDictionary : unigrams')

        d_index = 0  # 字典對應的數值
        dictionary_json = {}

        input_layout = {
            'top_number': self.dictionary_size,
            'dictionary_json': {}
        }

        for d in dictionary:
            dictionary_json[d[0][0]] = d_index
            d_index += 1

        input_layout['dictionary_json'] = dictionary_json

        self.coll_analyze_dictionary.insert_one(input_layout)
        print('執行 ClassDictionary end')

    @staticmethod
    def replace_special_word(text):
        # 特殊字元會造成分詞誤判時，先修改成特定字元
        text = text.replace("'s", "")
        text = text.replace("’s", "")

        # 去掉符號
        # text = text.replace("'", "")
        # text = text.replace("’", "")
        # text = text.replace("`", "")
        # text = text.replace(".", "")
        # text = text.replace(",", "")
        # text = text.replace("$", "")
        # text = text.replace("%", "")
        # text = text.replace("#", "")
        # text = text.replace("!", "")
        # text = text.replace("&", "")
        # text = text.replace(":", "")
        # text = text.replace(";", "")
        # text = text.replace("?", "")
        # text = text.replace("|", "")
        # text = text.replace("~", "")
        # text = text.replace("+", "")
        # text = text.replace("-", "")
        # text = text.replace("*", "")
        # text = text.replace("/", "")
        # text = text.replace("{", "")
        # text = text.replace("}", "")
        # text = text.replace("[", "")
        # text = text.replace("]", "")
        # text = text.replace("(", "")
        # text = text.replace(")", "")

        # 去掉數字
        text = text.replace("1", "")
        text = text.replace("2", "")
        text = text.replace("3", "")
        text = text.replace("4", "")
        text = text.replace("5", "")
        text = text.replace("6", "")
        text = text.replace("7", "")
        text = text.replace("8", "")
        text = text.replace("9", "")
        text = text.replace("0", "")

        # text = re.sub("[^a-zA-z0-9\s]", " ", text)

        return text

    @staticmethod
    def lemmatize_by_pos(word, pos):
        """
        字型還原
        :param word: 單字
        :param pos: 詞性
        :return:
        """
        lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

        if pos.startswith('J'):
            return lemmatizer.lemmatize(word, 'a')
        elif pos.startswith('V'):
            return lemmatizer.lemmatize(word, 'v')
        elif pos.startswith('N'):
            return lemmatizer.lemmatize(word, 'n')
        elif pos.startswith('R'):
            return lemmatizer.lemmatize(word, 'r')
        else:
            return word
