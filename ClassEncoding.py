from Entrance import Entrance

import gc


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
        dictionary_json = self.coll_analyze_dictionary.find_one()['dictionary_json']
        dictionary_key_list = list(dictionary_json)

        # 新聞
        analyze_news_list = list(self.coll_analyze_news.find())

        for news_data in analyze_news_list:
            news_sentence_list = news_data['news_sentence_list']
            news_encoding_list = []

            for word in news_sentence_list:
                if word in dictionary_key_list:
                    # 字典 mapping
                    news_encoding_list.append(dictionary_json[word])

            input_layout = {
                'sequence': news_data['sequence'],
                'news_encoding_list': news_encoding_list
            }

            self.coll_analyze_news_encoding.insert_one(input_layout)

        print('執行 ClassEncoding end')

        """ release memory """
        del dictionary_json  # clean parameter
        del dictionary_key_list  # clean parameter
        del analyze_news_list  # clean parameter
        gc.collect()  # 清除或釋放未引用的記憶體
