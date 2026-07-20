"""
ITGeeker Gold Widget - 黄金价格数据获取模块
数据源（按优先级）:
  1. 新浪财经 Au9999（人民币/克）
  2. GoldPrice.org JSON（人民币/克 或 美元/盎司）
  3. Yahoo Finance GC=F（美元/盎司）→ 可选汇率转换
开发者: 技术奇客ITGeeker.net
版本: v1.3.1.0
"""

import requests
import json
import re
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------
class GoldPriceData:
    """黄金价格数据容器"""

    def __init__(self):
        self.price: float = 0.0
        self.open_price: float = 0.0
        self.change: float = 0.0
        self.change_pct: float = 0.0
        self.high: float = 0.0
        self.low: float = 0.0
        self.prev_close: float = 0.0
        self.currency: str = "CNY"
        self.unit: str = "元/克"
        self.timestamp: datetime = datetime.now()
        self.source: str = ""
        self.error: str = ""

    @property
    def is_up(self) -> bool:
        return self.change >= 0


# ---------------------------------------------------------------------------
# 通用请求辅助
# ---------------------------------------------------------------------------
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _get(url: str, timeout=10, extra_headers: dict = None, encoding=None) -> Optional[requests.Response]:
    h = dict(_HEADERS)
    if extra_headers:
        h.update(extra_headers)
    try:
        resp = requests.get(url, headers=h, timeout=timeout)
        if encoding:
            resp.encoding = encoding
        return resp
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 数据源 1：新浪财经 Au9999（CNY/克）
# ---------------------------------------------------------------------------
def fetch_sina_au9999(timeout=10) -> Optional[GoldPriceData]:
    resp = _get(
        "https://hq.sinajs.cn/list=Au9999",
        timeout=timeout,
        extra_headers={"Referer": "https://finance.sina.com.cn"},
        encoding="gbk",
    )
    if not resp:
        return None
    try:
        content = resp.text.split('"')[1]
        parts = content.split(",")
        if len(parts) < 9:
            return None

        d = GoldPriceData()
        d.currency = "CNY"
        d.unit = "元/克"
        d.open_price = float(parts[1])
        d.prev_close = float(parts[2])
        d.price = float(parts[3])
        d.high = float(parts[4])
        d.low = float(parts[5])
        d.change = round(d.price - d.prev_close, 3)
        d.change_pct = round(d.change / d.prev_close * 100, 3) if d.prev_close else 0.0
        d.timestamp = datetime.now()
        d.source = "新浪财经(Au9999)"
        return d
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 数据源 2：GoldPrice.org JSON（支持 CNY / USD）
# ---------------------------------------------------------------------------
def fetch_goldprice_org(currency="CNY", timeout=10) -> Optional[GoldPriceData]:
    cur = currency.upper()
    resp = _get(f"https://data-asg.goldprice.org/dbXRates/{cur}", timeout=timeout)
    if not resp:
        return None
    try:
        data = resp.json()
        item = data["items"][0]
        price_oz = float(item["xauPrice"])
        chg_oz = float(item["chgXau"])
        pct = float(item["pcXau"])

        d = GoldPriceData()
        d.currency = cur
        if cur == "CNY":
            factor = 31.1035
            d.unit = "元/克"
            d.price = round(price_oz / factor, 3)
            d.change = round(chg_oz / factor, 3)
        else:
            d.unit = "$/oz"
            d.price = round(price_oz, 2)
            d.change = round(chg_oz, 2)

        d.change_pct = round(pct, 3)
        d.open_price = round(d.price - d.change, d.currency == "CNY" and 3 or 2)
        d.timestamp = datetime.now()
        d.source = f"GoldPrice.org({cur})"
        return d
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 数据源 3：Yahoo Finance GC=F（USD/oz）+ 可选汇率转换
# ---------------------------------------------------------------------------
def fetch_yahoo_gc(timeout=12) -> Optional[GoldPriceData]:
    """Yahoo Finance 期货 GC=F（COMEX 黄金，美元/盎司）"""
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
        "?interval=1d&range=1d&includePrePost=false"
    )
    resp = _get(url, timeout=timeout)
    if not resp:
        # 尝试备用域名
        url2 = (
            "https://query2.finance.yahoo.com/v8/finance/chart/GC=F"
            "?interval=1d&range=1d&includePrePost=false"
        )
        resp = _get(url2, timeout=timeout)
    if not resp:
        return None
    try:
        j = resp.json()
        result = j["chart"]["result"][0]
        meta = result["meta"]

        price = float(meta.get("regularMarketPrice", 0))
        prev_close = float(meta.get("chartPreviousClose", 0) or meta.get("previousClose", 0))
        if not price:
            return None

        change = round(price - prev_close, 2) if prev_close else 0.0
        change_pct = round(change / prev_close * 100, 3) if prev_close else 0.0

        d = GoldPriceData()
        d.currency = "USD"
        d.unit = "$/oz"
        d.price = price
        d.prev_close = prev_close
        d.open_price = float(meta.get("regularMarketOpen", prev_close) or prev_close)
        d.high = float(meta.get("regularMarketDayHigh", 0) or 0)
        d.low = float(meta.get("regularMarketDayLow", 0) or 0)
        d.change = change
        d.change_pct = change_pct
        d.timestamp = datetime.now()
        d.source = "Yahoo Finance(GC=F)"
        return d
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 辅助：获取 USD/CNY 汇率（Yahoo Finance）
# ---------------------------------------------------------------------------
def fetch_usd_cny_rate(timeout=8) -> Optional[float]:
    resp = _get(
        "https://query1.finance.yahoo.com/v8/finance/chart/USDCNY=X"
        "?interval=1d&range=1d",
        timeout=timeout,
    )
    if not resp:
        return None
    try:
        j = resp.json()
        rate = j["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return float(rate)
    except Exception:
        return None


def convert_usd_oz_to_cny_gram(data: GoldPriceData) -> GoldPriceData:
    """将 USD/oz 数据转换为 CNY/克"""
    rate = fetch_usd_cny_rate()
    if not rate:
        rate = 7.25  # 保底汇率

    factor = 31.1035
    new = GoldPriceData()
    new.currency = "CNY"
    new.unit = "元/克"
    new.price = round(data.price * rate / factor, 3)
    new.open_price = round(data.open_price * rate / factor, 3)
    new.high = round(data.high * rate / factor, 3) if data.high else 0.0
    new.low = round(data.low * rate / factor, 3) if data.low else 0.0
    new.change = round(data.change * rate / factor, 3)
    new.change_pct = data.change_pct
    new.prev_close = round(data.prev_close * rate / factor, 3)
    new.timestamp = data.timestamp
    new.source = data.source + f" (汇率≈{rate:.4f})"
    return new


# ---------------------------------------------------------------------------
# 统一对外接口（带故障转移）
# ---------------------------------------------------------------------------
def fetch_gold_price(currency: str = "CNY") -> GoldPriceData:
    """
    获取黄金价格，依次尝试多个数据源
    currency: "CNY" 或 "USD"
    """
    currency = currency.upper()

    if currency == "USD":
        # USD 模式：Yahoo → GoldPrice.org
        for fn in [fetch_yahoo_gc, lambda: fetch_goldprice_org("USD")]:
            result = fn()
            if result and not result.error:
                return result

    else:  # CNY 模式
        # 1. 新浪 Au9999（最准确）
        result = fetch_sina_au9999()
        if result and not result.error:
            return result

        # 2. GoldPrice.org CNY
        result = fetch_goldprice_org("CNY")
        if result and not result.error:
            return result

        # 3. Yahoo USD 转换为 CNY
        result = fetch_yahoo_gc()
        if result and not result.error:
            return convert_usd_oz_to_cny_gram(result)

    # 全部失败
    err = GoldPriceData()
    err.currency = currency
    err.unit = "元/克" if currency == "CNY" else "$/oz"
    err.error = "价格获取失败，请检查网络"
    err.timestamp = datetime.now()
    return err
