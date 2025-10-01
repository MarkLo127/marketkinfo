import yfinance as yf  # 股票數據
import pandas as pd  # 資料處理
import streamlit as st  # Streamlit 模組


# 7.SEC文件
class secreport:
    def __init__(self, symbol):
        self.symbol = symbol
        self.stock = yf.Ticker(self.symbol)

    def get_sec_filings(self):
        """
        獲取公司的 SEC 文件列表。
        """
        try:
            return self.stock.sec_filings
        except Exception as e:
            st.error(f"獲取 SEC 文件時發生錯誤：{str(e)}")
            return None

    def display_filings(self):
        """
        顯示 SEC 文件列表。
        """
        filings = self.get_sec_filings()  # 呼叫 get_sec_filings 來獲取數據
        if filings is not None and len(filings) > 0:
            # 確保 filings 是 DataFrame，否則將其轉換
            if isinstance(filings, list):
                filings = pd.DataFrame(filings)  # 將列表轉換為 DataFrame
            elif isinstance(filings, dict):
                filings = pd.DataFrame([filings])  # 將 dict 轉換為 DataFrame

            st.subheader(f"{self.symbol}-SEC 文件:")
            st.dataframe(filings)  # 顯示為 DataFrame 表格

            # 展開連結部分
            with st.expander(f"展開 {self.symbol}-SEC 連結"):
                for index, row in filings.iterrows():
                    st.write(
                        f"{row['date']} - [{row['type']}] - [{row['title']}]({row['edgarUrl']})"
                    )
        else:
            st.error(f"無法獲取公司 {self.symbol} 的 SEC 文件。")