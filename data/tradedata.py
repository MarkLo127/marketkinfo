# 資料分析
import pandas as pd  # 資料處理

# 資料擷取與網路相關
import yfinance as yf  # 股票數據

# 畫圖相關
import plotly.graph_objs as go  # Plotly 圖表物件
import plotly.express as px  # Plotly 快速繪圖
from plotly.subplots import make_subplots  # 子圖支援
import plotly  # Plotly 主模組

# 財務技術分析
from ta.trend import MACD  # MACD 技術指標
from ta.momentum import StochasticOscillator, RSIIndicator  # 隨機震盪與 RSI 技術指標

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

# 5.交易數據
class tradedata:

    @staticmethod
    def getdata(symbol, time_range):
        """根據時間範圍下載股票數據。"""
        stock_data = yf.Ticker(symbol)
        stock_data = stock_data.history(period=time_range)
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.droplevel(1)  # 移除 'NVDA' 層級
        return stock_data

    @staticmethod
    def get_data_time_range(symbol, start, end):
        """根據開始和結束日期下載股票數據。"""
        stock_data = yf.download(symbol, start=start, end=end,auto_adjust=False,progress=False)
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.droplevel(1)  # 移除 'NVDA' 層級
        return stock_data

    @staticmethod
    def calculate_difference(stock_data, period_days):
        """計算最新價格與指定天數前的價格差異。"""
        latest_price = stock_data.iloc[-1]["Close"]
        previous_price = (
            stock_data.iloc[-period_days]["Close"]
            if len(stock_data) > period_days
            else stock_data.iloc[0]["Close"]
        )
        price_difference = latest_price - previous_price
        percent_difference = (
            (price_difference / previous_price) * 100 if previous_price != 0 else 0
        )
        return price_difference, percent_difference

    @staticmethod
    def plot_kline(stock_data):
        """繪製K線圖和技術指標。"""
        fig = make_subplots(
            rows=4,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.01,
            row_heights=[0.8, 0.5, 0.5, 0.5],
        )

        # 計算移動平均線
        mav5 = stock_data["Close"].rolling(window=5).mean()
        mav20 = stock_data["Close"].rolling(window=20).mean()
        mav60 = stock_data["Close"].rolling(window=60).mean()

        # 計算RSI和MACD
        rsi = RSIIndicator(close=stock_data["Close"], window=14)
        macd = MACD(
            close=stock_data["Close"], window_slow=26, window_fast=12, window_sign=9
        )

        # K線圖
        fig.add_trace(
            go.Candlestick(
                x=stock_data.index,
                open=stock_data["Open"],
                high=stock_data["High"],
                low=stock_data["Low"],
                close=stock_data["Close"],
                hovertext="K線",
                hoverinfo="text",
            ),
            row=1,
            col=1,
        )
        fig.update_layout(xaxis_rangeslider_visible=False)

        # 繪製移動平均線
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=mav5,
                line=dict(color="blue", width=2),
                name="5-mav",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=mav20,
                line=dict(color="orange", width=2),
                name="20-mav",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=mav60,
                line=dict(color="purple", width=2),
                name="60-mav",
            ),
            row=1,
            col=1,
        )

        # 交易量條形圖
        colors = [
            "green" if row["Open"] - row["Close"] >= 0 else "red"
            for _, row in stock_data.iterrows()
        ]
        fig.add_trace(
            go.Bar(
                x=stock_data.index,
                y=stock_data["Volume"],
                marker_color=colors,
                name="交易量",
            ),
            row=2,
            col=1,
        )

        # RSI指標
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=rsi.rsi(),
                line=dict(color="purple", width=2),
                name="RSI",
            ),
            row=3,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=[70] * len(stock_data.index),
                line=dict(color="red", width=1),
                name="超買",
            ),
            row=3,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=[30] * len(stock_data.index),
                line=dict(color="green", width=1),
                name="超賣",
            ),
            row=3,
            col=1,
        )

        # MACD指標
        colorsM = ["green" if val >= 0 else "red" for val in macd.macd_diff()]
        fig.add_trace(
            go.Bar(
                x=stock_data.index,
                y=macd.macd_diff(),
                marker_color=colorsM,
                name="MACD 差異",
            ),
            row=4,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=macd.macd(),
                line=dict(color="orange", width=2),
                name="MACD",
            ),
            row=4,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=macd.macd_signal(),
                line=dict(color="blue", width=1),
                name="MACD 信號",
            ),
            row=4,
            col=1,
        )

        # 更新Y軸標題
        fig.update_yaxes(title_text="Peice", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        fig.update_yaxes(title_text="MACD", row=4, col=1)

        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
