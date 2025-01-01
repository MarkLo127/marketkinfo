# 資料分析
import pandas as pd  # 資料處理
import json  # JSON 處理

# 資料擷取與網路相關
import yfinance as yf  # 股票數據

# 地理與地圖相關
import folium  # 地圖繪製
from streamlit_folium import folium_static  # Folium 與 Streamlit 整合
from geopy.geocoders import Nominatim  # 地理編碼
import geopy  # 地理位置查找
from geopy.exc import GeocoderInsufficientPrivileges

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組


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