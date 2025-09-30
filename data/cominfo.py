# -*- coding: utf-8 -*-
# 資料分析
import pandas as pd  # 資料處理
import json  # JSON 處理
import os

# 資料擷取與網路相關
import yfinance as yf  # 股票數據

# 地理與地圖相關
import folium  # 地圖繪製
from streamlit_folium import folium_static  # Folium 與 Streamlit 整合
from geopy.geocoders import Nominatim, Photon, ArcGIS  # 地理編碼
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable, GeocoderInsufficientPrivileges
from geopy.extra.rate_limiter import RateLimiter
from functools import lru_cache
import time

# Streamlit 前端框架
import streamlit as st  # Streamlit 模組


# ===============================
# 全域地理編碼設定（含備援）
# ===============================

# 是否啟用備援地理編碼器（Nominatim 失敗 → Photon → ArcGIS）
USE_FALLBACK_GEOCODER = True

# 注意：請換成你可以被聯絡的 email 或網站（符合 Nominatim 使用規範）
_USER_AGENT = "marketkinfo/1.0 (+mailto:your_email@example.com)"

# 主要：Nominatim
_GEOLocator = Nominatim(user_agent=_USER_AGENT, timeout=10)
_GEOCODE = RateLimiter(
    _GEOLocator.geocode,
    min_delay_seconds=1.0,   # Nominatim 建議 >= 1 秒
    max_retries=3,
    error_wait_seconds=2.0,
    swallow_exceptions=False
)

# 備援：Photon、ArcGIS（若不需要可關掉 USE_FALLBACK_GEOCODER）
_PHOTON = Photon(user_agent=_USER_AGENT, timeout=10)
_PHOTON_GEOCODE = RateLimiter(
    _PHOTON.geocode, min_delay_seconds=1.0, max_retries=2, error_wait_seconds=2.0, swallow_exceptions=False
)
_ARCGIS = ArcGIS(timeout=10)
_ARCGIS_GEOCODE = RateLimiter(
    _ARCGIS.geocode, min_delay_seconds=0.5, max_retries=2, error_wait_seconds=1.0, swallow_exceptions=False
)

# （可選）本地已知地標快取（避免每次都打 API；你可自行擴充）
_HARDCODED_COORDS = {
    # "完整地址字串（不分大小寫）": (緯度, 經度)
    "one apple park way, cupertino, united states": (37.3349, -122.0090),
}


@lru_cache(maxsize=1024)
def _geocode_once(provider: str, query: str):
    """對特定 provider + query 做記憶化，避免重複打 API。"""
    q = query.strip()
    if not q:
        return None
    if provider == "nominatim":
        return _GEOCODE(q)
    elif provider == "photon":
        return _PHOTON_GEOCODE(q)
    elif provider == "arcgis":
        return _ARCGIS_GEOCODE(q)
    else:
        return None


def _lookup_hardcoded(query: str):
    """先查本地硬編碼地標（完全不打 API）。"""
    key = query.lower().strip()
    return _HARDCODED_COORDS.get(key)


def _geocode_with_fallback(query: str):
    """三段式備援：Nominatim → Photon → ArcGIS，皆失敗回傳 None。"""
    # 0) 本地硬編碼
    hc = _lookup_hardcoded(query)
    if hc:
        return ("hardcoded", hc[0], hc[1])

    # 1) Nominatim
    try:
        loc = _geocode_once("nominatim", query)
        if loc:
            return ("nominatim", loc.latitude, loc.longitude)
    except (GeocoderTimedOut, GeocoderUnavailable, GeocoderInsufficientPrivileges):
        pass
    except Exception:
        pass

    if not USE_FALLBACK_GEOCODER:
        return (None, None, None)

    # 2) Photon
    try:
        loc = _geocode_once("photon", query)
        if loc:
            return ("photon", loc.latitude, loc.longitude)
    except Exception:
        pass

    # 3) ArcGIS
    try:
        loc = _geocode_once("arcgis", query)
        if loc:
            return ("arcgis", loc.latitude, loc.longitude)
    except Exception:
        pass

    return (None, None, None)


