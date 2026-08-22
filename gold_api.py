"""
ITGeeker Gold Widget - 黄金价格数据获取模块
数据源（按优先级）:
  1. 东方财富 push2 JSONP（secid=118.AU9999，上海黄金交易所 Au9999）
  2. 新浪 ETF 518880（华安黄金，跟踪 SGE Au9999，跟踪误差 <0.5%）
  3. 新浪财经 Au9999（人民币/克）
  4. GoldPrice.org JSON（人民币/克 或 美元/盎司）
  5. Yahoo Finance GC=F（美元/盎司）→ 可选汇率转换
开发者: 技术奇客ITGeeker.net
版本: v1.3.5.0
"""

import requests
import json
import re
import time
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
# 数据源 1：东方财富 push2 JSONP（secid=118.AU9999，上海黄金交易所 Au9999）
# ---------------------------------------------------------------------------
# 多个 ut 候选，模拟不同浏览器指纹（push2 风控时轮换）
_EASTMONEY_UT_CANDIDATES = [
    "fa5fd054e8e60d3c5f10c1e7c7c1e7c7",
    "bd1d9dd1ddcddd89c8b9949a33c0e21a",
    "b288da1e9e85e1e1e85e1e1e85e1e1e1",
]

# push2 主域被风控时备用的镜像
_EASTMONEY_HOSTS = [
    "https://push2.eastmoney.com",
    "https://82.push2.eastmoney.com",
    "https://83.push2.eastmoney.com",
    "https://84.push2.eastmoney.com",
]


def _try_eastmoney_once(host: str, ut: str, fields: str, timeout: int) -> Optional[dict]:
    """尝试一次 push2 调用，返回解析后的 data 字典或 None。"""
    ts = int(time.time() * 1000)
    cb = f"jQuery1124{ts % 100000000}_{ts}"
    url = (
        f"{host}/api/qt/stock/get"
        f"?secid=118.AU9999"
        f"&fields={fields}"
        f"&invt=2&fltt=2"
        f"&cb={cb}"
        f"&_={ts}"
        f"&ut={ut}"
    )
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Referer": "https://quote.eastmoney.com/globalfuture/AU9999.html",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
            },
            timeout=timeout,
        )
    except Exception:
        return None
    if resp.status_code != 200:
        return None
    # JSONP 形如：jQuery1234({...}); 或 ({...});
    m = re.search(r"\(({.*})\)\s*;?\s*$", resp.text.strip(), re.DOTALL)
    if not m:
        return None
    try:
        payload = json.loads(m.group(1))
    except Exception:
        return None
    return payload.get("data") if isinstance(payload, dict) else None


def fetch_eastmoney_au9999(timeout=10) -> Optional[GoldPriceData]:
    """
    东方财富 push2 JSONP 实时行情（secid=118.AU9999，上海黄金交易所 Au9999）。
    解析字段含义（参考 push2 文档 + 实际数据反推）：
      f43  = 当前价 × 1000 （元/克，3 位小数）
      f60  = 昨收 × 1000
      f45  = 今开 × 1000
      f44  = 最高 × 1000
      f46  = 最低 × 1000
      f170 = 涨跌额 × 1000
      f169 = 涨跌幅 × 100   （百分比，已含小数位）
      f171 = 振幅 × 100
    """
    fields = "f43,f44,f45,f46,f48,f60,f168,f169,f170,f171,f86,f292"
    for host in _EASTMONEY_HOSTS:
        for ut in _EASTMONEY_UT_CANDIDATES:
            d = _try_eastmoney_once(host, ut, fields, timeout)
            if not d:
                continue
            f43 = d.get("f43")
            if not f43 or f43 <= 0:
                continue
            price = float(f43) / 1000.0
            prev_close = float(d.get("f60", 0) or 0) / 1000.0
            open_price = float(d.get("f45", 0) or 0) / 1000.0
            high = float(d.get("f44", 0) or 0) / 1000.0
            low = float(d.get("f46", 0) or 0) / 1000.0

            # 涨跌额/涨跌幅：优先用 push2 给的，没有就用现价-昨收推算
            change_from_api = float(d.get("f170", 0) or 0) / 1000.0
            pct_from_api = float(d.get("f169", 0) or 0) / 100.0
            if abs(change_from_api) > 0.001:
                change = change_from_api
            elif prev_close > 0:
                change = round(price - prev_close, 3)
            else:
                change = 0.0

            if abs(pct_from_api) > 0.001:
                change_pct = pct_from_api
            elif prev_close > 0:
                change_pct = round(change / prev_close * 100, 3)
            else:
                change_pct = 0.0

            out = GoldPriceData()
            out.currency = "CNY"
            out.unit = "元/克"
            out.price = round(price, 3)
            out.prev_close = round(prev_close, 3)
            out.open_price = round(open_price, 3)
            out.high = round(high, 3)
            out.low = round(low, 3)
            out.change = round(change, 3)
            out.change_pct = round(change_pct, 3)
            out.timestamp = datetime.now()
            out.source = "东方财富(AU9999·SGE)"
            return out
    return None


