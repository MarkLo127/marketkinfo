# 資料分析
import pandas as pd  # 資料處理

# 資料擷取與網路相關
import yfinance as yf  # 股票數據

# 翻譯
from deep_translator import GoogleTranslator
import concurrent.futures

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

# 季報
class financialreport_q:
    def __init__(self, symbol, target_language="zh-TW"):
        self.symbol = symbol
        self.target_language = target_language
        self.quarterly_balancesheet = None
        self.quarterly_incomestmt = None
        self.quarterly_cashflow = None

    # 多進程翻譯函數
    def tran(self, texts):
        translator = GoogleTranslator(source="en", target=self.target_language)
        # 使用多進程進行批量翻譯
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tran = list(executor.map(translator.translate, texts))
        return tran

    # 使用多進程翻譯DataFrame的列名和索引名
    def tran_df(self, df):
        if df is not None and not df.empty:
            # 多進程翻譯列名
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = pd.MultiIndex.from_tuples(
                    [
                        tuple(self.tran([str(col) for col in level]))
                        for level in df.columns.levels
                    ]
                )
            else:
                df.columns = self.tran([str(col) for col in df.columns])

            # 多進程翻譯索引名
            if isinstance(df.index, pd.MultiIndex):
                df.index = pd.MultiIndex.from_tuples(
                    [
                        tuple(self.tran([str(idx) for idx in level]))
                        for level in df.index.levels
                    ]
                )
            else:
                df.index = self.tran([str(idx) for idx in df.index])

            # 處理重複的列名
            df = self.remove_col(df)

        return df

    # 處理重複列名
    def remove_col(self, df):
        cols = pd.Series(df.columns)
        if cols.duplicated().any():
            cols += "_" + cols.groupby(cols).cumcount().astype(str)
            df.columns = cols
        return df

    # 獲取季度財務報表
    def get_financial_q(self):
        try:
            stock = yf.Ticker(self.symbol)
            self.quarterly_balancesheet = stock.quarterly_balancesheet
            self.quarterly_incomestmt = stock.quarterly_incomestmt
            self.quarterly_cashflow = stock.quarterly_cashflow
        except Exception as e:
            st.error(f"獲取財務報表發生錯誤：{str(e)}")
            (
                self.quarterly_balancesheet,
                self.quarterly_incomestmt,
                self.quarterly_cashflow,
            ) = (None, None, None)

    # 翻譯季度財務報表
    def tran_financial_q(self):
        if self.quarterly_balancesheet is not None:
            self.quarterly_balancesheet = self.tran_df(self.quarterly_balancesheet)
        if self.quarterly_incomestmt is not None:
            self.quarterly_incomestmt = self.tran_df(
                self.quarterly_incomestmt
            )
        if self.quarterly_cashflow is not None:
            self.quarterly_cashflow = self.tran_df(self.quarterly_cashflow)

    # 顯示季度財務報表
    def display_financial_q(self):
        st.subheader(f"{self.symbol}-資產負債表/季")
        st.dataframe(self.quarterly_balancesheet)

        st.subheader(f"{self.symbol}-綜合損益表/季")
        st.dataframe(self.quarterly_incomestmt)

        st.subheader(f"{self.symbol}-現金流量表/季")
        st.dataframe(self.quarterly_cashflow)