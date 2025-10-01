# 資料分析
import pandas as pd  # 資料處理

# 資料擷取與網路相關
import yfinance as yf  # 股票數據
from finvizfinance.quote import finvizfinance


# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

# 9.相關新聞
class News:
    def getnews(self, symbol):
        news_data = finvizfinance(symbol).ticker_news()
        return news_data