# ---------------------------------------------------------------------------
# 数据源 2：新浪黄金 ETF 518880（华安黄金，跟踪 SGE Au9999，跟踪误差 <0.5%）
# ---------------------------------------------------------------------------
def fetch_sina_etf_518880(timeout=8) -> Optional[GoldPriceData]:
    """
    通过新浪行情接口拉取上交所黄金 ETF 518880（华安黄金）的实时报价，
    ETF 单位 元/份（1 份 ≈ 0.01 克 Au9999），故 Au9999 元/克 = ETF × 100。

    华安黄金 ETF 518880 紧密跟踪上海黄金交易所 Au9999 现货合约，
    是国内最能实时反映 Au9999 价格的公开数据源，跟踪误差年化 <0.5%。
    """
    resp = _get(
        "https://hq.sinajs.cn/list=sh518880",
        timeout=timeout,
        extra_headers={"Referer": "https://finance.sina.com.cn"},
        encoding="gbk",
    )
    if not resp:
        return None
    try:
        text = resp.text
        if '"' not in text:
            return None
        content = text.split('"')[1]
        if not content:
            return None
        parts = content.split(',')
        # 至少需要：name, open, prev_close, price, high, low
        if len(parts) < 6:
            return None

        # parts 字段含义（Sina 股票 34 段格式）：
        # [0]=名称 [1]=今开 [2]=昨收 [3]=现价 [4]=最高 [5]=最低 [6]=买一价 ...
        etf_open = float(parts[1])
        etf_prev_close = float(parts[2])
        etf_price = float(parts[3])
        etf_high = float(parts[4])
        etf_low = float(parts[5])

        if not etf_price:
            return None

        # ETF × 100 ≈ Au9999 元/克（含管理费与微小跟踪误差）
        factor = 100.0

        d = GoldPriceData()
        d.currency = "CNY"
        d.unit = "元/克"
        d.open_price = round(etf_open * factor, 3)
        d.prev_close = round(etf_prev_close * factor, 3)
        d.price = round(etf_price * factor, 3)
        d.high = round(etf_high * factor, 3)
        d.low = round(etf_low * factor, 3)
        d.change = round(d.price - d.prev_close, 3)
        d.change_pct = round(d.change / d.prev_close * 100, 3) if d.prev_close else 0.0
        d.timestamp = datetime.now()
        d.source = "新浪ETF(518880·华安黄金)"
        return d
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 数据源 2：新浪财经 Au9999（CNY/克）—— 已停推，作为兼容保留
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
        # 1. 东方财富 push2 JSONP（secid=118.AU9999，SGE Au9999 实时）
        result = fetch_eastmoney_au9999()
        if result and not result.error:
            return result

        # 2. 新浪 ETF 518880（跟踪 SGE Au9999，跟踪误差 <0.5%）
        result = fetch_sina_etf_518880()
        if result and not result.error:
            return result

        # 3. 新浪 Au9999（已停推，保留兼容）
        result = fetch_sina_au9999()
        if result and not result.error:
            return result

        # 4. GoldPrice.org CNY
        result = fetch_goldprice_org("CNY")
        if result and not result.error:
            return result

        # 5. Yahoo USD 转换为 CNY（兜底，会产生 ~1% 期货升水误差）
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
