from Entrance import Entrance
import re
import requests
import yfinance as yf
import math


class ClassStockData(Entrance):
    def __init__(self):
        super().__init__()
        """
        使用 Entrance 的 __init__
        """
        print('執行 ClassStockData start')

    def run(self):
        # clean old data
        self.coll_analyze_ticker.drop()

        # voo list
        voo_ticker_list = self.get_ticker_list()

        # 設定抓VOO前多少個ticker
        analyze_ticker_list = voo_ticker_list[:]

        # append VIXY
        analyze_ticker_list.append('VIXY')

        for p_ticker in analyze_ticker_list:
            # ticker data
            ticker_yahoo_data = yf.Ticker(p_ticker.replace('.', '-'))
            ticker_period_data = ticker_yahoo_data.history(start=self.p_start_date, end=self.p_end_date)  # 自訂區間

            date_list = [date.strftime('%Y-%m-%d') for date in ticker_period_data.index]
            close_price_list = ticker_period_data['Close'].tolist()
            volumn_list = ticker_period_data['Volume'].tolist()
            high_list = ticker_period_data['High'].tolist()
            low_list = ticker_period_data['Low'].tolist()

            total_ticker_date_json = {}

            for idx in range(len(date_list)):
                input_json = {}

                label_deviation_price = 0
                label_deviation_volume = 0
                label_deviation_price_original = 0
                label_deviation_volume_original = 0
                ticker_price = close_price_list[idx]
                ticker_volume = volumn_list[idx]

                if idx > 0:
                    # 當日損益百分比區間誤差(1百分比為一區間)
                    deviation_price = (close_price_list[idx] - close_price_list[idx - 1]) / close_price_list[
                        idx - 1] * 100
                    label_deviation_price = self.set_label_value(deviation_price)
                    label_deviation_price_original = round(deviation_price, 2)

                if idx > 3:
                    # 當日成交量與前三日平均成交量變化百分比區間誤差(5百分比為一區間)
                    three_day_average = (volumn_list[idx - 3] + volumn_list[idx - 2] + volumn_list[idx - 1]) / 3
                    deviation_volume = (volumn_list[idx] - three_day_average) / three_day_average * 100 / 5
                    label_deviation_volume = self.set_label_value(deviation_volume)
                    label_deviation_volume_original = round(deviation_volume, 2)

                # 當日最高與最低股價差異百分比區間誤差(1百分比為一區間) ： 只會是正數
                deviation_range = (high_list[idx] - low_list[idx]) / low_list[idx] * 100
                label_deviation_range = self.set_label_value(deviation_range)
                label_deviation_range_original = round(deviation_range, 2)

                input_json['deviation_price'] = label_deviation_price
                input_json['deviation_volume'] = label_deviation_volume
                input_json['deviation_range'] = label_deviation_range
                input_json['deviation_price_original'] = label_deviation_price_original
                input_json['deviation_volume_original'] = label_deviation_volume_original
                input_json['deviation_range_original'] = label_deviation_range_original
                input_json['ticker_price'] = ticker_price
                input_json['ticker_volume'] = ticker_volume

                total_ticker_date_json[date_list[idx]] = input_json

            # input layout : one ticker have one data
            input_layout = {
                'ticker': p_ticker,
                'start_date': self.p_start_date,
                'end_date': self.p_end_date,
                'stock_data': total_ticker_date_json
            }

            self.coll_analyze_ticker.insert_one(input_layout)

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

    @staticmethod
    def set_label_value(input_value):
        """
        設定 label 值
        """
        if input_value > 0:
            # 上取整函數
            return int(math.ceil(input_value))
        elif input_value < 0:
            # 下取整函數
            return int(math.floor(input_value))
        else:
            return 0
