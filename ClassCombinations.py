from Entrance import Entrance
import threading
import json
import os


class ClassCombinations(Entrance):
    def __init__(self):
        super().__init__()
        """
        使用 Entrance 的 __init__
        """
        print('執行 ClassCombinations start')
        self.max_thread_num = 30  # thread 數量

    def run(self):
        """
            使用 thread
        """
        if not os.path.exists(self.combination_file_path):
            print('檔案存放位置不存在')
            return

        for ticker in self.ticker_list:
            key = {'ticker': ticker}

            # 股價資料
            ticker_data = self.coll_analyze_ticker.find_one(key)

            """ 有值才執行 """
            if ticker_data is not None:
                # 股票資料
                stock_price_json = ticker_data['stock_data']
                # 漲跌資料
                analyze_period = self.coll_analyze_period.find(key)
                period_json = list(analyze_period)[0]['period']

                # 日期
                date_list = list(stock_price_json.keys())
                three_date_list = []  # 將三天組成一個 array 串成 list
                label_list = []
                for idx, date in enumerate(date_list):
                    if self.p_start_date <= date <= self.p_end_date:
                        three_date_list.append([date_list[idx - 2], date_list[idx - 1], date])
                        label_list.append(period_json[date])

                """ 將日期依照 thread 數量分配要執行的日期組合 """
                combination_date_list_list = []
                combination_label_list_list = []
                for m in range(self.max_thread_num):
                    combination_date_list_list.append([])
                    combination_label_list_list.append([])
                for idx, combination_date in enumerate(three_date_list):
                    n = idx % self.max_thread_num
                    combination_date_list_list[n].append(combination_date)
                    combination_label_list_list[n].append(label_list[idx])

                # exec thread
                thread_list = []
                for idx, combination_date_list in enumerate(combination_date_list_list):
                    thread_list.append(threading.Thread(target=self.function_combination_sequence,
                                                        args=(ticker, combination_date_list,
                                                              combination_label_list_list[idx],)))
                    thread_list[idx].start()

                for i in thread_list:
                    i.join()

    def function_combination_sequence(self, ticker, combination_date_list, combination_label_list):
        for idx, combination_date in enumerate(combination_date_list):

            # total news data
            total_news_data_list = []

            # 將全部交易天數新聞資料合併
            for news_date in combination_date:
                news_key = {
                    'ticker': ticker,
                    'source': 'Zacks',
                    'date': news_date
                }

                news_data = self.coll_analyze_news.find(news_key)
                total_news_data_list.extend(list(news_data))

            total_sequence_list = [news['sequence'] for news in total_news_data_list]

            # 檔名要加上路徑
            file_name = self.combination_file_path + ticker + '_' + combination_date[-1] + '.txt'

            """ 執行組合 ＆ 匯出資料 """
            self.combinations_function(len(total_news_data_list), 3, file_name, total_sequence_list,
                                       combination_label_list[idx])

    def combinations_function(self, m, n, file_name, total_sequence_list, label):
        """
            定義：算出m個index中取出n個的組合
        """
        if n > m or m < 4:
            return

        # default values
        total_index = list(range(m))  # 全部的index
        stop_idx_location = -2  # 倒數第幾個index,從這index往前都是停止的
        result = list(range(n))  # 第一個結果
        last_idx = result[-1]  # 最後一個index初始值
        current_times = 1  # 執行第幾個結果

        # print(result)
        self.insert_index_combinations(file_name, result, total_sequence_list, label)

        while True:
            if last_idx < m - 1:
                # 如果最後一個欄位還能向後移動，則移動
                last_idx += 1
                result = result[0:-1]
                result.append(last_idx)
            else:
                # 最後一個欄位已經到最後一個index

                if result[stop_idx_location:] == total_index[stop_idx_location:]:
                    # 固定點後面已經沒有其他組合 or 最後一種組合
                    if result[0] == m - n:
                        # 最後一種組合
                        print(file_name, ', C', m, '取 3, 有', current_times, '種結果, label =', label)
                        print('執行 ClassCombinations end')
                        return
                    else:
                        stop_idx_location -= 1  # 固定點往前
                        result[stop_idx_location] += 1  # 固定點index值加一
                        # 前面有index+1，後方的index(共stop_idx_location*-1-1個)回來緊貼著變動的index
                        for i in reversed(range(1, -stop_idx_location)):
                            result[-i] = result[-i - 1] + 1

                else:
                    for j in range(2, -stop_idx_location + 1):
                        # 由後往前確認是否有空隙
                        if result[-j] + 1 == result[-j + 1]:
                            pass
                        else:
                            result[-j] += 1
                            for k in reversed(range(1, j)):
                                result[-k] = result[-k - 1] + 1

                            break  # 停止檢查

            last_idx = result[-1]
            current_times += 1
            # print(result, current_times)
            self.insert_index_combinations(file_name, result, total_sequence_list, label)

    @staticmethod
    def insert_index_combinations(file_name, index_list, total_sequence_list, label):
        """
        將資料存在檔案裡
        :param file_name: 檔案名稱
        :param index_list: 組合算出來的index組合排序
        :param total_sequence_list: 三天新聞的總seq
        :param label: 最後一天的label
        :return:
        """
        with open(file_name, 'a') as f:
            input_layout = {
                'sequence_combinations': [total_sequence_list[i] for i in index_list],
                'label': label
            }

            json_str = json.dumps(input_layout)

            f.write(json_str + '\n')
