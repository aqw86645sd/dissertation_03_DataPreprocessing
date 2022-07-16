import pymongo


class Entrance:
    def __init__(self):
        """ 控制是否執行該功能 """
        self.is_analyze_dictionary = False  # 製作字典
        self.is_analyze_ticker = False  # 行情資料
        self.is_analyze_period = False  # 漲跌區間
        self.is_analyze_combinations = True  # 句子組合

        """ parameter """
        self.p_start_date = '2022-02-19'
        self.p_end_date = '2022-02-28'
        self.ticker_list = ['AAPL']
        self.dictionary_size = 3000  # 字典大小

        """ DB setting """
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.coll_analyze_news = self.client['python_getStockNews']['analyze_news']
        self.coll_analyze_ticker = self.client['python_getStockNews']['analyze_ticker']
        self.coll_analyze_period = self.client['python_getStockNews']['analyze_period']
        self.coll_analyze_dictionary = self.client['python_getStockNews']['analyze_dictionary']
        self.coll_analyze_combinations = self.client['python_getStockNews']['analyze_combinations']

        """ 檔案存放位置 """
        self.combination_file_path = '/Volumes/P2/School/Train_Data/Combination_Sequence/'

    def run(self):
        """ 製作字典 (analyze_dictionary) """
        # 參考 03_NLTK_ngrams_analyze.ipynb

        """ 抓出句子相關資訊（平均長度、每日平均數） """
        # 參考 04_check_sentence_data.ipynb

        """ 抓出股票行情資料 (analyze_ticker) """
        # 參考 05_insert_analyze_ticker.ipynb

        """ 抓出股票漲跌區間 (analyze_period) """
        # 參考 06_knowledge_all.ipynb

        """ 每三日的新聞句子組合並使用股票漲跌區間判斷LABEL (analyze_combinations) """
        # 參考 07_insert_analyze_combination.ipynb
        if self.is_analyze_combinations:
            from ClassCombinations import ClassCombinations
            combination = ClassCombinations()
            combination.run()

    @staticmethod
    def get_etf_ticker_list(etf_symbol):
        pass


if __name__ == '__main__':
    execute = Entrance()
    execute.run()
