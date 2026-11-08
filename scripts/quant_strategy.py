"""Reproducible daily-close research backtest and current investability screener.

Only price-history signals enter the HISTORICAL strategy (not current M7 edges,
valuation, or point-in-time-incomplete fundamental factors).
No backward interpolation, synthetic performance, or hindsight Alpha.
"""
from __future__ import annotations
import math
import statistics
from datetime import date

DEFAULT={"benchmark":"SPY","sector_benchmark":"XLK","top_n":8,
  "rebalance":"monthly","one_way_bps":10,"min_history":86,
  "max_price_age_days":7,"price_monitor_weight":.20,
  "supply_alpha_weight":.30,"growth_weight":.20,"valuation_weight":.15,
  "size_weight":.05,"risk_weight":.10}
SECTOR_BANDS={
 "AI compute":"AMD MRVL AVGO MU TSM QCOM CRUS SWKS ON NXPI MPWR MCHP STM".split(),
 "Semicap":"AMAT LRCX KLAC ASML ONTO ACLS ENTG MKSI FORM UCTT".split(),
 "Optics/network":"ANET COHR LITE FN GLW APH".split(),
 "Servers":"CLS DELL HPE SMCI".split(),
 "Infrastructure":"VRT ETN HUBB POWL GEV CEG VST".split()
}

def rank_pct(value,values):
    if value is None:return None
    xs=sorted(v for v in values if v is not None and math.isfinite(v))
    if len(xs)<3:return None
    return round(100*(sum(v<value for v in xs)+.5*sum(v==value for v in xs)-.5)/(len(xs)-1),4)

def ret(bars,n):
    if len(bars)<=n or bars[-n-1]<=0:return None
    return bars[-1]/bars[-n-1]-1

def volatility_daily(bars,window=60):
    if len(bars)<window+1:return None
    y=[bars[i]/bars[i-1]-1 for i in range(len(bars)-window,len(bars)) if bars[i-1]>0]
    if len(y)<window:return None
    return statistics.stdev(y) if len(y)>1 else None

def standalone_signal(stock,sector):
    """Research monitor: 20-session excess return vs XLK, 5-day return."""
    if not stock or not sector or len(stock)<65 or len(sector)<65:return None
    excess=(ret(stock,20) or 0)-(ret(sector,20) or 0)
    five=ret(stock,5)
    if five is None:return None
    return excess,five

def annual_growth(row):
    v=row.get("revenue_growth_yoy")
    if v is None:return None
    return max(-1.,min(float(v),3.)) if isinstance(v,(float,int)) and math.isfinite(v) else None

def investment_score(stocks,facts,meta,provisional=None):
    """Investor-oriented *screening* score; missing inputs never scored as zero.

    Financial input: SEC revenue FY, revenue growth, indication of market cap.
    Factors: 30% supply evidence Alpha (if present), 20% price monitor,
    20% growth, 15% price-to-sales value, 5% size, 10% inverse realized vol.
    Requires >75% weight and at least one fundamental factor to be rankable.
    """
    provisional=provisional or {}
    candidates={}
    for sym in stocks:
        row=meta.get(sym,{})
        point=facts.get(sym,{})
        rev=point.get("revenue_fy_usd")
        close=row.get("close")
        share=point.get("shares_outstanding")
        cap=(close*share if isinstance(close,(float,int)) and close>0 and isinstance(share,(float,int)) and share>0 and not point.get("foreign_adr_caution") else None)
        # Only an indicated cap; large SEC share counts may differ from today's shares.
        ps=cap/rev if cap and rev and rev>0 else None
        vals={
          "supply_alpha":row.get("provisional_alpha") if row.get("coverage",0)>=.45 else None,
          "monitor":row.get("monitor_score"),
          "growth":annual_growth(point),
          "value":math.log(ps) if ps and ps>0 else None,
          "size":math.log(cap) if cap and cap>0 else None,
          "risk":row.get("realized_vol_60d")
        }
        candidates[sym]={"raw":vals,"cap":cap,"ps":ps,
          "source":point.get("source"),"revenue":rev,"revenue_growth":annual_growth(point),
          "revenue_filed":point.get("revenue_filed"),"shares_filed":point.get("shares_filed"),
          "adr_caution":point.get("foreign_adr_caution",False),
          "price_source":row.get("price_source"),
          "price_date":row.get("price_date")}
    fields={"supply_alpha":.30,"monitor":.20,"growth":.20,"value":.15,"size":.05,"risk":.10}
    scores={s:{} for s in stocks}
    for factor in fields:
        values=[v["raw"][factor] for v in candidates.values()
                if isinstance(v["raw"][factor],(float,int)) and math.isfinite(v["raw"][factor])]
        for sym,v in candidates.items():
            x=v["raw"][factor]
            if x is None or not math.isfinite(x):scores[sym][factor]=None;continue
            scores[sym][factor]=(100-rank_pct(x,values)) if factor in ("value","risk") else rank_pct(x,values)
    output=[]
    for sym,v in candidates.items():
        available=[(f,w,scores[sym][f]) for f,w in fields.items() if scores[sym][f] is not None]
        weight=sum(w for _,w,_ in available)
        fundamental_covered=any(scores[sym].get(f) is not None for f in ("growth","value"))
        eligible=weight>=.75 and fundamental_covered
        score=(sum(w*x for _,w,x in available)/weight) if eligible else None
        output.append({"ticker":sym,"investability_score":round(score,2) if score is not None else None,
           "rank_eligible":eligible,"factor_coverage":round(weight,3),
           "component_scores":scores[sym], "weights":fields,
           "market_cap_proxy_usd":round(v["cap"]) if v["cap"] else None,
           "price_to_sales_proxy":round(v["ps"],3) if v["ps"] else None,
           "revenue_fy_usd":v["revenue"],
           "revenue_growth_yoy":v["revenue_growth"],
           "revenue_filed":v["revenue_filed"],"shares_filed":v["shares_filed"],
           "price_date":v["price_date"],"price_source":v["price_source"],
           "fundamental_source":v["source"],"adr_caution":v["adr_caution"],
           "status":"SCREENING_SCORE_ONLY_NOT_BACKTESTED" if eligible else "INSUFFICIENT_POINT_IN_TIME_FUNDAMENTALS"})
    output.sort(key=lambda x:(x["investability_score"] is None,-(x["investability_score"] or 0),x["ticker"]))
    for i,entry in enumerate([x for x in output if x["investability_score"] is not None],1):entry["rank"]=i
    return output

