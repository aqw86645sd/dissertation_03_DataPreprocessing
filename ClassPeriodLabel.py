from Entrance import Entrance
import yfinance as yf
import re
import requests


class ClassPeriodLabel(Entrance):
    def __init__(self):
        super().__init__()
        """
        使用 Entrance 的 __init__
        """
        print('執行 ClassPeriodLabel start')

    def run(self):
        # clean old data
        self.coll_analyze_period.drop()

        ticker_list = self.get_ticker_list()

        # append VIXY
        ticker_list.append('VIXY')

        for p_ticker in ticker_list:
            label_json = self.get_period(p_ticker)

            """ 知識庫 """

            input_layout = {
                'ticker': p_ticker,
                'start_date': self.p_start_date,
                'end_date': self.p_end_date,
                'period': label_json
            }

            self.coll_analyze_period.insert_one(input_layout)

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

    def get_period(self, p_ticker):
        """ ticker 股價資料 """
        ticker_yahoo_data = yf.Ticker(p_ticker.replace('.', '-'))
        ticker_period_data = ticker_yahoo_data.history(start=self.p_start_date, end=self.p_end_date)  # 自訂區間

        date_list = ticker_period_data.index.tolist()
        close_data_list = ticker_period_data.Close

        # avg5
        avg5_list = close_data_list.rolling(5).mean()
        # avg20
        avg20_list = close_data_list.rolling(20).mean()

        # 漲跌資料 0:跌, 1:漲
        label_json = {}

        for date in date_list:
            date_str = str(date)[0:10]
            if avg5_list[date] > avg20_list[date]:
                label_json[date_str] = 1
            else:
                label_json[date_str] = 0

        return label_json
