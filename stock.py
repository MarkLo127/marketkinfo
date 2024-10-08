# 資料分析
import pandas as pd  # 資料處理
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

#翻譯
from deep_translator import GoogleTranslator
import concurrent.futures

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

#1.大盤指數
class plotindex:
    def __init__(self, period, time, plot_type='index'):
        self.period = period
        self.time = time
        self.plot_type = plot_type
        self.symbols = {
            'index': ['^IXIC', '^VIX', '^GSPC', '^DJI', '^SOX', '^RUT'],
            'foreign': ['^GSPC', '^IXIC', '^HSI', '399001.SZ', '^TWII', '^N225']
        }
        self.data = {}
    
    def fetch_data(self):
        """Fetch historical data for the selected indexes."""
        tickers = self.symbols[self.plot_type]
        
        try:
            data = yf.download(tickers, period=self.period)['Adj Close']
            for symbol in tickers:
                if symbol in data:
                    self.data[symbol] = data[symbol].dropna()
        except Exception as e:
            st.error(f"Error fetching data: {e}")

    def plot_index(self):
        """Plot the US indexes."""
        st.subheader(f'美股大盤＆中小企業{self.time}走勢')

        # Create Plotly subplot figure for indexes
        fig = make_subplots(rows=3, cols=2, subplot_titles=["NASDAQ", "VIX", "S&P 500", "DJIA", "PHLX Semiconductor Sector", "Russell-2000"])

        for i, symbol in enumerate(self.symbols['index']):
            fig.add_trace(go.Scatter(x=self.data[symbol].index, y=self.data[symbol].values, mode='lines', name=symbol), row=(i // 2) + 1, col=(i % 2) + 1)

        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    def plot_index_vs(self):
        st.subheader(f'美股大盤＆中小企業{self.time}走勢比較')
        tickers = self.symbols['index']
        
        prices = yf.download(tickers, period=self.period)['Adj Close'].dropna()
        prices = prices / prices.iloc[0] * 100
        prices = prices.reset_index().melt(id_vars='Date', var_name='Ticker', value_name='Growth (%)')
        
        fig = px.line(prices, x='Date', y='Growth (%)', color='Ticker')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    def plot_foreign(self):
        """Plot the foreign indexes."""
        st.subheader(f'美股大盤＆海外大盤{self.time}走勢')

        # Create Plotly subplot figure for foreign indexes
        fig = make_subplots(rows=3, cols=2, subplot_titles=["S&P 500", "NASDAQ", "恆生指數", "深證指數", "加權指數", "日經指數"])

        for i, symbol in enumerate(self.symbols['foreign']):
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            # Apply conversion for foreign indexes
            if symbol in ['^HSI', '399001.SZ', '^TWII', '^N225']:  
                exchange_rates = {'^HSI': 0.13, '399001.SZ': 0.14, '^TWII': 0.031, '^N225': 0.0067}
                fig.add_trace(go.Scatter(x=self.data[symbol].index, y=(self.data[symbol] * exchange_rates[symbol]).values, mode='lines', name=symbol), row=row, col=col)
            else:
                fig.add_trace(go.Scatter(x=self.data[symbol].index, y=self.data[symbol].values, mode='lines', name=symbol), row=row, col=col)

        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
    
    def plot_foreign_vs(self):
        st.subheader(f'美股大盤＆海外大盤{self.time}走勢比較')
        tickers = self.symbols['foreign']
        exchange_rates = {'^HSI': 0.13, '399001.SZ': 0.14, '^TWII': 0.031, '^N225': 0.0067}
        
        prices = yf.download(tickers, period=self.period)['Adj Close'].dropna()
        prices = prices / prices.iloc[0] * 100
        prices = prices.reset_index().melt(id_vars='Date', var_name='Ticker', value_name='Growth (%)')
        
        for ticker, rate in exchange_rates.items():
            prices.loc[prices['Ticker'] == ticker, 'Growth (%)'] *= rate
        
        fig = px.line(prices, x='Date', y='Growth (%)', color='Ticker')
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig)
  
    def plot(self):
        """Plot the financial data based on the selected type."""
        self.fetch_data()
        if self.plot_type == 'index':
            self.plot_index()
            self.plot_index_vs()
        elif self.plot_type == 'foreign':
            self.plot_foreign()
            self.plot_foreign_vs()

#2.公司基本資訊
class cominfo:
    tran_dict = {
        'address1': '地址',
        'city': '城市',
        'country': '國家',
        'phone': '電話',
        'website': '網站',
        'industry': '行業',
        'sector': '產業',
        'longBusinessSummary': '公司簡介',
        'fullTimeEmployees': '全職員工數量',
        'marketCap': '市值',
        'totalRevenue': '總收入',
        'netIncomeToCommon': '淨利潤',
        'trailingEps': '每股盈餘(EPS)',
        'trailingPE': '本益比(PE)',
        'dividendRate': '股息率',
        'dividendYield': '股息殖利率',
        'beta': 'Beta值',
        'profitMargins': '利潤率',
        'revenueGrowth': '收入成長率',
        'earningsGrowth': '收益成長率'
    }

    def __init__(self, symbol):
        self.symbol = symbol
        self.com_info = self.get_com_info()

    def get_com_info(self):
        """獲取公司的詳細資訊"""
        stock = yf.Ticker(self.symbol)
        com_info = stock.info

        # 儲存資訊為 JSON
        with open("df.json", "w") as outfile:
            json.dump(com_info, outfile)

        # 讀取資料並轉置
        df = pd.read_json("df.json").head(1).transpose()
        return df

    def tran_info(self):
        """翻譯公司資訊並格式化顯示"""
        tran_info = {}
        self.com_info.index = self.com_info.index.str.strip()  # 去除索引空格

        for key in self.tran_dict.keys():
            if key in self.com_info.index:
                value = self.com_info.loc[key].values[0]
                if isinstance(value, float):
                    if 'rate' in key or 'Growth' in key or 'Yield' in key:
                        value = f"{value * 100:.2f}%"  # 百分比格式
                    else:
                        value = f"{value:,.2f}"  # 千分位格式
                elif isinstance(value, int):
                    value = f"{value:,}"  # 千分位格式
                tran_info[self.tran_dict[key]] = value

        return pd.DataFrame.from_dict(tran_info, orient='index', columns=['內容'])

    def get_location(self, address, city, country):
        """獲取公司位置的經緯度，若 address 無法定位則使用 city 定位"""
        geolocator = Nominatim(user_agent="streamlit_app")
        
        # 優先嘗試使用 address 定位
        location = geolocator.geocode(f"{address}, {city}, {country}")
        
        # 如果 address 無法定位，則使用 city 和 country 來定位
        if location is None:
            location = geolocator.geocode(f"{city}, {country}")
        return location


    def display_map(self, location, translated_df):
        """顯示公司位置的地圖"""
        m = folium.Map(location=[location.latitude, location.longitude], zoom_start=15)
        folium.Marker([location.latitude, location.longitude],popup=translated_df.to_html(escape=False),tooltip=f'{self.symbol}位置').add_to(m)
        folium_static(m)

#3.公司經營狀況
class com＿mange:
    def get_mange_info(symbol):
        # Step 1: Get stock statistics
        url = f"https://finviz.com/quote.ashx?t={symbol}&p=d#statements"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        try:
            response = res.get(url, headers=headers)
            response.raise_for_status()
        except res.exceptions.RequestException as e:
            st.error(f"獲取 {symbol} 數據時出錯: {e}")
            return None
        # Step 2: Parse the HTML to get the data
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='snapshot-table2')
        if not table:
            st.error("頁面上未找到表格")
            return None
        
        # Step 3: Extract data into a dictionary
        rows = table.find_all('tr')
        data = {}
        for row in rows:
            cells = row.find_all('td')
            for i in range(0, len(cells), 2):
                key = cells[i].get_text(strip=True)
                value = cells[i + 1].get_text(strip=True)
                data[key] = value
        # Step 4: Process values for categorization and plotting
        def process_value(value):
            if isinstance(value, str):
                value = value.replace(',', '')  # Remove commas for thousands
                if value.endswith('%'):
                    return float(value[:-1])  # Convert percentage to float
                elif value.endswith('B'):
                    return float(value[:-1]) * 1e9  # Convert billions to float
                elif value.endswith('M'):
                    return float(value[:-1]) * 1e6  # Convert millions to float
                elif value.endswith('K'):
                    return float(value[:-1]) * 1e3  # Convert thousands to float
                elif value.replace('.', '', 1).isdigit():  # Check if it's a numeric string
                    return float(value)  # Convert numeric string to float
            return value  # Return the original value if no conversion is needed
        # Create a DataFrame for categorization
        df = pd.DataFrame(list(data.items()), columns=['Metric', 'Value'])
        # Step 5: Categorize and plot data
        st.subheader(f'{symbol}-經營狀況')
        st.table(df)