def _metrics(returns,turnovers,cost_bps,periods=252):
    if not returns:return None
    capital=[1.]
    for r in returns:capital.append(max(1e-10,capital[-1]*(1+r)))
    n=len(returns); mean=statistics.mean(returns); std=statistics.stdev(returns) if n>1 else 0
    peak=capital[0]; draw=[]
    for c in capital[1:]:
        peak=max(peak,c);draw.append(c/peak-1)
    downside=[min(r,0.) for r in returns]
    down_std=math.sqrt(sum(x*x for x in downside)/len(downside)) if downside else 0.
    total=capital[-1]-1
    annual=capital[-1]**(periods/n)-1
    return {"total_return":round(total,6),"cagr_annualized":round(annual,6),
      "annualized_volatility":round(std*math.sqrt(periods),6),
      "sharpe_rf0":round(mean/std*math.sqrt(periods),3) if std else None,
      "sortino_rf0":round(mean/down_std*math.sqrt(periods),3) if down_std else None,
      "max_drawdown":round(min(draw or [0]),6),
      "positive_day_rate":round(sum(r>0 for r in returns)/n,4),
      "days":n,"turnover_one_way":round(sum(turnovers),5),
      "total_transaction_cost_bps":round(cost_bps,4),
      "ending_nav":round(capital[-1],6)}

