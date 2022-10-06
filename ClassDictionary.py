from Entrance import Entrance
import re
import requests
import yfinance as yf


class ClassDictionary(Entrance):
    def __init__(self):
        super().__init__()
        """
        使用 Entrance 的 __init__
        """
        print('執行 ClassDictionary start')

    def run(self):
        # clean old data
        self.coll_analyze_dictionary.drop()
        self.coll_analyze_dictionary_filter.drop()

        news_id_list = []  # 紀錄 news_id

        # 參考 04_1_dictionary_tf-idf.ipynb
        """
        將每個單字都做 TF-IDF

        TF-IDF 做了以下這樣的假設：
        * 一個『詞彙』越常出現在一篇『文件』中，這個『詞彙』越重要
        * 一個『詞彙』越常出現在多篇『文件』中，這個『詞彙』越不重要
        """

        vti_ticker_list = self.get_ticker_list()
        ticker_list = vti_ticker_list[:100]  # 使用前100大標的新聞做字典

        # get txn date
        vixy_yahoo_data = yf.Ticker('VIXY')
        vixy_period_data = vixy_yahoo_data.history(start=self.p_start_date, end=self.p_end_date)
        date_list = [date.strftime('%Y-%m-%d') for date in vixy_period_data.index]

        json_word = {}  # 單字數量

        # layout
        '''
        json_word = {
            cnt  # 單字全部出現次數
            point  # 二維坐標 (漲跌, 成交量) 
            news_id_json：{  # 新聞單字出現分佈 
                news_id：{  # 新聞ID
                    ticker：{  # 標的
                        ticker_cnt  # 在該新聞中標的出現單字次數
                    }
                }
            }
        }
        '''

        for p_ticker in ticker_list:
            print(p_ticker)

            if p_ticker in 'BRK.B':
                # 會錯，先省略
                continue

            # 行情
            ticker_data = list(self.coll_analyze_ticker.find({'ticker': p_ticker}))

            if len(ticker_data) == 0:
                continue

            stock_data = ticker_data[0]['stock_data']

            for p_date in date_list:

                # 只抓 Zacks 的新聞
                sentence_key = {'source': 'Zacks', 'ticker': p_ticker, 'date': p_date}

                # 該日期有出現的句子
                data_sentence_list = list(self.coll_analyze_news.find(sentence_key))

                # 二維座標 (價格漲跌幅, 成交量漲跌幅)
                position = [stock_data[p_date]['deviation_price_original'],
                            stock_data[p_date]['deviation_volume_original']]

                for data_sentence in data_sentence_list:

                    news_id = data_sentence['news_id']

                    if news_id not in news_id_list:
                        news_id_list.append(news_id)

                    for word in data_sentence['news_sentence_list']:

                        if word[:1].isalpha():  # 第一個字為英文

                            if word in json_word:  # 已存在json_word
                                # 抓之前資料
                                cnt = json_word[word]['cnt']
                                point = json_word[word]['point']
                                news_id_json = json_word[word]['news_id_json']

                            else:  # 不存在json_word
                                # init
                                cnt = 0
                                point = []
                                news_id_json = {}

                            cnt += 1  # 單字全部出現次數
                            point.append(position)  # 二維坐標 (漲跌, 成交量)

                            # edit news_id_json data
                            if news_id in news_id_json:
                                if p_ticker not in news_id_json[news_id]:
                                    news_id_json[news_id][p_ticker] = 0
                            else:
                                news_id_json[news_id] = {}
                                news_id_json[news_id][p_ticker] = 0

                            news_id_json[news_id][p_ticker] += 1

                            json_word[word] = {'cnt': cnt, 'point': point, 'news_id_json': news_id_json}

                        else:
                            pass

        # 計算平均
        news_id_cnt = len(news_id_list)  # 全部新聞數（distinct）

        # 平均漲跌百分比
        # 平均成交量百分比
        # 在單一新聞出現多次的頻率：只算有出現過的 news_id 平均次數
        # 在多個新聞出現的平率：每個出現過的 news_id 只算一次 / 全部新聞數量

        # list_json_word = []
        avg_json = {}

        # 計算單字平均數值
        for word in json_word:
            word_data = json_word[word]

            cnt = word_data['cnt']

            sum_price = 0  # 漲跌百分比合計
            sum_volume = 0  # 成交量百分比合計
            abs_sum_price = 0  # 漲跌百分比絕對值合計
            abs_sum_volume = 0  # 成交量百分比絕對值合計

            for point in word_data['point']:
                sum_price += point[0]
                sum_volume += point[1]
                abs_sum_price += abs(point[0])
                abs_sum_volume += abs(point[1])

            word_time_in_same_news = 0

            for news_id in word_data['news_id_json']:
                # 有多個標的要先算出平均
                avg_word_time_in_same_news = 0

                for ticker in word_data['news_id_json'][news_id]:
                    avg_word_time_in_same_news += word_data['news_id_json'][news_id][ticker]

                word_time_in_same_news += avg_word_time_in_same_news

            avg_price = sum_price / cnt  # 平均漲跌百分比
            avg_volume = sum_volume / cnt  # 平均成交量百分比
            avg_abs_price = abs_sum_price / cnt  # 平均絕對值漲跌百分比
            avg_abs_volume = abs_sum_volume / cnt  # 平均絕對值成交量百分比
            tf = word_time_in_same_news / len(
                word_data['news_id_json'])  # 在單一新聞出現多次的頻率：只算有出現過的 news_id 平均次數
            idf = len(word_data['news_id_json']) / news_id_cnt  # 在多個新聞出現的平率：每個出現過的 news_id 只算一次 / 全部新聞數量

            avg_json[word] = {
                'cnt': json_word[word]['cnt'],
                'avg_price': avg_price,
                'avg_volume': avg_volume,
                'avg_abs_price': avg_abs_price,
                'avg_abs_volume': avg_abs_volume,
                'tf': tf,
                'idf': idf
            }

        input_ = {
            'start_date': self.p_start_date,
            'end_date': self.p_end_date,
            'word_json': avg_json
        }
        print('執行 ClassDictionary : insert coll_analyze_dictionary')
        self.coll_analyze_dictionary.insert_one(input_)

        # 參考 04_2_dictionary_filter.ipynb

        dictory = list(self.coll_analyze_dictionary.find())[0]['word_json']

        filter_word_json = {}

        index = 1  # 一定要從1開始，0是要padding時補位的

        for word in dictory:
            if dictory[word]['tf'] < self.p_tf_limit:
                pass
            elif dictory[word]['idf'] > self.p_idf_limit:
                pass
            elif dictory[word]['avg_abs_price'] < self.p_abs_price_limit:
                pass
            elif dictory[word]['avg_abs_volume'] < self.p_abs_price_volume:
                pass
            else:
                input_ = dictory[word]
                input_['index'] = index

                filter_word_json[word] = input_
                index += 1

        dict_input_ = {
            'length': len(filter_word_json),
            'tf_limit': self.p_tf_limit,
            'idf_limit': self.p_idf_limit,
            'abs_price_limit': self.p_abs_price_limit,
            'abs_price_volume': self.p_abs_price_volume,
            'word_json': filter_word_json
        }

        print('執行 ClassDictionary : insert coll_analyze_dictionary_filter')
        self.coll_analyze_dictionary_filter.insert_one(dict_input_)

        print('執行 ClassDictionary end')

    @staticmethod
    def get_ticker_list():
        """ getting holdings data from Zacks for the given ticker """
        url = "https://www.zacks.com/funds/etf/VOO/holding"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
        }

        with requests.Session() as req:
            req.headers.update(headers)
            r = req.get(url)
            tickerList = re.findall(r'etf\\\/(.*?)\\', r.text)

        return tickerList
