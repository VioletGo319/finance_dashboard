"""40-name equal-weight historical PRICE-ONLY diagnostic, vs QQQ.

This is NOT a historical backtest of the current 40-stock SEC/estimated
investment scores, because those values are not point-in-time reconstructible.
Historic listings (e.g., GEV/CEG) join only after 65 observed sessions;
current 40-name membership retains strong survivorship/selection bias.
Missing actual daily closes are never interpolated into trading returns.
"""
from __future__ import annotations
from datetime import date
import math
import statistics

try:
    from scripts.quant_strategy import _metrics,vix_target_exposure
except ModuleNotFoundError:
    from quant_strategy import _metrics,vix_target_exposure

def simulate_forty_price_only(quotes,tickers,initial_date,trade_bps=10,vix_trigger=False):
    if len(tickers)!=40 or len(set(tickers))!=40:
        return {"status":"BAD_UNIVERSE","reason":"Expected 40 unique tickers"}
    universe=(*tickers,"QQQ","XLK","VIX")
    bars={ticker:dict(quotes.get(ticker,{}).get("bars") or []) for ticker in universe}
    dates=sorted(set(bars["QQQ"]) & set(bars["XLK"]))
    dates=[d for d in dates if bars["QQQ"][d]>0 and bars["XLK"][d]>0]
    if len(dates)<120 or dates[85]>initial_date:
        return {"status":"INSUFFICIENT_HISTORY","requested_start":initial_date}
    if vix_trigger and len(bars["VIX"])<120:
        return {"status":"INSUFFICIENT_VIX_HISTORY"}
    holdings={}
    selected=[]
    last_exposure=None
    rr=[];qqq=[];xlk=[];turnover=[];fees=[];counts=[];stock_exposures=[];trade_count=0
    dates_out=[]
    for i in range(85,len(dates)-1):
        d=dates[i]
        if d<initial_date:continue
        prev=dates[i-1]
        exposure=vix_target_exposure(bars["VIX"].get(prev)) if vix_trigger else 1.
        if exposure is None:
            return {"status":"MISSING_VIX_CLOSE","date":prev}
        first=not rr
        monthly=first or d[:7]!=dates[i-1][:7]
        if monthly:
            available=[]
            for ticker in tickers:
                # At signal formation, require 65 observed prior closes
                # ending exactly at prior benchmark session.
                earlier=[day for day in dates[:i] if day in bars[ticker] and bars[ticker][day]>0]
                if len(earlier)>=65 and earlier[-1]==prev:
                    available.append(ticker)
            if not available:return {"status":"NO_ACTIVE_STOCKS","date":prev}
            selected=available
        changed=last_exposure is None or last_exposure!=exposure
        cost=0.
        if monthly or changed:
            if exposure==0:
                target={}
            elif monthly or not holdings:
                target={t:exposure/len(selected) for t in selected}
            else:
                previous=sum(holdings.values())
                target={t:w*exposure/previous for t,w in holdings.items()} if previous>0 else {}
            # Validate observed execution prices, no synthetic fills.
            if any(d not in bars[t] or bars[t][d]<=0 for t in set(target)|set(holdings)):
                return {"status":"MISSING_EXECUTION_CLOSE","date":d}
            delta=sum(abs(target.get(t,0)-holdings.get(t,0))
                      for t in set(target)|set(holdings))
            cost=delta*trade_bps/10000
            turnover.append(delta/2)
            fees.append(cost)
            if delta>1e-10:trade_count+=1
            holdings=target
        last_exposure=exposure
        if any(d not in bars[t] or dates[i+1] not in bars[t] or bars[t][d]<=0
               for t in holdings):
            return {"status":"MISSING_HELD_RETURN","date":d}
        gross=sum(w*(bars[t][dates[i+1]]/bars[t][d]-1) for t,w in holdings.items())
        rr.append(gross-cost)
        qqq.append(bars["QQQ"][dates[i+1]]/bars["QQQ"][d]-1)
        xlk.append(bars["XLK"][dates[i+1]]/bars["XLK"][d]-1)
        dates_out.append(dates[i+1]);counts.append(len(selected))
        stock_exposures.append(sum(holdings.values()))
        if gross>-0.999999:
            holdings={t:w*(bars[t][dates[i+1]]/bars[t][d])/(1+gross) for t,w in holdings.items()}
    if len(rr)<100:return {"status":"INSUFFICIENT_HORIZON"}
    results=_metrics(rr,turnover,sum(fees)*10000)
    qqq_metrics=_metrics(qqq,[],0)
    xlk_metrics=_metrics(xlk,[],0)
    spread=[a-b for a,b in zip(rr,qqq)]
    stdev=statistics.stdev(spread) if len(spread)>1 else 0
    return {"status":"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC",
            "start_date":dates_out[0],"end_date":dates_out[-1],
            "requested_start":initial_date,
            "strategy_id":"M7-FORTY-EQUALWEIGHT-VIX-v1" if vix_trigger else
                "M7-FORTY-EQUALWEIGHT-v1",
            "metrics":results,"benchmarks":{"QQQ":qqq_metrics,"XLK":xlk_metrics},
            "information_ratio":round(statistics.mean(spread)/stdev*math.sqrt(252),3) if stdev else None,
            "trade_events":trade_count,
            "average_active_names":round(statistics.mean(counts),2),
            "minimum_active_names":min(counts),
            "maximum_active_names":max(counts),
            "mean_stock_exposure":round(statistics.mean(stock_exposures),5),
            "end_active_names":counts[-1],
            "first_trade_date":dates_out[0],
            "assumptions":{
                "universe":"today's 40 names, not historic constituents; survivorship bias",
                "eligibility":"listed with >=65 historical closes as of prior signal close",
                "weights":"equal weight across historically eligible names",
                "rebalance":"monthly stock membership/weights, daily VIX exposure when band changes",
                "signal":"previous session VIX close; execute following close, next close-to-close return",
                "execution":"observed close only; never interpolate missing prices",
                "one_way_bps":trade_bps,
                "cash_yield":0.,
                "historical_fundamental_scores_used":False,
                "historical_estimated_factors_used":False,
                "not_a_full_40_stock_alpha_backtest":True}
           }
