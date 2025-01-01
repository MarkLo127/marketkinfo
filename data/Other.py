import yfinance as yf  # 股票數據
import streamlit as st  # Streamlit 模組

#獲利資訊
class Other:
    def __init__(self, symbol):
        self.symbol = symbol
        
    def get_eps(self):
        stock = yf.Ticker(self.symbol)
        eps = stock.earnings_dates
        st.subheader(f"{self.symbol}-獲利資訊")
        st.dataframe(eps)
    
    def get_insider(self):
        stock = yf.Ticker(self.symbol)
        insider_purchases = stock.insider_purchases
        insider_transactions = stock.insider_transactions
        insider_roster_holders = stock.insider_roster_holders
        st.subheader(f"{self.symbol}-內部交易統計")
        st.dataframe(insider_purchases)
        st.subheader(f"{self.symbol}-內部交易")
        st.dataframe(insider_transactions)
        st.subheader(f"{self.symbol}-內部持股")
        st.dataframe(insider_roster_holders)