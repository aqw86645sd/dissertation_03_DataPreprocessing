

import pymongo


class Entrance:
    def __init__(self):
        self.dictionary_size = 3000  # 字典大小

        self.p_start_date = '2022-01-01'
        self.p_end_date = '2022-06-30'

        """ DB setting """
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.coll_analyze_dictionary = self.client['python_getStockNews']['analyze_dictionary']

    def run(self):
        pass

    @staticmethod
    def get_etf_ticker_list(etf_symbol):
        pass


if __name__ == '__main__':
    execute = Entrance()
    execute.run()

    """ 製作字典 """
    # 參考 03_NLTK_ngrams_analyze.ipynb

    """ 抓出句子相關資訊（平均長度、每日平均數） """
    # 參考 04_check_sentence_data.ipynb

    """ 抓出股票行情資料 """
    # 參考 05_insert_analyze_ticker.ipynb

    """ 抓出股票漲跌資料 """
    # 參考 07_knowledge_all.ipynb