# 4.公司財報
#年報
class financialreport_y:
    def __init__(self, symbol, target_language='zh-TW'):
        self.symbol = symbol
        self.target_language = target_language
        self.balance_sheet = None
        self.income_statement = None
        self.cash_flow = None
    
    # 多進程翻譯函數
    def tran(self, texts):
        translator = GoogleTranslator(source='en', target=self.target_language)
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
                    [tuple(self.tran([str(col) for col in level])) for level in df.columns.levels]
                )
            else:
                df.columns = self.tran([str(col) for col in df.columns])

            # 多進程翻譯索引名
            if isinstance(df.index, pd.MultiIndex):
                df.index = pd.MultiIndex.from_tuples(
                    [tuple(self.tran([str(idx) for idx in level])) for level in df.index.levels]
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
            self.income_statement = stock.financials
            self.cash_flow = stock.cashflow
        except Exception as e:
            st.error(f"獲取財務報表發生錯誤：{str(e)}")
            self.balance_sheet, self.income_statement, self.cash_flow = None, None, None
    
    # 翻譯財務報表
    def tran_financial(self):
        if self.balance_sheet is not None:
            self.balance_sheet = self.tran_df(self.balance_sheet)
        if self.income_statement is not None:
            self.income_statement = self.tran_df(self.income_statement)
        if self.cash_flow is not None:
            self.cash_flow = self.tran_df(self.cash_flow)
    
    # 顯示財務報表
    def display_financial(self):
        if self.balance_sheet is not None:
            st.subheader(f"{self.symbol}-資產負債表/年")
            st.dataframe(self.balance_sheet)

        if self.income_statement is not None:
            st.subheader(f"{self.symbol}-綜合損益表/年")
            st.dataframe(self.income_statement)

        if self.cash_flow is not None:
            st.subheader(f"{self.symbol}-現金流量表/年")
            st.dataframe(self.cash_flow)

#季報
class ffinancialreport_q:
    def __init__(self, symbol, target_language='zh-TW'):
        self.symbol = symbol
        self.target_language = target_language
        self.quarterly_balance_sheet = None
        self.quarterly_income_statement = None
        self.quarterly_cash_flow = None
    
    # 多進程翻譯函數
    def tran(self, texts):
        translator = GoogleTranslator(source='en', target=self.target_language)
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
                    [tuple(self.tran([str(col) for col in level])) for level in df.columns.levels]
                )
            else:
                df.columns = self.tran([str(col) for col in df.columns])

            # 多進程翻譯索引名
            if isinstance(df.index, pd.MultiIndex):
                df.index = pd.MultiIndex.from_tuples(
                    [tuple(self.tran([str(idx) for idx in level])) for level in df.index.levels]
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
            self.quarterly_balance_sheet = stock.quarterly_balance_sheet
            self.quarterly_income_statement = stock.quarterly_financials
            self.quarterly_cash_flow = stock.quarterly_cashflow
        except Exception as e:
            st.error(f"獲取財務報表發生錯誤：{str(e)}")
            self.quarterly_balance_sheet, self.quarterly_income_statement, self.quarterly_cash_flow = None, None, None
    
    # 翻譯季度財務報表
    def tran_financial_q(self):
        if self.quarterly_balance_sheet is not None:
            self.quarterly_balance_sheet = self.tran_df(self.quarterly_balance_sheet)
        if self.quarterly_income_statement is not None:
            self.quarterly_income_statement = self.tran_df(self.quarterly_income_statement)
        if self.quarterly_cash_flow is not None:
            self.quarterly_cash_flow = self.tran_df(self.quarterly_cash_flow)
    
    # 顯示季度財務報表
    def display_financial_q(self):
        if self.quarterly_balance_sheet is not None:
            st.subheader(f"{self.symbol}-資產負債表/季")
            st.dataframe(self.quarterly_balance_sheet)

        if self.quarterly_income_statement is not None:
            st.subheader(f"{self.symbol}-綜合損益表/季")
            st.dataframe(self.quarterly_income_statement)

        if self.quarterly_cash_flow is not None:
            st.subheader(f"{self.symbol}-現金流量表/季")
            st.dataframe(self.quarterly_cash_flow)

# 5.交易數據
class tradedata:
    
    @staticmethod
    def getdata(symbol, time_range):
        stock_data = yf.download(symbol, period=time_range)
        return stock_data
    
    @staticmethod
    def getdata_timerange(symbol,start,end):
        stock_data = yf.download(symbol,start=start,end=end)
        return stock_data

    # 計算價格差異的函數
    @staticmethod
    def calculate_difference(stock_data, period_days):
        latest_price = stock_data.iloc[-1]["Adj Close"]  # 最新收盤價
        previous_price = stock_data.iloc[-period_days]["Adj Close"] if len(stock_data) > period_days else stock_data.iloc[0]["Adj Close"]  # 特定天數前的收盤價
        price_difference = latest_price - previous_price  # 計算價格差異
        percent_difference = (price_difference / previous_price) * 100  # 計算百分比變化
        return price_difference, percent_difference  # 返回價格差異和百分比變化

    # 繪製K線圖
    @staticmethod
    def plot_kline(stock_data):
        fig = plotly.subplots.make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.8, 0.5, 0.5, 0.5])
        
        mav5 = stock_data['Adj Close'].rolling(window=5).mean()  # 5日MAV
        mav20 = stock_data['Adj Close'].rolling(window=20).mean()  # 20日MAV
        mav60 = stock_data['Adj Close'].rolling(window=60).mean()  # 60日MAV
        
        rsi = RSIIndicator(close=stock_data['Adj Close'], window=14)
        macd = MACD(close=stock_data['Adj Close'], window_slow=26, window_fast=12, window_sign=9)

        # K線圖
        fig.add_trace(go.Candlestick(x=stock_data.index, open=stock_data['Open'], high=stock_data['High'], low=stock_data['Low'], close=stock_data['Adj Close']), row=1, col=1)
        fig.update_layout(xaxis_rangeslider_visible=False)

        # 移動平均線
        fig.add_trace(go.Scatter(x=stock_data.index, y=mav5, line=dict(color='blue', width=2), name='MAV-5', showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=mav20, line=dict(color='orange', width=2), name='MAV-20', showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=mav60, line=dict(color='purple', width=2), name='MAV-60', showlegend=False), row=1, col=1)

        # 成交量
        colors = ['green' if row['Open'] - row['Adj Close'] >= 0 else 'red' for _, row in stock_data.iterrows()]
        fig.add_trace(go.Bar(x=stock_data.index, y=stock_data['Volume'], marker_color=colors, name='Volume', showlegend=False), row=2, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=stock_data.index, y=rsi.rsi(), line=dict(color='purple', width=2), showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=[70]*len(stock_data.index), line=dict(color='red', width=1), name='Overbought', showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=[30]*len(stock_data.index), line=dict(color='green', width=1), name='Oversold', showlegend=False), row=3, col=1)

        # MACD
        colorsM = ['green' if val >= 0 else 'red' for val in macd.macd_diff()]
        fig.add_trace(go.Bar(x=stock_data.index, y=macd.macd_diff(), marker_color=colorsM, showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=macd.macd(), line=dict(color='orange', width=2), showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=macd.macd_signal(), line=dict(color='blue', width=1), showlegend=False), row=4, col=1)

        # 設置Y軸標題
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        fig.update_yaxes(title_text="MACD", row=4, col=1)

        # 隱藏圖例
        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

