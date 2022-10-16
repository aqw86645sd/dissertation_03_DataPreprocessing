import pymongo
import gc


class Entrance:
    def __init__(self):
        """ 控制是否執行該功能 """
        self.is_analyze_ticker = False  # 行情資料
        self.is_analyze_dictionary = True  # 製作字典
        self.is_analyze_period = False  # 漲跌區間
        self.is_analyze_combinations = False  # 句子組合sorted
        self.is_analyze_news_encoding = False  # 新聞單字encoding

        """ parameter """
        self.p_start_date = '2022-01-01'
        self.p_end_date = '2022-06-30'
        self.ticker_list = ['AAPL']

        """ dictionary filter """
        self.p_tf_limit = 3  # TF 最小值
        self.p_idf_limit = 0.3  # IDF 最大值
        self.p_abs_price_limit = 2  # 漲跌百分比絕對值平均 最小值
        self.p_abs_price_volume = 2  # 成交量百分比絕對值平均 最小值

        """ DB setting """
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.coll_analyze_news = self.client['python_getStockNews']['analyze_news']
        self.coll_analyze_ticker = self.client['python_getStockNews']['analyze_ticker']
        self.coll_analyze_period = self.client['python_getStockNews']['analyze_period']
        self.coll_analyze_dictionary = self.client['python_getStockNews']['analyze_dictionary']
        self.coll_analyze_dictionary_filter = self.client['python_getStockNews']['analyze_dictionary_filter']
        self.coll_analyze_combinations = self.client['python_getStockNews']['analyze_combinations']
        self.coll_analyze_news_encoding = self.client['python_getStockNews']['analyze_news_encoding']

        """ 檔案存放位置 """
        self.combination_file_path = '/Volumes/P2/School/Train_Data/Combination_Sequence/'

    def run(self):
        """ 抓出股票行情資料 (analyze_ticker) """
        # 參考 03_insert_analyze_ticker.ipynb
        if self.is_analyze_ticker:
            from ClassStockData import ClassStockData
            stockData = ClassStockData()
            stockData.run()

        """ 製作字典 (analyze_dictionary) """
        # 參考 04_1_dictionary_tf-idf.ipynb
        # 參考 04_2_dictionary_filter.ipynb
        if self.is_analyze_dictionary:
            from ClassDictionary import ClassDictionary
            dictionary = ClassDictionary()
            dictionary.run()

            del dictionary
            gc.collect()  # 清除或釋放未引用的記憶體

        """ 抓出股票漲跌區間 (analyze_period) """
        # 參考 05_knowledge_all.ipynb

        """ 每三日的新聞句子組合並使用股票漲跌區間判斷LABEL (analyze_combinations) """
        # 參考 06_insert_analyze_combination.ipynb
        if self.is_analyze_combinations:
            from ClassCombinations import ClassCombinations
            combination = ClassCombinations()
            combination.run()

            del combination
            gc.collect()  # 清除或釋放未引用的記憶體

        """ 將news句子資料用字典做encoding (analyze_news_encoding) """
        # 參考 07_insert_analyze_news_encoding.ipynb
        if self.is_analyze_news_encoding:
            from ClassEncoding import ClassEncoding
            encoding = ClassEncoding()
            encoding.run()

            del encoding
            gc.collect()  # 清除或釋放未引用的記憶體

        """ 抓出句子相關資訊（平均長度、每日平均數） """
        # 參考 08_check_sentence_data.ipynb


if __name__ == '__main__':
    execute = Entrance()
    execute.run()
