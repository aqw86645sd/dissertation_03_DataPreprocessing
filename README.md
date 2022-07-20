# dissertation_03_DataPreprocessing
訓練前的資料預處理


包含：
1. 製作字典 (analyze_dictionary)
2. 抓出股票行情資料 (analyze_ticker)
3. 抓出股票漲跌區間 (analyze_period)
4. 每三日的新聞句子組合並使用股票漲跌區間判斷LABEL (analyze_combinations)
5. 將news句子資料用字典做encoding (analyze_news_encoding)
6. 抓出句子相關資訊（平均長度、每日平均數）



# 環境
## NLTK 安裝
pip3 install nltk

安裝完需安裝 punkt 等其他套件