# ===============================
# 2.公司基本資訊
# ===============================
class cominfo:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.com_info = self.get_cominfo()

    def get_cominfo(self):
        """讀取公司詳情（相容 yfinance 舊 .info / 新 .get_info()），並保存為 df.json。"""
        stock = yf.Ticker(self.symbol)

        # 兼容不同版本 yfinance：優先使用 get_info()，退回 .info
        com_info = {}
        try:
            if hasattr(stock, "get_info"):
                com_info = stock.get_info() or {}
            else:
                com_info = getattr(stock, "info", {}) or {}
        except Exception as e:
            # 無法取得資訊時，避免整個中斷
            com_info = {}

        # 儲存 JSON（可用於除錯或離線查看）
        try:
            with open("df.json", "w", encoding="utf-8") as outfile:
                json.dump(com_info, outfile, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # 直接回傳 dict（若你想強制從檔案讀，也可打開以下程式碼）
        # with open("df.json", "r", encoding="utf-8") as infile:
        #     json_data = json.load(infile)
        # return json_data
        return com_info

    def categorize_info(self):
        """將公司資訊分門別類成五大區塊 + 其他。"""
        json_data = self.com_info or {}

        # 1. 基本資料
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

        # 2. 財務資訊
        financial_info = {
            "全職員工": json_data.get("fullTimeEmployees"),
            "市值": json_data.get("marketCap"),
            "總收入": json_data.get("totalRevenue"),
            "總現金": json_data.get("totalCash"),
            "總負債": json_data.get("totalDebt"),
            "自由現金流": json_data.get("freeCashflow"),
            "營運現金流": json_data.get("operatingCashflow"),
            "每股收入": json_data.get("revenuePerShare"),
            "每股帳面價值": json_data.get("bookValue"),
            "負債股權比率": json_data.get("debtToEquity"),
            "總利潤率": json_data.get("grossMargins"),
            "營業利潤率": json_data.get("operatingMargins"),
            "資產回報率": json_data.get("returnOnAssets"),
            "股東權益報酬率": json_data.get("returnOnEquity"),
        }

        # 3. 風險與股東資訊
        risk_info = {
            "審計風險": json_data.get("auditRisk"),
            "董事會風險": json_data.get("boardRisk"),
            "薪酬風險": json_data.get("compensationRisk"),
            "股東權利風險": json_data.get("shareHolderRightsRisk"),
            "內部人持股比例": json_data.get("heldPercentInsiders"),
            "機構持股比例": json_data.get("heldPercentInstitutions"),
        }

        # 4. 高管資訊（list）
        officers_info = json_data.get("companyOfficers", []) or []

        # 5. 市場與股價資訊
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

        # 其他資訊
        other_info = {
            "企業價值": json_data.get("enterpriseValue"),
            "每股收益（過去）": json_data.get("trailingEps"),
            "每股收益（預測）": json_data.get("forwardEps"),
            "盈利增長": json_data.get("earningsGrowth"),
            "收入增長": json_data.get("revenueGrowth"),
            "貨幣": json_data.get("financialCurrency"),
        }

        return basic_info, financial_info, risk_info, officers_info, market_info, other_info

    def display_categorized_info(self):
        """顯示分類後的公司資訊（Streamlit）。"""
        basic_info, financial_info, risk_info, officers_info, market_info, other_info = self.categorize_info()

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

    def _candidate_queries(self, address: str, city: str, country: str):
        """組裝一系列地理查詢候選（從精確到粗略）。"""
        # 忽略空值，組裝查詢
        parts_full = [p for p in [address, city, country] if p]
        parts_city = [p for p in [city, country] if p]

        queries = []
        if parts_full:
            queries.append(", ".join(parts_full))
        if parts_city:
            queries.append(", ".join(parts_city))
        return queries

    def get_location(self, address, city, country):
        """
        取得公司地理座標：
        - 先查本地硬編碼
        - 再依序嘗試 Nominatim / Photon / ArcGIS（取決於 USE_FALLBACK_GEOCODER）
        - 過程中加入退避重試，不讓整個 App 因暫時性錯誤而崩潰
        - 全部失敗回傳 None
        """
        candidates = self._candidate_queries(address, city, country)
        if not candidates:
            return None

        # 先看完整地址是否存在本地硬編碼（降低 API 依賴）
        for q in candidates:
            hc = _lookup_hardcoded(q)
            if hc:
                return (hc[0], hc[1])

        # 逐一嘗試候選查詢：每個候選都做短暫退避重試
        for q in candidates:
            # 主要：帶備援的查詢
            try:
                src, lat, lon = _geocode_with_fallback(q)
                if src:
                    return (lat, lon)
            except (GeocoderTimedOut, GeocoderUnavailable, GeocoderInsufficientPrivileges):
                # 短暫錯誤 → 退避重試 2 次
                for i in range(2):
                    time.sleep(2 * (i + 1))
                    try:
                        src, lat, lon = _geocode_with_fallback(q)
                        if src:
                            return (lat, lon)
                    except (GeocoderTimedOut, GeocoderUnavailable, GeocoderInsufficientPrivileges):
                        continue
                    except Exception:
                        continue
            except Exception:
                # 其他不可預期錯誤：不中斷 app，換下一個候選
                continue

        # 全部失敗
        return None

    def display_map(self, location, company=None):
        """
        安全地顯示公司位置地圖：
        - location 為 (lat, lon) 或 None
        - None 時顯示提示，不讓應用崩潰
        """
        if not location:
            st.info(f"找不到 {self.symbol} 的定位資料，或地理服務暫時不可用。請稍後再試或檢查地址欄位是否完整。")
            return

        lat, lon = location
        m = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker(
            [lat, lon],
            tooltip=f"{self.symbol} Location",
        ).add_to(m)
        folium_static(m)