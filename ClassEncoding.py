from Entrance import Entrance


class ClassEncoding(Entrance):
    def __init__(self):
        super().__init__()
        """
        使用 Entrance 的 __init__
        """
        print('執行 ClassEncoding start')

    def run(self):

        # delete old data
        self.coll_analyze_news_encoding.drop()

        # 字典
        dictionary_json = list(self.coll_analyze_dictionary_filter.find())[0]['word_json']

        for p_ticker in self.ticker_list:

            key = {'source': 'Zacks', 'ticker': p_ticker}

            # 新聞
            analyze_news_list = list(self.coll_analyze_news.find(key))

            for news_data in analyze_news_list:
                news_sentence_list = news_data['news_sentence_list']
                news_encoding_list = []

                for word in news_sentence_list:
                    if word in dictionary_json:
                        # 字典 mapping
                        news_encoding_list.append(dictionary_json[word]['index'])

                input_layout = {
                    'sequence': news_data['sequence'],
                    'news_encoding_list': news_encoding_list
                }

                if len(news_encoding_list) == 0:
                    pass
                else:
                    self.coll_analyze_news_encoding.insert_one(input_layout)

        print('執行 ClassEncoding end')
