# 資料分析
import pandas as pd  # 資料處理
import numpy as np  # 資料處理
import json  # JSON 處理
import csv

# 資料擷取與網路相關
import yfinance as yf  # 股票數據
import requests as res  # HTTP 請求
from bs4 import BeautifulSoup  # 網頁解析

# 地理與地圖相關
import folium  # 地圖繪製
from streamlit_folium import folium_static  # Folium 與 Streamlit 整合
from geopy.geocoders import Nominatim  # 地理編碼
import geopy  # 地理位置查找
from geopy.exc import GeocoderInsufficientPrivileges

# 畫圖相關
import plotly.graph_objs as go  # Plotly 圖表物件
import plotly.express as px  # Plotly 快速繪圖
from plotly.subplots import make_subplots  # 子圖支援
import plotly  # Plotly 主模組

# 財務技術分析
from ta.trend import MACD  # MACD 技術指標
from ta.momentum import StochasticOscillator, RSIIndicator  # 隨機震盪與 RSI 技術指標

# 翻譯
from deep_translator import GoogleTranslator
import concurrent.futures

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組


# 1.大盤指數
class plotindex:
    def tran(self):  # 修改方法签名，添加self参数
        return {  # 修改为返回字典而不是使用大括号
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

    def __init__(self, period, time, plot_type="index"):
        self.period = period
        self.time = time
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
        self.symbol_names = {
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
        self.data = {}

    def fetch_data(self):
        """Fetch historical data for the selected indexes."""
        tickers = self.symbols[self.plot_type]

        try:
            data = yf.download(tickers, period=self.period)["Close"]
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
            data = data.rename(columns=self.tran())  # 修改为调用tran方法
            st.dataframe(data)

    def plot_index_vs(self):
        """Plot comparison of US indexes."""
        st.subheader(f"美股大盤＆中小企業{self.time}走勢比較")
        tickers = self.symbols["index"]

        prices = yf.download(tickers, period=self.period).dropna()
        prices = np.log(prices["Close"] / prices["Close"].shift(1))
        prices = prices.cumsum()
        prices = (np.exp(prices) - 1) * 100
        prices = prices.reset_index().melt(
            id_vars="Date", var_name="Ticker", value_name="Growth (%)"
        )

        # Use the custom names in the plot
        prices["Ticker"] = prices["Ticker"].map(self.symbol_names)
        fig = px.line(prices, x="Date", y="Growth (%)", color="Ticker")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
        with st.expander(f"展開美股大盤＆中小企業{self.time}走勢比較"):
            st.dataframe(prices)

    def plot_foreign(self):
        """Plot the foreign indexes."""
        st.subheader(f"美股大盤＆海外大盤{self.time}走勢")

        # Create Plotly subplot figure for foreign indexes
        fig = make_subplots(
            rows=4,  # 确保行数与数据数量匹配
            cols=2,
            subplot_titles=[
                self.symbol_names[symbol] for symbol in self.symbols["foreign"]
            ],
        )

        for i, symbol in enumerate(self.symbols["foreign"]):
            if symbol in self.data:  # 确保数据存在
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
            data = data.rename(columns=self.tran())  # 调用tran方法
            st.dataframe(data)

    def plot_foreign_vs(self):
        """Plot comparison of foreign indexes."""
        st.subheader(f"美股大盤＆海外大盤{self.time}走勢比較")
        tickers = self.symbols["foreign"]

        prices = yf.download(tickers, period=self.period).dropna()
        prices = np.log(prices["Close"] / prices["Close"].shift(1))
        prices = prices.cumsum()
        prices = (np.exp(prices) - 1) * 100
        prices = prices.reset_index().melt(
            id_vars="Date", var_name="Ticker", value_name="Growth (%)"
        )

        # Use the custom names in the plot
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

# 2.公司基本資訊
class cominfo:
    def __init__(self, symbol):
        self.symbol = symbol
        self.com_info = self.get_cominfo()

    def get_cominfo(self):
        """Retrieve detailed company information."""
        stock = yf.Ticker(self.symbol)
        com_info = stock.info

        # Save information as JSON
        with open("df.json", "w") as outfile:
            json.dump(com_info, outfile)

        # Load JSON directly
        with open("df.json", "r") as infile:
            json_data = json.load(infile)
        return json_data

    def categorize_info(self):
        """Categorize and extract company information into five categories."""
        json_data = self.com_info

        # 1. Basic Information
        basic_info = {
            "地址": json_data.get("address1"),
            "城市": json_data.get("city"),
            "州": json_data.get("state"),
            "郵遞區號": json_data.get("zip"),
            "國家": json_data.get("country"),
            "電話": json_data.get("phone"),
            "網站": json_data.get("website"),
            "行業": json_data.get("industry"),
            "部門": json_data.get("sector"),
        }

        # 2. Financial Information
        financial_info = {
            "全職員工": json_data.get("fullTimeEmployees"),
            "市值": json_data.get("marketCap"),
            "總收入": json_data.get("totalRevenue"),
            "總現金": json_data.get("totalCash"),
            "總負債": json_data.get("totalDebt"),
            "自由現金流": json_data.get("freeCashflow"),
            "營運現金流": json_data.get("operatingCashflow"),
            "每股收入":json_data.get("revenuePerShare"),
            "每股帳面價值":json_data.get("bookValue"),
            "負債股權比率":json_data.get("debtToEquity"),
            "總利潤率":json_data.get("grossMargins"),
            "營業利潤率":json_data.get("operatingMargins"),
            "資產回報率": json_data.get("returnOnAssets"),
            "股東權益報酬率": json_data.get("returnOnEquity"),
        }

        # 3. Risk and Shareholder Information
        risk_info = {
            "審計風險": json_data.get("auditRisk"),
            "董事會風險": json_data.get("boardRisk"),
            "薪酬風險": json_data.get("compensationRisk"),
            "股東權利風險": json_data.get("shareHolderRightsRisk"),
            "內部人持股比例": json_data.get("heldPercentInsiders"),
            "機構持股比例": json_data.get("heldPercentInstitutions"),
        }

        # 4. Executive Information
        officers_info = json_data.get("companyOfficers", [])

        # 5. Market Information
        market_info = {
            "當前價格": json_data.get("currentPrice"),
            "52 週最高價": json_data.get("fiftyTwoWeekHigh"),
            "52 週最低價": json_data.get("fiftyTwoWeekLow"),
            "目標最高價": json_data.get("targetHighPrice"),
            "目標最低價": json_data.get("targetLowPrice"),
            "平均目標價": json_data.get("targetMeanPrice"),
            "過去市盈率": json_data.get("trailingPE"),
            "預測市盈率": json_data.get("forwardPE"),
            "股息率": json_data.get("dividendRate"),
            "股息收益率": json_data.get("dividendYield"),
        }
        
        #other info
        other_info = {
            "企業價值": json_data.get("enterpriseValue"),
            "每股收益（過去）": json_data.get("trailingEps"),
            "每股收益（預測）": json_data.get("forwardEps"),
            "盈利增長": json_data.get("earningsGrowth"),
            "收入增長": json_data.get("revenueGrowth"),
            "貨幣": json_data.get("financialCurrency"),
        }        

        return basic_info, financial_info, risk_info, officers_info, market_info,other_info

    def display_categorized_info(self):
        """Display categorized company information."""
        basic_info, financial_info, risk_info, officers_info, market_info,other_info = self.categorize_info()

        st.subheader(f"{self.symbol}-基本公司資訊")
        st.write(pd.DataFrame([basic_info]))

        st.subheader(f"{self.symbol}-財務資訊")
        st.write(pd.DataFrame([financial_info]))

        st.subheader(f"{self.symbol}-風險與股東資訊")
        st.write(pd.DataFrame([risk_info]))
        
        st.subheader(f"{self.symbol}-高管訊息")
        st.write(pd.DataFrame(officers_info))

        st.subheader(f"{self.symbol}-市場與股價訊息")
        st.write(pd.DataFrame([market_info]))
        
        st.subheader(f"{self.symbol}-其他訊息")
        st.write(pd.DataFrame([other_info]))

    def get_location(self, address, city, country):
        """Get the geographic location of the company."""
        geolocator = Nominatim(user_agent="streamlit_app")

        # Try locating using the address
        location = geolocator.geocode(f"{address}, {city}, {country}")

        # If address fails, try city and country
        if location is None:
            location = geolocator.geocode(f"{city}, {country}")
        return location

    def display_map(self, location, company):
        """Display a map with the company's location."""
        m = folium.Map(location=[location.latitude, location.longitude], zoom_start=15)
        folium.Marker(
            [location.latitude, location.longitude],
            tooltip=f"{self.symbol} Location",
        ).add_to(m)
        folium_static(m)

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
        stock_data = yf.download(symbol, start=start, end=end)
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

#獲利資訊
class Other:
    def __init__(self, symbol):
        self.symbol = symbol
        
    def get_eps(self):
        stock = yf.Ticker(self.symbol)
        eps = stock.earnings_dates
        st.subheader(f"{self.symbol}-獲利資訊")
        st.table(eps)
    
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


# 8.機構評級
class Holding:
    tran_dict = {
        "Date Reported": "報告日期",
        "Holder": "持有人",
        "pctHeld": "持股比例",
        "Shares": "股份數",
        "Value": "價值",
        "Date": "日期",
        "Action": "動作",
        "Analyst": "分析機構",
        "Rating Change": "評級變化",
        "Price Target Change": "目標價格變化",
        "Price Target Start": "目標價格起始",
        "Price Target End": "目標價格結束",
    }

    @staticmethod
    def display_pie_chart(holder_name, pct_held, title, ticker):
        """Display pie chart for holders."""
        fig = go.Figure()
        fig.add_trace(
            go.Pie(
                labels=holder_name,
                values=pct_held,
                hoverinfo="label+percent+value",
                textinfo="percent",
                textfont_size=12,
                hole=0.4,
                marker=dict(
                    colors=[
                        f"rgb({i*30 % 255}, {100 + i*40 % 155}, {i*50 % 255})"
                        for i in range(len(holder_name))
                    ]
                ),
            )
        )

        # 添加股票代號到甜甜圈圖的中心
        fig.add_annotation(
            text=ticker,  # 股票代號
            font=dict(size=20, color="black"),  # 設定字體大小和顏色
            showarrow=False,  # 不顯示箭頭
            x=0.5,  # x座標
            y=0.5,  # y座標
            align="center",  # 文字對齊方式
        )

        fig.update_layout(title=title)  # 直接使用標題
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    @staticmethod
    def holder(symbol):
        symbol = yf.Ticker(symbol)
        holders = symbol.institutional_holders

        if holders is not None and not holders.empty:
            pct_held = holders["pctHeld"]
            holder_name = holders["Holder"]
            Holding.display_pie_chart(
                holder_name,
                pct_held,
                f"機構持股 {symbol.ticker} 比例前10名",
                symbol.ticker,
            )
            df = pd.DataFrame(holders)
            df.rename(columns=Holding.tran_dict, inplace=True)
            with st.expander(f"機構持股 {symbol.ticker} 比例與價值前10名數據"):
                st.table(df)
        else:
            st.error(f"{symbol} 無機構持有數據")

    @staticmethod
    def fund_holder(symbol):
        symbol = yf.Ticker(symbol)
        funds = symbol.mutualfund_holders

        if funds is not None and not funds.empty:
            pct_held = funds["pctHeld"]
            holder_name = funds["Holder"]
            Holding.display_pie_chart(
                holder_name,
                pct_held,
                f"共同基金持股 {symbol.ticker} 比例前10名",
                symbol.ticker,
            )
            df = pd.DataFrame(funds)
            df.rename(columns=Holding.tran_dict, inplace=True)
            with st.expander(f"共同基金持股 {symbol.ticker} 比例與價值前10名數據"):
                st.table(df)
        else:
            st.error(f"{symbol} 無共同基金持有數據")

    @staticmethod
    def scrape_finviz(symbol):
        url = f"https://finviz.com/quote.ashx?t={symbol}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = res.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"無法從 {url} 獲取數據，狀態碼: {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find(
            "table", class_="js-table-ratings styled-table-new is-rounded is-small"
        )

        if table is None:
            raise Exception("未能在頁面上找到評級表格。")

        data = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            data.append(
                {
                    "Date": cols[0].text.strip(),
                    "Action": cols[1].text.strip(),
                    "Analyst": cols[2].text.strip(),
                    "Rating Change": cols[3].text.strip(),
                    "Price Target Change": (
                        cols[4].text.strip() if len(cols) > 4 else None
                    ),
                }
            )

        df = pd.DataFrame(data).dropna(subset=["Price Target Change"])
        df["Price Target Change"] = (
            df["Price Target Change"].str.replace("→", "->").str.replace(" ", "")
        )

        if df["Price Target Change"].str.contains(r"\$").any():
            price_change_ranges = df["Price Target Change"].str.extract(
                r"\$(\d+)->\$(\d+)"
            )
            price_change_ranges = price_change_ranges.apply(
                pd.to_numeric, errors="coerce"
            )

            df["Price Target Start"] = price_change_ranges[0]
            df["Price Target End"] = price_change_ranges[1]

            # 設置評級的順序
            rating_order = df["Rating Change"].unique().tolist()
            df["Rating Change"] = pd.Categorical(
                df["Rating Change"], categories=rating_order, ordered=True
            )
            df.rename(columns=Holding.tran_dict, inplace=True)

            # 繪製圖表
            fig1 = go.Figure()
            for i, row in df.iterrows():
                fig1.add_trace(
                    go.Scatter(
                        x=[row["目標價格起始"], row["目標價格結束"]],
                        y=[row["分析機構"], row["分析機構"]],
                        mode="lines+markers+text",
                        line=dict(
                            color=(
                                "blue"
                                if row["目標價格結束"] >= row["目標價格起始"]
                                else "red"
                            ),
                            width=2,
                        ),
                        marker=dict(size=10),
                        text=[f"${row['目標價格起始']}", f"${row['目標價格結束']}"],
                        textposition="top center",
                    )
                )

            fig1.update_layout(
                title=f"機構對 {symbol} 目標價格變化",
                xaxis_title="目標價格",
                yaxis_title="機構",
                yaxis=dict(type="category"),
                showlegend=False,
            )

            fig2 = px.histogram(
                df,
                x="評級變化",
                title=f"機構評級 {symbol} 變化分佈",
                color="評級變化",
                category_orders={"評級變化": rating_order},
            )
            fig2.update_layout(showlegend=False)

            st.plotly_chart(fig1)
            st.plotly_chart(fig2)
            with st.expander(f"機構評級 {symbol} 變化分佈數據"):
                st.table(df)


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


# streamlit版面配置
def app():
    st.set_page_config(page_title="MarketInfo", layout="wide", page_icon="📈")
    hide_menu_style = "<style> footer {visibility: hidden;} </style>"
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align: center; color: rainbow;'>📈 MarketInfo</h1>",
        unsafe_allow_html=True,
    )
    st.subheader(" ", divider="rainbow")
    st.sidebar.title("📊 Menu")
    options = st.sidebar.selectbox(
        "選擇功能",
        [
            "大盤指數",
            "公司基本資訊",
            "公司財報",
            "交易數據",
            "其他資訊",
            "期權數據",
            "SEC文件",
            "機構買賣",
            "近期相關消息",
        ],
    )
    st.sidebar.markdown(
        """
    ### 免責聲明：
    1. **K 線圖觀看角度**  
    - 綠漲、紅跌  
    2. 本平台僅適用於數據搜尋，不建議任何投資行為  
    3. 排版問題建議使用電腦查詢數據  
    4. 其他專案：[MarketSearch](https://marketsearch.streamlit.app)  
    """
    )

    if options == "大盤指數":
        period = st.selectbox(
            "選擇時長", ["年初至今", "1年", "2年", "5年", "10年", "全部"]
        )
        if period == "年初至今":
            period = "ytd"
            time = "年初至今"
        elif period == "1年":
            period = "1y"
            time = "1年"
        elif period == "2年":
            period = "2y"
            time = "2年"
        elif period == "5年":
            period = "5y"
            time = "5年"
        elif period == "10年":
            period = "10y"
            time = "10年"
        elif period == "全部":
            period = "max"
            time = "全部"

        # 繪製大盤指數
        pltindex = plotindex(period, time, plot_type="index")
        pltindex.plot()

        # 繪製海外大盤
        pltforeign = plotindex(period, time, plot_type="foreign")
        pltforeign.plot()

    elif options == "公司基本資訊":
        symbol = st.text_input("輸入美股代號").upper()
        if st.button("查詢"):
            if symbol:
                company = cominfo(symbol)

                # 獲取地址資訊
                address = company.com_info["address1"]
                city = company.com_info["city"]
                country = company.com_info["country"]

                # 獲取公司位置
                location = company.get_location(address, city, country)

                # 顯示翻譯後的資訊
                company.display_categorized_info()

                # 顯示地圖
                if location:
                    st.subheader(f"{symbol}-位置")
                    company.display_map(location,company)
                else:
                    st.error(f"無法獲取{symbol}位置。")

    elif options == "公司財報":
        with st.expander("展開輸入參數"):
            time_range = st.selectbox("選擇時長", ["年報", "季報"])
            if time_range == "年報":
                symbol = st.text_input("輸入美股代碼").upper()
            elif time_range == "季報":
                symbol = st.text_input("輸入美股代碼").upper()
        if st.button("查詢"):
            if time_range == "年報":
                translator = financialreport_y(symbol)
                translator.get_financial()
                translator.tran_financial()
                translator.display_financial()
            elif time_range == "季報":
                translator_quarterly = financialreport_q(symbol)
                translator_quarterly.get_financial_q()
                translator_quarterly.tran_financial_q()
                translator_quarterly.display_financial_q()

    elif options == "交易數據":
        with st.expander("展開輸入參數"):
            range = st.selectbox("長期/短期", ["長期", "短期", "自訂範圍"])
            if range == "長期":
                symbol = st.text_input("輸入美股代碼").upper()
                time_range = st.selectbox(
                    "選擇時長", ["1年", "2年", "5年", "10年", "全部"]
                )
                if time_range == "1年":
                    period = "1y"
                    period_days = 252
                elif time_range == "2年":
                    period = "2y"
                    period_days = 252 * 2
                elif time_range == "5年":
                    period = "5y"
                    period_days = 252 * 5
                elif time_range == "10年":
                    period = "10y"
                    period_days = 252 * 10
                elif time_range == "全部":
                    period = "max"
                    period_days = None  # 使用全部数据的长度

            elif range == "短期":
                symbol = st.text_input("輸入美股代碼").upper()
                time_range = st.selectbox(
                    "選擇時長", ["年初至今", "1個月", "3個月", "6個月"]
                )
                if time_range == "年初至今":
                    period = "ytd"
                    period_days = None
                elif time_range == "1個月":
                    period = "1mo"
                    period_days = 21  # 一个月大约是21个交易日
                elif time_range == "2個月":
                    period = "2mo"
                    period_days = 42
                elif time_range == "3個月":
                    period = "3mo"
                    period_days = 63  # 三个月大约是63个交易日
                elif time_range == "6個月":
                    period = "6mo"
                    period_days = 126  # 六个月大约是126个交易日

            elif range == "自訂範圍":
                symbol = st.text_input("輸入美股代碼").upper()
                start_date = st.date_input("開始日期")
                end_date = st.date_input("結束日期")
                time_range = f"{start_date}~{end_date}"
                if start_date and end_date:
                    period_days = (end_date - start_date).days

        if st.button("查詢"):
            if symbol:
                # 获取股票数据
                if range == "長期" or range == "短期":
                    stock_data = tradedata.getdata(symbol, period)
                    st.subheader(f"{symbol}-{time_range}交易數據")
                elif range == "自訂範圍":
                    stock_data = tradedata.get_data_time_range(
                        symbol, start_date, end_date
                    )
                    st.subheader(f"{symbol}-{start_date}～{end_date}交易數據")

                if stock_data is not None and not stock_data.empty:
                    if period_days is None:
                        period_days = len(
                            stock_data
                        )  # 更新 period_days 为 stock_data 的长度
                    price_difference, percent_difference = (
                        tradedata.calculate_difference(stock_data, period_days)
                    )

                    latest_close_price = stock_data.iloc[-1]["Close"]

                    highest_price = stock_data["High"].max()
                    lowest_price = stock_data["Low"].min()

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("最新收盤價", f"${latest_close_price:.2f}")
                    with col2:
                        st.metric(
                            f"{time_range}增長率",
                            f"${price_difference:.2f}",
                            f"{percent_difference:+.2f}%",
                        )
                    with col3:
                        st.metric(f"{time_range}最高價", f"${highest_price:.2f}")
                    with col4:
                        st.metric(f"{time_range}最低價", f"${lowest_price:.2f}")
                    st.subheader(f"{symbol}-{time_range}K線圖表")
                    tradedata.plot_kline(stock_data)
                else:
                    st.error(f"查無{symbol}數據")
                with st.expander(f"展開{symbol}-{time_range}數據"):
                    st.dataframe(stock_data)
    
    elif options == "其他資訊":
        symbol = st.text_input("輸入美股代號").upper()
        if st.button("查詢"):
            other = Other(symbol)
            other.get_eps()
            other.get_insider()
            
    elif options == "期權數據":
        if "symbol" not in st.session_state:
            st.session_state.symbol = ""

        if st.session_state.symbol == "":
            symbol = st.text_input("輸入美股代號").upper()
            if st.button("查詢"):
                st.session_state.symbol = symbol  # 保存查詢的 symbol
        else:
            symbol = st.session_state.symbol

        if symbol:
            option = Option(symbol)
            option_dates = option.get_option_dates()
            df = pd.DataFrame(option_dates, columns=["可用日期"])
            st.subheader(f"{symbol} 期權到期日")
            st.table(df)

            date = st.date_input("選擇日期（請依照上面日期選擇）")
            date_str = date.strftime("%Y-%m-%d")  # 將日轉換為字符串進行比較

            if date_str in option_dates:
                st.subheader(f"{symbol}看漲期權(到期日：{date_str})")
                calls_df = option.options_calls_date(date_str)
                st.dataframe(option.tran_col(calls_df))

                st.subheader(f"{symbol}看跌期權(到期日：{date_str})")
                puts_df = option.options_puts_date(date_str)
                st.dataframe(option.tran_col(puts_df))
            else:
                st.error("查無相關日期期權")

    elif options == "SEC文件":
        symbol = st.text_input("輸入美股代號").upper()
        if st.button("查詢"):
            sec = secreport(symbol)
            sec.display_filings()

    elif options == "機構買賣":
        symbol = st.text_input("輸入美股代號").upper()
        if st.button("查詢"):
            Holding.holder(symbol)
            Holding.fund_holder(symbol)
            Holding.scrape_finviz(symbol)
            st.markdown(f"[資料來源](https://finviz.com/quote.ashx?t={symbol})")

    elif options == "近期相關消息":
        symbol = st.text_input("輸入美股代號").upper()
        if st.button("查詢"):
            if symbol:
                news_data = News()
                news_data = news_data.getnews(symbol)
                if news_data:
                    # 将新闻数据转换为DataFrame
                    df = pd.DataFrame(news_data)
                    st.subheader(f"{symbol}-近期相關消息")
                    st.write(df)  # 显示表格
                    # 打印所有新闻链接
                    with st.expander(f"展開{symbol}-近期相關消息連結"):
                        for news in news_data:
                            st.write(f'**[{news["Title"]}]({news["URL"]})**')
                    st.markdown(f"[資料來源](https://finviz.com/quote.ashx?t={symbol})")
                else:
                    st.write(f"查無{symbol}近期相關消息")


if __name__ == "__main__":
    app()
