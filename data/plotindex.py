import pandas as pd  # 資料處理
import numpy as np  # 資料處理

# 資料擷取與網路相關
import yfinance as yf  # 股票數據

# 畫圖相關
import plotly.graph_objs as go  # Plotly 圖表物件
import plotly.express as px  # Plotly 快速繪圖
from plotly.subplots import make_subplots  # 子圖支援
import plotly  # Plotly 主模組

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

# 1.大盤指數
class plotindex:
    def tran(self):
        return {
            "^IXIC": "NASDAQ",
            "^NDX": "NASDAQ 100",
            "^VIX": "VIX",
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^SOX": "PHLX Semiconductor Sector",
            "^RUT": "Russell 2000",
            "BRK-A": "波克夏海瑟威",
            "^HSI": "恆生指數",
            "^STI": "新加坡海峽指數",
            "^TWII": "加權指數",
            "^N225": "日經指數",
            "399001.SZ": "深證指數",
            "^KS11": "韓國綜合股價指數",
        }

    def __init__(self, period, time, interval, plot_type="index"):
        self.period = period
        self.time = time
        self.interval = interval  # 新增 interval 參數
        self.plot_type = plot_type
        self.symbols = {
            "index": [
                "^IXIC",
                "^NDX",
                "^VIX",
                "^GSPC",
                "^DJI",
                "^SOX",
                "^RUT",
                "BRK-A",
            ],
            "foreign": [
                "^GSPC",
                "^IXIC",
                "^HSI",
                "^STI",
                "^TWII",
                "^N225",
                "399001.SZ",
                "^KS11",
            ],
        }
        self.symbol_names = self.tran()
        self.data = {}

    def fetch_data(self):
        """Fetch historical data for the selected indexes."""
        tickers = self.symbols[self.plot_type]

        try:
            data = yf.download(tickers, period=self.period, interval=self.interval)["Close"]
            for symbol in tickers:
                if symbol in data:
                    self.data[symbol] = data[symbol].dropna()
        except Exception as e:
            st.error(f"Error fetching data: {e}")

    def plot_index(self):
        """Plot the US indexes."""
        st.subheader(f"美股大盤＆中小企業{self.time}走勢")

        # Create Plotly subplot figure for indexes
        fig = make_subplots(
            rows=4,
            cols=2,
            subplot_titles=[
                self.symbol_names[symbol] for symbol in self.symbols["index"]
            ],
        )

        for i, symbol in enumerate(self.symbols["index"]):
            fig.add_trace(
                go.Scatter(
                    x=self.data[symbol].index,
                    y=self.data[symbol].values,
                    mode="lines",
                    name=self.symbol_names[symbol],
                ),
                row=(i // 2) + 1,
                col=(i % 2) + 1,
            )

        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
        with st.expander(f"展開美股大盤＆中小企業{self.time}走勢"):
            data = pd.DataFrame(self.data)
            data = data.rename(columns=self.tran())
            st.dataframe(data)

    def plot_index_vs(self):
        """Plot comparison of US indexes."""
        st.subheader(f"美股大盤＆中小企業{self.time}走勢比較")
        tickers = self.symbols["index"]

        prices = yf.download(tickers, period=self.period, interval=self.interval).dropna()
        prices = np.log(prices["Close"] / prices["Close"].shift(1))
        prices = prices.cumsum()
        prices = (np.exp(prices) - 1) * 100
        prices = prices.reset_index().melt(
            id_vars="Date", var_name="Ticker", value_name="Growth (%)"
        )

        prices["Ticker"] = prices["Ticker"].map(self.symbol_names)
        fig = px.line(prices, x="Date", y="Growth (%)", color="Ticker")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
        with st.expander(f"展開美股大盤＆中小企業{self.time}走勢比較"):
            st.dataframe(prices)

    def plot_foreign(self):
        """Plot the foreign indexes."""
        st.subheader(f"美股大盤＆海外大盤{self.time}走勢")

        fig = make_subplots(
            rows=4,
            cols=2,
            subplot_titles=[
                self.symbol_names[symbol] for symbol in self.symbols["foreign"]
            ],
        )

        for i, symbol in enumerate(self.symbols["foreign"]):
            if symbol in self.data:
                row = (i // 2) + 1
                col = (i % 2) + 1
                fig.add_trace(
                    go.Scatter(
                        x=self.data[symbol].index,
                        y=self.data[symbol].values,
                        mode="lines",
                        name=self.symbol_names[symbol],
                    ),
                    row=row,
                    col=col,
                )

        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
        with st.expander(f"展開美股大盤＆海外大盤{self.time}走勢"):
            data = pd.DataFrame(self.data)
            data = data.rename(columns=self.tran())
            st.dataframe(data)

    def plot_foreign_vs(self):
        """Plot comparison of foreign indexes."""
        st.subheader(f"美股大盤＆海外大盤{self.time}走勢比較")
        tickers = self.symbols["foreign"]

        prices = yf.download(tickers, period=self.period, interval=self.interval).dropna()
        prices = np.log(prices["Close"] / prices["Close"].shift(1))
        prices = prices.cumsum()
        prices = (np.exp(prices) - 1) * 100
        prices = prices.reset_index().melt(
            id_vars="Date", var_name="Ticker", value_name="Growth (%)"
        )

        prices["Ticker"] = prices["Ticker"].map(self.symbol_names)
        fig = px.line(prices, x="Date", y="Growth (%)", color="Ticker")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
        with st.expander(f"展開美股大盤＆海外大盤{self.time}走勢比較"):
            st.dataframe(prices)

    def plot(self):
        """Plot the financial data based on the selected type."""
        self.fetch_data()
        if self.plot_type == "index":
            self.plot_index()
            self.plot_index_vs()
        elif self.plot_type == "foreign":
            self.plot_foreign()
            self.plot_foreign_vs()
