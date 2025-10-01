# 資料分析
import pandas as pd  # 資料處理

# 資料擷取與網路相關
import yfinance as yf  # 股票數據
from finvizfinance.quote import finvizfinance
import requests as res  # HTTP 請求
from bs4 import BeautifulSoup  # 網頁解析

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

# 9.相關新聞
class News:
    def getnews(self, symbol):
        url = f"https://finviz.com/quote.ashx?t={symbol}&p=d"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # 發送請求並處理可能的錯誤
        try:
            response = res.get(url, headers=headers)
            response.raise_for_status()  # 確保請求成功
        except res.exceptions.RequestException as e:
            st.error(f"無法獲取 {symbol} 相關消息: {e}")
            return None

        # 解析頁面內容
        soup = BeautifulSoup(response.text, "html.parser")

        # 尋找新聞表格
        news_table = soup.find("table", class_="fullview-news-outer")
        if news_table is None:
            st.error(f"無法獲取 {symbol} 相關新聞表格")
            return None

        # 獲取新聞項目
        news_items = news_table.find_all("tr")
        news_data = []

        for news_item in news_items:
            cells = news_item.find_all("td")
            if len(cells) < 2:
                continue

            # 提取新聞的日期和標題
            date_info = cells[0].text.strip()
            news_link = cells[1].find("a", class_="tab-link-news")

            if news_link:
                news_title = news_link.text.strip()
                news_url = news_link["href"]
                news_data.append(
                    {"Date": date_info, "Title": news_title, "URL": news_url}
                )

        return news_data