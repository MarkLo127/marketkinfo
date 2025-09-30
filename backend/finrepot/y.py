# 資料分析
import pandas as pd  # 資料處理

# 資料擷取與網路相關
import yfinance as yf  # 股票數據

# 翻譯
from deep_translator import GoogleTranslator
import concurrent.futures

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

# 4.公司財報
# 年報
class financialreport_y:
    def __init__(self, symbol, target_language="zh-TW"):
        self.symbol = symbol
        self.target_language = target_language
        self.balance_sheet = None
        self.income_stmt = None
        self.cash_flow = None

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

    # 處理重複的列名
    def remove_col(self, df):
        cols = pd.Series(df.columns)
        if cols.duplicated().any():
            cols += "_" + cols.groupby(cols).cumcount().astype(str)
            df.columns = cols
        return df

    # 獲取財務報表
    def get_financial(self):
        try:
            stock = yf.Ticker(self.symbol)
            self.balance_sheet = stock.balance_sheet
            self.income_stmt = stock.income_stmt
            self.cash_flow = stock.cashflow
        except Exception as e:
            st.error(f"獲取財務報表發生錯誤：{str(e)}")
            self.balance_sheet, self.income_stmt, self.cash_flow = None, None, None

    # 翻譯財務報表
    def tran_financial(self):
        self.balance_sheet = self.tran_df(self.balance_sheet)
        self.income_stmt = self.tran_df(self.income_stmt)
        self.cash_flow = self.tran_df(self.cash_flow)

    # 顯示財務報表
    def display_financial(self):
        st.subheader(f"{self.symbol}-資產負債表/年")
        st.dataframe(self.balance_sheet)
        
        st.subheader(f"{self.symbol}-綜合損益表/年")
        st.dataframe(self.income_stmt)

        st.subheader(f"{self.symbol}-現金流量表/年")
        st.dataframe(self.cash_flow)