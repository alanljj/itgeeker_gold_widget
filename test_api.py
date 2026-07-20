from gold_api import fetch_gold_price, fetch_yahoo_gc, fetch_sina_au9999, fetch_goldprice_org

print("--- 测试各数据源 ---")

r1 = fetch_sina_au9999()
if r1:
    print(f"新浪Au9999: price={r1.price} {r1.unit}  err='{r1.error}'  src={r1.source}")
else:
    print("新浪Au9999: None")

r2 = fetch_goldprice_org("CNY")
if r2:
    print(f"GoldPrice CNY: price={r2.price} {r2.unit}  err='{r2.error}'  src={r2.source}")
else:
    print("GoldPrice CNY: None")

r3 = fetch_yahoo_gc()
if r3:
    print(f"Yahoo GC=F: price={r3.price} {r3.unit}  err='{r3.error}'  src={r3.source}")
else:
    print("Yahoo GC=F: None")

print()
d = fetch_gold_price("CNY")
if d.error:
    print("最终结果 ERROR:", d.error)
else:
    sign = "+" if d.change >= 0 else ""
    print(f"最终结果: {d.price} {d.unit}  涨跌:{sign}{d.change} ({sign}{d.change_pct}%)  来源:{d.source}")