def simulate_daily_close(quotes,tickers,initial_date=None,top_n=8,trade_bps=10):
    """Monthly selection, next-session-close execution, no same-close fills.

    Date alignment by intersection with SPY and XLK.
    On rebalance day i, signal is from i-1 and next return is close i -> i+1.
    This is a current-universe diagnostic with survivorship bias; not a claim
    of unbiased historical investability or point-in-time universe.
    """
    benchmarks=("SPY","XLK")
    maps={t:dict(quotes.get(t,{}).get("bars") or []) for t in (*tickers,*benchmarks)}
    if any(len(maps[b])<100 for b in benchmarks):return {"status":"INSUFFICIENT_BENCHMARK_HISTORY","reason":"SPY/XLK close history not available"}
    dates=sorted(set(maps["SPY"])&set(maps["XLK"]))
    dates=[d for d in dates if all(maps[b][d]>0 for b in benchmarks)]
    if len(dates)<100:return {"status":"INSUFFICIENT_ALIGNED_HISTORY"}
    holdings={};returns=[];benchmark_returns=[];sector_returns=[];dates_ret=[];turnover=[];costs=[];trades=[];weights_history=[]
    missing_days=0
    start=85
    first=initial_date or dates[start]
    for i in range(start,len(dates)-1):
        day=dates[i]
        if day<first:continue
        rebalance=not returns or day[:7]!=dates[i-1][:7]
        tc=0.
        if rebalance:
            prev=dates[i-1]
            signal={};moment=[]
            for t in tickers:
                arr=[maps[t][d] for d in dates[:i] if d in maps[t] and maps[t][d]>0]
                b=[maps["XLK"][d] for d in dates[:i] if d in maps[t] and d in maps["XLK"] and maps[t][d]>0]
                if len(arr)<65 or len(b)<65:continue
                if prev not in maps[t]:continue
                five=ret(arr,5);twenty=ret(arr,20);sixty=ret(arr,60)
                if five is None or twenty is None or sixty is None:continue
                vol=volatility_daily(arr,60)
                if not vol or vol<=0:continue
                signal[t]=(five,twenty-ret(b,20),sixty,vol)
            for t,v in signal.items():
                others=list(signal.values())
                p5=rank_pct(v[0],[x[0] for x in others])
                p20=rank_pct(v[1],[x[1] for x in others])
                p60=rank_pct(v[2],[x[2] for x in others])
                risk=100-rank_pct(v[3],[x[3] for x in others])
                if None in (p5,p20,p60,risk):continue
                moment.append((.30*p5+.40*p20+.20*p60+.10*risk,t))
            moment.sort(key=lambda x:(-x[0],x[1]))
            chosen=[]
            sector_count={}
            for _,t in moment:
                sector=next((k for k,v in SECTOR_BANDS.items() if t in v),"other")
                if sector_count.get(sector,0)>=3:continue
                if day not in maps[t] or dates[i+1] not in maps[t]:continue
                chosen.append(t);sector_count[sector]=sector_count.get(sector,0)+1
                if len(chosen)>=top_n:break
            target={t:1/len(chosen) for t in chosen} if chosen else {}
            if target:
                delta=sum(abs(target.get(t,0)-holdings.get(t,0)) for t in set(target)|set(holdings))
                tc=delta*trade_bps/10000
                turnover.append(delta/2)
                trades.append({"date":day,"signal_date":prev,"tickers":chosen,
                               "execution":"following completed close after signal",
                               "one_way_turnover":round(delta/2,6),"cost_fraction":round(tc,7)})
                holdings=target
        if not holdings:continue
        # Drop any date with missing held-stock returns rather than silently
        # assigning a zero return; terminate diagnostic to prevent distortion.
        if any(day not in maps[t] or dates[i+1] not in maps[t] for t in holdings):
            return {"status":"GAPS_IN_HELD_STOCK_HISTORY","at":day,
                    "reason":"Cannot assume returns for an untraded/delisted stock"}
        gross=sum(w*(maps[t][dates[i+1]]/maps[t][day]-1) for t,w in holdings.items())
        returns.append(gross-tc)
        benchmark_returns.append(maps["SPY"][dates[i+1]]/maps["SPY"][day]-1)
        sector_returns.append(maps["XLK"][dates[i+1]]/maps["XLK"][day]-1)
        dates_ret.append(dates[i+1]);costs.append(tc)
        weights_history.append(holdings.copy())
        # Positions drift between monthly rebalances. Holding fixed equal
        # weights each day without trading would silently imply cost-free
        # daily rebalancing and overstate investability.
        if gross > -0.999999999:
            holdings={t:w*(maps[t][dates[i+1]]/maps[t][day])/(1+gross)
                      for t,w in holdings.items()}
    if len(returns)<20:return {"status":"INSUFFICIENT_BACKTEST_HORIZON"}
    active=[s-b for s,b in zip(returns,benchmark_returns)]
    bm=_metrics(benchmark_returns,[],0);tech=_metrics(sector_returns,[],0);res=_metrics(returns,turnover,sum(costs)*10000)
    sstd=statistics.stdev(active) if len(active)>1 else 0
    alpha=statistics.mean(active)/sstd*math.sqrt(252) if sstd else None
    nav=1.;sp=1.;xl=1.;curve=[]
    for d,r,b,x in zip(dates_ret,returns,benchmark_returns,sector_returns):
        nav*=1+r;sp*=1+b;xl*=1+x
        curve.append({"date":d,"strategy_nav":round(nav,6),"spy_nav":round(sp,6),"xlk_nav":round(xl,6)})
    monthly={}
    for row in curve:
        m=row["date"][:7]
        monthly[m]=row
    previous=[1.,1.,1.];monthly_returns=[]
    for m,row in sorted(monthly.items()):
        current=[row["strategy_nav"],row["spy_nav"],row["xlk_nav"]]
        monthly_returns.append({"month":m,"strategy":round(current[0]/previous[0]-1,5),
          "spy":round(current[1]/previous[1]-1,5),"xlk":round(current[2]/previous[2]-1,5)})
        previous=current
    return {"status":"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC",
        "strategy_id":"M7-MOMENTUM-8-MONTHLY-v1",
        "start_date":dates_ret[0],"end_date":dates_ret[-1],
        "universe":len(tickers),"min_history":65,
        "signal":"30% 5-session momentum + 40% 20-session XLK-excess + 20% 60-session momentum + 10% inverse realized volatility percentile; no fundamentals or current Alpha",
        "rebalance":"monthly, next-trading-day close fill after prior-close signal",
        "risk":"equal weight top 8, max 3 names per sector, no leverage",
        "one_way_bps":trade_bps,
        "metrics":res,"benchmarks":{"SPY":bm,"XLK":tech},
        "information_ratio":round(alpha,3) if alpha is not None else None,
        "curve":curve,"monthly":monthly_returns,"trades":trades,
        "limitations":["Current 40-stock universe used historically: strong survivorship/selection bias",
          "No delisted securities, adjusted dividends or splits separately audited; provider close data as delivered",
          "No intraday fill or market-impact estimates; close-price execution assumes liquidity",
          "Realized returns based on prior-day signals with one-session close execution lag",
          "SEC as-filed fundamentals and 2026 M7 supply Alpha NOT incorporated in historical returns",
          "Short historical window (up to 330 calendar days): insufficient to validate a robust trading edge"]}