# 6.期權數據
class Option:
    def __init__(self, symbol):
        self.symbol = symbol

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

            st.subheader(f"公司 {self.symbol} 的 SEC 文件:")
            st.dataframe(filings)  # 顯示為 DataFrame 表格

            # 展開連結部分
            with st.expander(f'展開 {self.symbol} 的 SEC 連結'):
                for index, row in filings.iterrows():
                    st.write(f"{row['date']} - [{row['type']}] - [{row['title']}]({row['edgarUrl']})")
        else:
            st.error(f"無法獲取公司 {self.symbol} 的 SEC 文件。")

# 8.機構評級
class Holding:
    def __init__(self, symbol):
        self.symbol = symbol

    @staticmethod
    def holder(symbol):
        symbol = yf.Ticker(symbol)
        holders = symbol.institutional_holders
      
        if holders is not None:
            # 提取 pctHeld, value 和 Holder 欄位，並將持股比例轉換為百分比
            pct_held = holders['pctHeld']  # 轉換為百分比
            value = holders['Value']
            holder_name = holders['Holder']
            
            # 動態生成不同顏色列表，每個直條不同顏色
            colors = [f'rgb({i*30 % 255}, {100 + i*40 % 155}, {i*50 % 255})' for i in range(len(holder_name))]
            
            # 使用 plotly 繪製條形圖
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=holder_name,
                y=pct_held,
                name='持股比例 (%)',
                marker=dict(color=colors),  # 使用不同顏色
                text=value,  # 顯示價值
                texttemplate='%{text:.2s}',  # 格式化數值
                textposition='auto'
            ))
            
            fig.update_layout(
                title=f'機構持股{symbol.ticker}比例與價值',
                xaxis_title='機構',
                yaxis_title='持股比例 (%)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"{symbol} 無機構持有數據")
        df = pd.DataFrame(holders)
        with st.expander(f"機構持股{symbol.ticker}比例與價值數據"):
            st.table(df)

    @staticmethod
    def fund_holder(symbol):
        symbol = yf.Ticker(symbol)
        funds = symbol.mutualfund_holders
        
        if funds is not None:
            # 提取 pctHeld, value 和 Holder 欄位，並將持股比例轉換為百分比
            pct_held = funds['pctHeld']  # 轉換為百分比
            value = funds['Value']
            holder_name = funds['Holder']
            
            # 動態生成不同顏色列表，每個直條不同顏色
            colors = [f'rgb({i*35 % 255}, {i*45 % 255}, {150 + i*55 % 105})' for i in range(len(holder_name))]
            
            # 使用 plotly 繪製條形圖
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=holder_name,
                y=pct_held,
                name='持股比例 (%)',
                marker=dict(color=colors),  # 使用不同顏色
                text=value,  # 顯示價值
                texttemplate='%{text:.2s}',  # 格式化數值
                textposition='auto'
            ))
            
            fig.update_layout(
                title=f'共同基金持股{symbol.ticker}比例與價值',
                xaxis_title='共同基金',
                yaxis_title='持股比例 (%)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"{symbol} 無共同基金持有數據")

        df = pd.DataFrame(funds)
        with st.expander(f"共同基金持股{symbol.ticker}比例與價值數據"):
            st.table(df)

    @staticmethod
    def scrape_finviz(symbol):
        # 爬蟲部分
        url = f"https://finviz.com/quote.ashx?t={symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = res.get(url, headers=headers)

        # 檢查請求是否成功
        if response.status_code != 200:
            raise Exception(f"無法從 {url} 獲取數據，狀態碼: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 定位包含分析師評級的表格
        table = soup.find('table', class_='js-table-ratings styled-table-new is-rounded is-small')
        
        # 檢查是否成功找到表格
        if table is None:
            raise Exception("未能在頁面上找到評級表格。")
        
        # 從表格中提取數據
        data = []
        for row in table.find_all('tr')[1:]:  # 跳過表頭
            cols = row.find_all('td')
            data.append({
                "Date": cols[0].text.strip(),
                "Action": cols[1].text.strip(),
                "Analyst": cols[2].text.strip(),
                "Rating Change": cols[3].text.strip(),
                "Price Target Change": cols[4].text.strip() if len(cols) > 4 else None
            })

        # 將數據轉換為 DataFrame
        df = pd.DataFrame(data)

        # 移除空的目標價格變化
        df = df.dropna(subset=['Price Target Change'])

        # 清理數據，替換特殊字符
        df['Price Target Change'] = df['Price Target Change'].str.replace('→', '->').str.replace(' ', '')

        # 將目標價格變化轉換為數值範圍
        price_change_ranges = df['Price Target Change'].str.extract(r'\$(\d+)->\$(\d+)')
        price_change_ranges = price_change_ranges.apply(pd.to_numeric)
        df['Price Target Start'] = price_change_ranges[0]
        df['Price Target End'] = price_change_ranges[1]

        # 動態生成評級變化的順序
        rating_order = df['Rating Change'].unique().tolist()
        df['Rating Change'] = pd.Categorical(df['Rating Change'], categories=rating_order, ordered=True)

        # 可視化 1：分析師的目標價格變化
        fig1 = go.Figure()
        for i, row in df.iterrows():
            fig1.add_trace(go.Scatter(
                x=[row['Price Target Start'], row['Price Target End']],
                y=[row['Analyst'], row['Analyst']],
                mode='lines+markers+text',
                line=dict(color='blue' if row['Price Target End'] >= row['Price Target Start'] else 'red', width=2),
                marker=dict(size=10, color='blue' if row['Price Target End'] >= row['Price Target Start'] else 'red'),
                text=[f"${row['Price Target Start']}", f"${row['Price Target End']}"],
                textposition="top center"
            ))

        fig1.update_layout(
            title=f'機構對{symbol}目標價格變化',
            xaxis_title='目標價格',
            yaxis_title='機構',
            yaxis=dict(type='category'),
            showlegend=False
        )

        # 可視化 2：評級變化的分佈，使用不同顏色
        fig2 = px.histogram(
            df,
            x='Rating Change',
            title=f'機構評級{symbol}變化分佈',
            color='Rating Change',
            category_orders={'Rating Change': rating_order}
            )  # 明確排序順序
        
        fig2.update_layout(showlegend=False)
    
        # 顯示圖表
        st.plotly_chart(fig1)
        st.plotly_chart(fig2)

        # 顯示評級數據
        with st.expander(f"機構評級{symbol}變化分佈數據"):
            st.table(df)

# 9.相關新聞
class News:
    def getnews(self, symbol):
        url = f"https://finviz.com/quote.ashx?t={symbol}&p=d"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        
        # 發送請求並處理可能的錯誤
        try:
            response = res.get(url, headers=headers)
            response.raise_for_status()  # 確保請求成功
        except res.exceptions.RequestException as e:
            st.error(f"無法獲取 {symbol} 相關消息: {e}")
            return None
        
        # 解析頁面內容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尋找新聞表格
        news_table = soup.find('table', class_='fullview-news-outer')
        if news_table is None:
            st.error(f"無法獲取 {symbol} 相關新聞表格")
            return None
        
        # 獲取新聞項目
        news_items = news_table.find_all('tr')
        news_data = []
        
        for news_item in news_items:
            cells = news_item.find_all('td')
            if len(cells) < 2:
                continue
            
            # 提取新聞的日期和標題
            date_info = cells[0].text.strip()
            news_link = cells[1].find('a', class_='tab-link-news')
            
            if news_link:
                news_title = news_link.text.strip()
                news_url = news_link['href']
                news_data.append({
                    'Date': date_info,
                    'Title': news_title,
                    'URL': news_url
                })
        
        return news_data

#streamlit版面配置
def app():
    st.set_page_config(page_title="MarketInfo", layout="wide", page_icon="📈")
    hide_menu_style = "<style> footer {visibility: hidden;} </style>"
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: rainbow;'>📈 MarketInfo</h1>", unsafe_allow_html=True)
    st.subheader(' ',divider="rainbow")
    st.sidebar.title('📊 Menu')
    options = st.sidebar.selectbox('選擇功能', ['大盤指數','公司基本資訊','公司經營狀況','公司財報','交易數據','期權數據','SEC文件','機構買賣','近期相關消息'])
    st.sidebar.markdown('''
    ### 免責聲明：
    1. **K 線圖觀看角度**  
    - 綠漲、紅跌  
    2. 本平台僅適用於數據搜尋，不建議任何投資行為  
    3. 排版問題建議使用電腦查詢數據  
    4. 其他專案：[MarketSearch](https://marketsearch.streamlit.app)  
    ''')

    if  options == '大盤指數':
        period = st.selectbox('選擇時長',['年初至今','1年','2年','5年','10年','全部'])
        if period == '年初至今':
            period = 'ytd'
            time = '年初至今'
        elif period == '1年':
            period = '1y'
            time = '1年'
        elif period == '2年':
            period = '2y'
            time = '2年'
        elif period == '5年':
            period = '5y'
            time = '5年'
        elif period == '10年':
            period = '10y'
            time = '10年'
        elif period == '全部':
            period = 'max'
            time = '全部'
            
        # 繪製大盤指數
        pltindex = plotindex(period, time, plot_type='index')
        pltindex.plot()
        with st.expander(f'展開{time}大盤指數數據'):
            data = pltindex.data
            data = pd.DataFrame(data)
            st.dataframe(data)
        # 繪製海外大盤
        pltforeign = plotindex(period, time, plot_type='foreign')
        pltforeign.plot()
        with st.expander(f'展開{time}海外大盤指數數據'):
            data = pltforeign.data
            data = pd.DataFrame(data)
            st.dataframe(data)
    
    elif options == '公司基本資訊':
        symbol = st.text_input('輸入美股代號').upper()
        if st.button('查詢'):
            if symbol:
                company = cominfo(symbol)
                translated_df = company.tran_info()  
                
                # 獲取地址資訊
                address = company.com_info.loc['address1'].values[0]
                city = company.com_info.loc['city'].values[0]
                country = company.com_info.loc['country'].values[0]
                
                # 獲取公司位置
                location = company.get_location(address, city, country)
                
                # 顯示翻譯後的資訊
                st.subheader(f"{symbol}-基本資訊")
                st.table(translated_df)
                
                # 顯示地圖
                if location:
                    st.subheader(f"{symbol}-位置")
                    company.display_map(location, translated_df)
                else:
                    st.error(f"無法獲取{symbol}位置。")

    elif  options == '公司經營狀況':
        symbol = st.text_input('輸入美股代號').upper()
        if st.button('查詢'):
                com＿mange.get_mange_info(symbol)
                st.markdown(f"[資料來源](https://finviz.com/quote.ashx?t={symbol})")
    
    elif options == '公司財報':
        with st.expander("展開輸入參數"):
            time_range = st.selectbox('選擇時長', ['年報', '季報'])
            if time_range == '年報':
                symbol = st.text_input("輸入美股代碼").upper()
            elif time_range == '季報':
                symbol = st.text_input("輸入美股代碼").upper()
        if st.button('查詢'):
            if time_range == '年報':
                translator = financialreport_y(symbol)
                translator.get_financial()
                translator.tran_financial()
                translator.display_financial()
            elif time_range == '季報':
                translator_quarterly = ffinancialreport_q(symbol)
                translator_quarterly.get_financial_q()
                translator_quarterly.tran_financial_q()
                translator_quarterly.display_financial_q()

    elif  options == '交易數據':
        with st.expander("展開輸入參數"):
            range = st.selectbox('長期/短期', ['長期', '短期','自訂範圍'])
            if range == '長期':
                symbol = st.text_input("輸入美股代碼").upper()
                time_range = st.selectbox('選擇時長', ['1年', '2年', '5年', '10年', '全部'])
                if time_range == '1年':
                    period = '1y'
                    period_days = 252
                elif time_range == '2年':
                    period = '2y'
                    period_days = 252 * 2
                elif time_range == '5年':
                    period = '5y'
                    period_days = 252 * 5
                elif time_range == '10年':
                    period = '10y'
                    period_days = 252 * 10
                elif time_range == '全部':
                    period = 'max'
                    period_days = None  # 使用全部数据的长度

            elif range == '短期':
                symbol = st.text_input("輸入美股代碼").upper()
                time_range = st.selectbox('選擇時長',['年初至今','1個月','3個月','6個月'])
                if time_range == '年初至今':
                    period = 'ytd'
                    period_days = None
                elif time_range == '1個月':
                    period = '1mo'
                    period_days = 21  # 一个月大约是21个交易日
                elif time_range == '2個月':
                    period = '2mo'
                    period_days = 42
                elif time_range == '3個月':
                    period = '3mo'
                    period_days = 63  # 三个月大约是63个交易日
                elif time_range == '6個月':
                    period = '6mo'
                    period_days = 126  # 六个月大约是126个交易日

            elif range == '自訂範圍':
                symbol = st.text_input("輸入美股代碼").upper()
                start_date = st.date_input('開始日期')
                end_date = st.date_input('結束日期')
                time_range = f'{start_date}~{end_date}'
                if start_date and end_date:
                    period_days = (end_date - start_date).days
      
        if st.button("查詢"):
            if symbol:
                # 获取股票数据
                if range == '長期' or range == '短期':
                    stock_data = tradedata.getdata(symbol, period)
                    st.subheader(f"{symbol}-{time_range}交易數據")
                elif range == '自訂範圍':
                    stock_data = tradedata.getdata_timerange(symbol, start_date, end_date)
                    st.subheader(f"{symbol}-{start_date}～{end_date}交易數據")

                if stock_data is not None and not stock_data.empty:
                    if period_days is None:
                        period_days = len(stock_data)  # 更新 period_days 为 stock_data 的长度
                    price_difference, percent_difference = tradedata.calculate_difference(stock_data, period_days)
                    
                    latest_close_price = stock_data.iloc[-1]["Adj Close"]
                    
                    highest_price = stock_data["High"].max()
                    lowest_price = stock_data["Low"].min()

                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("最新收盤價", f"${latest_close_price:.2f}")
                    with col2:
                        st.metric(f"{time_range}增長率", f"${price_difference:.2f}", f"{percent_difference:+.2f}%")
                    with col3:
                        st.metric(f"{time_range}最高價", f"${highest_price:.2f}")
                    with col4:
                        st.metric(f"{time_range}最低價", f"${lowest_price:.2f}")
                    st.subheader(f"{symbol}-{time_range}K線圖表")
                    tradedata.plot_kline(stock_data)
                else:
                    st.error(f'查無{symbol}數據')
                with st.expander(f'展開{symbol}-{time_range}數據'):
                    st.dataframe(stock_data)
    
    elif options == '期權數據':
        if 'symbol' not in st.session_state:
            st.session_state.symbol = ''
        
        if st.session_state.symbol == '':
            symbol = st.text_input('輸入美股代號').upper()
            if st.button('查詢'):
                st.session_state.symbol = symbol  # 保存查詢的 symbol
        else:
            symbol = st.session_state.symbol
        
        if symbol:
            opion = Option(symbol)
            option_dates = opion.get_option_dates()
            df = pd.DataFrame(option_dates, columns=['可用日期'])
            st.subheader(f'{symbol} 期權到期日期')
            st.table(df)
            date = st.date_input('選擇日期（請依照上面日期選擇）')
            date_str = date.strftime('%Y-%m-%d')  # 將日期轉換為字符串進行比較

            if date_str in option_dates:
                st.subheader(f'{symbol}買權資訊（到期日：{date_str})')
                st.dataframe( opion.options_calls_date(date_str))
                st.subheader(f'{symbol}賣權資訊（到期日：{date_str})')
                st.dataframe(opion.options_puts_date(date_str))
            else:
                st.error('查無相關日期期權')
            
            if st.button('重新查詢'):
                st.session_state.symbol = ''  # 清除 symbol 以便重新輸入

    elif options == 'SEC文件':
        symbol = st.text_input('輸入美股代號').upper()
        if st.button('查詢'):
            sec = secreport(symbol)
            sec.display_filings()

    elif  options == '機構買賣':
        symbol = st.text_input('輸入美股代號').upper()
        if st.button('查詢'):
            holding = Holding(symbol)
            holding.holder(symbol)
            holding.fund_holder(symbol)
            holding.scrape_finviz(symbol)
            st.markdown(f"[資料來源](https://finviz.com/quote.ashx?t={symbol})")

    elif  options == '近期相關消息':
        symbol = st.text_input('輸入美股代號').upper()
        if st.button('查詢'):
            if symbol:
                news_data = News()
                news_data = news_data.getnews(symbol)
                if news_data:
                    # 将新闻数据转换为DataFrame
                    df = pd.DataFrame(news_data)
                    st.subheader(f"{symbol}-近期相關消息")
                    st.write(df)  # 显示表格
                    # 打印所有新闻链接
                    with st.expander(f'展開{symbol}-近期相關消息連結'):
                        for news in news_data:
                            st.write(f'**[{news["Title"]}]({news["URL"]})**')
                    st.markdown(f"[資料來源](https://finviz.com/quote.ashx?t={symbol})")
                else:
                    st.write(f"查無{symbol}近期相關消息")

if __name__ == "__main__":
    app()
