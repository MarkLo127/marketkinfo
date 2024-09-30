# 資料分析
import pandas as pd  # 資料處理
import json  # JSON 處理

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

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

#1.大盤指數
class FinancialDataPlotter:
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
        for symbol in self.symbols[self.plot_type]:
            self.data[symbol] = yf.download(symbol, period=self.period)['Close']

    def plot_index(self):
        """Plot the US indexes."""
        st.header(f'美股大盤＆中小企業{self.time}走勢')

        # Create Plotly subplot figure for indexes
        fig = make_subplots(rows=3, cols=2, subplot_titles=["NASDAQ", "VIX", "S&P 500", "DJIA", "PHLX Semiconductor Sector", "Russell-2000"])

        for i, symbol in enumerate(self.symbols['index']):
            fig.add_trace(go.Scatter(x=self.data[symbol].index, y=self.data[symbol].values, mode='lines', name=symbol), row=(i // 2) + 1, col=(i % 2) + 1)

        fig.update_layout(height=1000, width=1000, showlegend=False)
        st.plotly_chart(fig)

    def plot_foreign(self):
        """Plot the foreign indexes."""
        st.header(f'美股大盤＆海外大盤{self.time}走勢')

        # Create Plotly subplot figure for foreign indexes
        fig = make_subplots(rows=3, cols=2, subplot_titles=["S&P 500", "NASDAQ", "恆生指數", "深證指數", "加權指數", "日經指數"])

        for i, symbol in enumerate(self.symbols['foreign']):
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            # Apply conversion for foreign indexes
            if symbol in ['^HSI', '399001.SZ', '^TWII', '^N225']:  
                conversion_factor = {'^HSI': 0.1382, '399001.SZ': 0.1382, '^TWII': 0.0308, '^N225': 0.0064}
                fig.add_trace(go.Scatter(x=self.data[symbol].index, y=(self.data[symbol] * conversion_factor[symbol]).values, mode='lines', name=symbol), row=row, col=col)
            else:
                fig.add_trace(go.Scatter(x=self.data[symbol].index, y=self.data[symbol].values, mode='lines', name=symbol), row=row, col=col)

        fig.update_layout(height=1000, width=1000, showlegend=False)
        st.plotly_chart(fig)

    def plot(self):
        """Plot the financial data based on the selected type."""
        self.fetch_data()
        if self.plot_type == 'index':
            self.plot_index()
        elif self.plot_type == 'foreign':
            self.plot_foreign()

#2.公司基本資訊
class CompanyInfo:
    translation_dict = {
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
        self.com_info = self.get_company_details()

    def get_company_details(self):
        """獲取公司的詳細資訊"""
        stock_info = yf.Ticker(self.symbol)
        com_info = stock_info.info

        # 儲存資訊為 JSON
        with open("df.json", "w") as outfile:
            json.dump(com_info, outfile)

        # 讀取資料並轉置
        df = pd.read_json("df.json").head(1).transpose()
        return df

    def translate_info(self):
        """翻譯公司資訊並格式化顯示"""
        translated_info = {}
        self.com_info.index = self.com_info.index.str.strip()  # 去除索引空格

        for key in self.translation_dict.keys():
            if key in self.com_info.index:
                value = self.com_info.loc[key].values[0]
                if isinstance(value, float):
                    if 'rate' in key or 'Growth' in key or 'Yield' in key:
                        value = f"{value * 100:.2f}%"  # 百分比格式
                    else:
                        value = f"{value:,.2f}"  # 千分位格式
                elif isinstance(value, int):
                    value = f"{value:,}"  # 千分位格式
                translated_info[self.translation_dict[key]] = value

        return pd.DataFrame.from_dict(translated_info, orient='index', columns=['內容'])

    def get_location(self, address, city, country):
        """獲取公司位置的經緯度"""
        geolocator = Nominatim(user_agent="company_locator")
        location = geolocator.geocode(f"{address}, {city}, {country}")
        return location

    def display_map(self, location, translated_df):
        """顯示公司位置的地圖"""
        m = folium.Map(location=[location.latitude, location.longitude], zoom_start=13)
        folium.Marker(
            [location.latitude, location.longitude],
            popup=translated_df.to_html(escape=False),
            tooltip='公司位置'
        ).add_to(m)
        folium_static(m)

#3.公司經營狀況
class StockAnalyzer:
    def get_stock_details_and_plot(symbol):
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
def financial_statements(symbol):
    try:
        stock_info = yf.Ticker(symbol)
        balance_sheet = stock_info.balance_sheet
        income_statement = stock_info.financials
        cash_flow = stock_info.cashflow

        return balance_sheet, income_statement, cash_flow
    except Exception as e:
        st.error(f"獲取{symbol}財務報表發生錯誤：{str(e)}")
        return None, None, None

# Function to display financial statements
def display_financial_statements(balance_sheet, income_statement, cash_flow):
    if balance_sheet is not None:
        st.subheader("資產負債表-年")
        st.table(balance_sheet)

    if income_statement is not None:
        st.subheader("綜合損益表-年")
        st.table(income_statement)

    if cash_flow is not None:
        st.subheader("現金流量表-年")
        st.table(cash_flow)

# Function to fetch financial statements quarterly
def financial_statements_quarterly(symbol):
    try:
        stock_info = yf.Ticker(symbol)
        quarterly_balance_sheet = stock_info.quarterly_balance_sheet
        quarterly_income_statement = stock_info.quarterly_income_stmt
        quarterly_cash_flow = stock_info.quarterly_cashflow  # Changed to fetch quarterly cash flow correctly

        return quarterly_balance_sheet, quarterly_income_statement, quarterly_cash_flow
    except Exception as e:
        st.error(f"獲取{symbol}財務報表發生錯誤：{str(e)}")
        return None, None, None

# Function to display financial statements
def display_financial_statements_quarterly(quarterly_balance_sheet, quarterly_income_statement, quarterly_cash_flow):
    if quarterly_balance_sheet is not None:
        st.subheader("資產負債表 - 季")
        st.table(quarterly_balance_sheet)

    if quarterly_income_statement is not None:
        st.subheader("綜合損益表 - 季")
        st.table(quarterly_income_statement)

    if quarterly_cash_flow is not None:
        st.subheader("現金流量表 - 季")
        st.table(quarterly_cash_flow)

# 5.交易數據
def get_stock_data(symbol,time_range):
    stock_data = yf.download(symbol,period=time_range)
    return stock_data

# 计算价格差异的函数
def calculate_price_difference(stock_data, period_days):
    latest_price = stock_data.iloc[-1]["Adj Close"]  # 获取最新的收盘价
    previous_price = stock_data.iloc[-period_days]["Adj Close"] if len(stock_data) > period_days else stock_data.iloc[0]["Adj Close"]  # 获取特定天数前的收盘价
    price_difference = latest_price - previous_price  # 计算价格差异
    percentage_difference = (price_difference / previous_price) * 100  # 计算百分比变化
    return price_difference, percentage_difference  # 返回价格差异和百分比变化

# 6.機構評級
def scrape_and_plot_finviz_data(symbol):
    # 爬虫部分
    url = f"https://finviz.com/quote.ashx?t={symbol}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = res.get(url, headers=headers)
    # 检查请求是否成功
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {url}, status code: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    # 定位包含分析师评级的表格
    table = soup.find('table', class_='js-table-ratings styled-table-new is-rounded is-small')
    # 检查是否成功找到表格
    if table is None:
        raise Exception("Failed to find the ratings table on the page.")
    
    # 从表格中提取数据
    data = []
    for row in table.find_all('tr')[1:]:  # 跳过表头
        cols = row.find_all('td')
        data.append({
            "Date": cols[0].text.strip(),
            "Action": cols[1].text.strip(),
            "Analyst": cols[2].text.strip(),
            "Rating Change": cols[3].text.strip(),
            "Price Target Change": cols[4].text.strip() if len(cols) > 4 else None
        })
    
    # 将数据转换为 DataFrame
    df = pd.DataFrame(data)
    # 移除空的目标价格变化
    df = df.dropna(subset=['Price Target Change'])
    # 清理数据，替换特殊字符
    df['Price Target Change'] = df['Price Target Change'].str.replace('→', '->').str.replace(' ', '')
    # 将目标价格变化转换为数值范围
    price_change_ranges = df['Price Target Change'].str.extract(r'\$(\d+)->\$(\d+)')
    price_change_ranges = price_change_ranges.apply(pd.to_numeric)
    df['Price Target Start'] = price_change_ranges[0]
    df['Price Target End'] = price_change_ranges[1]
    
    # 动态生成评级变化的顺序
    rating_order = df['Rating Change'].unique().tolist()
    
    df['Rating Change'] = pd.Categorical(df['Rating Change'], categories=rating_order, ordered=True)
    
    # 绘图部分
    # 可视化 1：分析师的目标价格变化
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
        title='機構目標價格變化',
        xaxis_title='目標價格',
        yaxis_title='機構',
        yaxis=dict(type='category'),
        showlegend=False,
        height=800,  # 增加图表高度
        width=1200   # 增加图表宽度
        )
    
    # 可视化 2：评级变化的分布，使用不同颜色
    fig2 = px.histogram(df, 
                        x='Rating Change', 
                        title='機構評級變化分佈', 
                        color='Rating Change',
                        category_orders={'Rating Change': rating_order})  # 明確排序順序
    
    fig2.update_layout(
        height=800,  # 增加图表高度
        width=1200   # 增加图表宽度
    )

    # 显示图表
    st.subheader(f'機構買賣{symbol}資訊')
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    with st.expander(f'展開{symbol}機構評級數據'):
        st.table(df)

# 7.相關新聞
def get_stock_news(symbol):
    url = f"https://finviz.com/quote.ashx?t={symbol}&p=d"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = res.get(url, headers=headers)
        response.raise_for_status()  # Ensure the request was successful
    except res.exceptions.RequestException as e:
        st.error(f"無法獲取{symbol}相關消息: {e}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find all news items
    news_table = soup.find('table', class_='fullview-news-outer')
    if news_table is None:
        st.error(f"無法獲取{symbol}相關新聞表格")
        return None
    news_items = news_table.find_all('tr')
    news_data = []
    for news_item in news_items:
        cells = news_item.find_all('td')
        if len(cells) < 2:
            continue
        date_info = cells[0].text.strip()
        news_link = cells[1].find('a', class_='tab-link-news')
        if news_link:
            news_title = news_link.text.strip()
            news_url = news_link['href']
            news_data.append({'Date': date_info, 'Title': news_title, 'URL': news_url})
    return news_data

#streamlit版面配置
def app():
    st.set_page_config(page_title="StockInfo", layout="wide", page_icon="📈")
    hide_menu_style = "<style> footer {visibility: hidden;} </style>"
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: rainbow;'>📈 StockInfo</h1>", unsafe_allow_html=True)
    st.header(' ',divider="rainbow")
    st.sidebar.title('📈 Menu')
    options = st.sidebar.selectbox('選擇功能', ['大盤指數','公司基本資訊','公司經營狀況','公司財報','交易數據','機構買賣','近期相關消息'])
    st.sidebar.markdown('''
    免責聲明：        
    1. K 線圖觀看角度      
            - 綠漲、紅跌        
    2. 本平台僅適用於數據搜尋，不建議任何投資行為
    3. 排版問題建議使用電腦查詢數據  
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
        plotter_index = FinancialDataPlotter(period, time, plot_type='index')
        plotter_index.plot()

        # 繪製海外大盤
        plotter_foreign = FinancialDataPlotter(period, time, plot_type='foreign')
        plotter_foreign.plot()
    
    elif options == '公司基本資訊':
        symbol = st.text_input('輸入美股代號').upper()
        if st.button('查詢'):
            if symbol:
                company = CompanyInfo(symbol)
                translated_df = company.translate_info()  
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
                StockAnalyzer.get_stock_details_and_plot(symbol)
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
                balance_sheet, income_statement, cash_flow = financial_statements(symbol)
                display_financial_statements(balance_sheet, income_statement, cash_flow)
            elif time_range == '季報':
                quarterly_balance_sheet, quarterly_income_statement, quarterly_cash_flow = financial_statements_quarterly(symbol)
                display_financial_statements_quarterly(quarterly_balance_sheet, quarterly_income_statement, quarterly_cash_flow)
              
    elif  options == '交易數據':
        with st.expander("展開輸入參數"):
            range = st.selectbox('長期/短期', ['長期', '短期'])
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
                time_range = st.selectbox('選擇時長',['1個月','3個月','6個月'])
                if time_range == '1個月':
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
        if st.button("查詢"):
            if symbol:
                # 获取股票数据
                stock_data = get_stock_data(symbol, period)
                st.header(f"{symbol}-{time_range}交易數據")
                if stock_data is not None and not stock_data.empty:
                    if period_days is None:
                        period_days = len(stock_data)  # 更新 period_days 为 stock_data 的长度
                    price_difference, percentage_difference = calculate_price_difference(stock_data, period_days)
                    latest_close_price = stock_data.iloc[-1]["Adj Close"]
                    highest_price = stock_data["High"].max()
                    lowest_price = stock_data["Low"].min()
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("最新收盤價", f"${latest_close_price:.2f}")
                    with col2:
                        st.metric(f"{time_range}增長率", f"${price_difference:.2f}", f"{percentage_difference:+.2f}%")
                    with col3:
                        st.metric(f"{time_range}最高價", f"${highest_price:.2f}")
                    with col4:
                        st.metric(f"{time_range}最低價", f"${lowest_price:.2f}")
                    st.subheader(f"{symbol}-{time_range}K線圖表")
                    fig = go.Figure()
                    fig = plotly.subplots.make_subplots(rows=4, cols=1,shared_xaxes=True,vertical_spacing=0.01,row_heights=[0.8,0.5,0.5,0.5])
                    mav5 = stock_data['Adj Close'].rolling(window=5).mean()  # 5日mav
                    mav20 = stock_data['Adj Close'].rolling(window=20).mean()  # 20日mav
                    mav60 = stock_data['Adj Close'].rolling(window=60).mean()  # 60日mav
                    rsi = RSIIndicator(close=stock_data['Adj Close'], window=14)
                    macd = MACD(close=stock_data['Adj Close'],window_slow=26,window_fast=12, window_sign=9)
                    fig.add_trace(go.Candlestick(x=stock_data.index,open=stock_data['Open'],high=stock_data['High'],low=stock_data['Low'],close=stock_data['Adj Close'],),row=1,col=1)
                    fig.update_layout(xaxis_rangeslider_visible=False)
                    fig.add_trace(go.Scatter(x=stock_data.index, y=mav5, opacity=0.7, line=dict(color='blue', width=2), name='MAV-5'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=stock_data.index, y=mav20, opacity=0.7,line=dict(color='orange', width=2), name='MAV-20'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=stock_data.index, y=mav60,  opacity=0.7, line=dict(color='purple', width=2),name='MAV-60'), row=1, col=1)
                    # Plot volume trace on 2nd row
                    colors = ['green' if row['Open'] - row['Adj Close'] >= 0 else 'red' for index, row in stock_data.iterrows()]
                    fig.add_trace(go.Bar(x=stock_data.index,y=stock_data['Volume'],marker_color=colors,name='Volume'),row=2, col=1)
                    # Plot RSI trace on 5th row
                    fig.add_trace(go.Scatter(x=stock_data.index,y=rsi.rsi(),line=dict(color='purple',width=2)),row=3,col=1)
                    fig.add_trace(go.Scatter(x=stock_data.index,y=[70]*len(stock_data.index),line=dict(color='red', width=1),name='Overbought'), row=3, col=1)
                    fig.add_trace(go.Scatter(x=stock_data.index,y=[30]*len(stock_data.index),line=dict(color='green', width=1),name='Oversold'), row=3, col=1)
                     # Plot MACD trace on 3rd row
                    colorsM = ['green' if val >= 0 else 'red' for val in macd.macd_diff()]
                    fig.add_trace(go.Bar(x=stock_data.index,y=macd.macd_diff(),marker_color=colorsM),row=4,col=1)
                    fig.add_trace(go.Scatter(x=stock_data.index,y=macd.macd(),line=dict(color='orange', width=2)),row=4,col=1)
                    fig.add_trace(go.Scatter(x=stock_data.index,y=macd.macd_signal(),line=dict(color='blue', width=1)),row=4,col=1)
                    fig.update_yaxes(title_text="Price", row=1, col=1)
                    fig.update_yaxes(title_text="Volume", row=2, col=1)
                    fig.update_yaxes(title_text="RSI", row=3, col=1)
                    fig.update_yaxes(title_text="MACD", row=4, col=1)
                    st.plotly_chart(fig,use_container_width=True)
                else:
                    st.error(f'查無{symbol}數據')
                with st.expander(f'展開{symbol}-{time_range}數據'):
                    st.dataframe(stock_data)
    
    elif  options == '機構買賣':
        symbol = st.text_input('輸入美股代號').upper()
        if st.button('查詢'):
            scrape_and_plot_finviz_data(symbol)
            st.markdown(f"[資料來源](https://finviz.com/quote.ashx?t={symbol})")

    elif  options == '近期相關消息':
        symbol = st.text_input('輸入美股代號').upper()
        if st.button('查詢'):
            if symbol:
                news_data = get_stock_news(symbol)
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
