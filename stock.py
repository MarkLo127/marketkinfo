from data.plotindex import *
from data.cominfo import *
from data.financialreport_y import *
from data.financialreport_q import *
from data.tradedata import *
from data.Other import *
from data.Option import *
from data.Holding import *
from data.News import *
from data.secreport import *

import streamlit as st

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
        time_range = st.selectbox("選擇期間", ["短期","長期"])              
        elif time_range == "短期":
            period = st.selectbox("選擇時長", ["1天","5天","1個月","3個月","6個月","年初至今"])
            if period == "1天":
                period = "1d"
                time = "1天"
            elif period == "5天":
                period = "5d"
                time = "5天"
            elif period == "1個月":
                period = "1mo"
                time = "1個月"
            elif period == "3個月":
                period = "3mo"
                time = "3個月"
            elif period == "6個月":
                period = "6mo"
                time = "6個月"
            elif period == "年初至今":
                period = "ytd"
                time = "年初至今"
                
        elif time_range == "長期":
            period = st.selectbox("選擇時長", ["1年", "2年", "5年", "10年", "全部"])
            if period == "1年":
                period = "1y"
                time = "1年"
            elif period == "2年":
                period = "2y"
                time = "2年"
            elif period == "5年":
                period = "5y"
                time = "5年"
            elif  period == "10年":
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
