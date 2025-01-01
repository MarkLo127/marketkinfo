import yfinance as yf  # 股票數據
import pandas as pd  # 資料處理
import streamlit as st  # Streamlit 模組


# 6.期權數據
class Option:
    def __init__(self, symbol):
        self.symbol = symbol
        self.tran_dict = {
            "contractSymbol": " ",
            "lastTradeDate": "最後交易日期",
            "strike": "行使價",
            "lastPrice": "最後價格",
            "bid": "賣出價格",
            "ask": "買入價格",
            "change": "變動",
            "percentChange": "百分比變動",
            "volume": "交易量",
            "openInterest": "未平倉量",
            "impliedVolatility": "隱含波動率",
            "inTheMoney": "實值",
            "contractSize": "合約大小",
            "currency": "貨幣",
        }

    def get_option_dates(self):
        stock = yf.Ticker(self.symbol)
        return stock.options

    def options_calls_date(self, date):
        stock = yf.Ticker(self.symbol)
        option_chain = stock.option_chain(date)
        return option_chain.calls

    def options_puts_date(self, date):
        stock = yf.Ticker(self.symbol)
        option_chain = stock.option_chain(date)
        return option_chain.puts

    def tran_col(self, df):
        """Translate DataFrame column names to Chinese."""
        df.rename(columns=self.tran_dict, inplace=True)
        return df
