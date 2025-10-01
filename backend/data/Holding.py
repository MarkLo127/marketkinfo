# 資料分析
import pandas as pd  # 資料處理

# 資料擷取與網路相關
import yfinance as yf  # 股票數據
from finvizfinance.quote import finvizfinance

# 畫圖相關
import plotly.graph_objs as go  # Plotly 圖表物件
import plotly.express as px  # Plotly 快速繪圖
from plotly.subplots import make_subplots  # 子圖支援
import plotly  # Plotly 主模組

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組

# 8.機構評級
class Holding:
    tran_dict = {
        "Date Reported": "報告日期",
        "Holder": "持有人",
        "pctHeld": "持股比例",
        "Shares": "股份數",
        "Value": "價值",
        "Date": "日期",
        "Status": "動作",
        "Outer": "分析機構",
        "Rating": "評級變化",
        "Price": "目標價格變化",
        "Price Start": "目標價格起始",
        "Price End": "目標價格結束",
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
        data = finvizfinance(symbol).ticker_outer_ratings()  # 獲取外部評級數據
        df = pd.DataFrame(data).dropna(subset=["Price"])
        df["Price"] = (
            df["Price"].str.replace("→", "->").str.replace(" ", "")
        )

        if df["Price"].str.contains(r"\$").any():
            price_change_ranges = df["Price"].str.extract(
                r"\$(\d+)->\$(\d+)"
            )
            price_change_ranges = price_change_ranges.apply(
                pd.to_numeric, errors="coerce"
            )

            df["Price Start"] = price_change_ranges[0]
            df["Price End"] = price_change_ranges[1]

            # 設置評級的順序
            rating_order = df["Rating"].unique().tolist()
            df["Rating"] = pd.Categorical(
                df["Rating"], categories=rating_order, ordered=True
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