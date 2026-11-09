"""Causal 40-name historical PRICE-ONLY investability-style risk diagnostic.

The current forward six-factor alpha/fundamental scores cannot be backfilled.
Instead, for each monthly signal date, calculate a historical price-only score:
30% 5-day return, 40% 20-day XLK-relative return, 20% 60-day return,
10% low realized 60-day volatility. Convert to percentiles and use the
SAME capped softmax allocation as the forward autonomous paper portfolio.

Dynamic eligibility: 65 actual closes ending the previous benchmark session;
no IPO backfill or imputed execution prices. VIX close is from prev session.
This is an educational research diagnostic with a current-universe survivorship
bias, NOT proof of historical six-factor investability alpha.
"""
from __future__ import annotations
import math,statistics

try:
    from scripts.autonomous_paper import investability_weights
    from scripts.quant_strategy import _metrics,rank_pct,vix_target_exposure
except ModuleNotFoundError:
    from autonomous_paper import investability_weights
    from quant_strategy import _metrics,rank_pct,vix_target_exposure

def trailing_signal_candidates(bars,tickers,dates,i):
    """Prices through i-1 exclusively; all metrics point in time."""
    prev=dates[i-1]
    xlk=bars["XLK"]
    if i<65 or dates[i-21] not in xlk or prev not in xlk:return []
    b20=xlk[prev]/xlk[dates[i-21]]-1
    raw={}
    for t in tickers:
        earlier=[bars[t][d] for d in dates[:i] if d in bars[t] and bars[t][d]>0]
        if len(earlier)<65 or prev not in bars[t]:continue
        p=earlier
        r5=p[-1]/p[-6]-1
        ex20=(p[-1]/p[-21]-1)-b20
        r60=p[-1]/p[-61]-1
        day_returns=[p[k]/p[k-1]-1 for k in range(len(p)-60,len(p))]
        vol=statistics.stdev(day_returns)
        if not math.isfinite(vol) or vol<=0:continue
        raw[t]=(r5,ex20,r60,vol)
    if len(raw)<10:return []
    metrics=list(raw.values())
    comps=[[r[k] for r in metrics] for k in range(4)]
    candidates=[]
    for t,vals in raw.items():
        ranks=[rank_pct(vals[k],comps[k]) for k in range(4)]
        if any(x is None for x in ranks):continue
        score=.30*ranks[0]+.40*ranks[1]+.20*ranks[2]+.10*(100-ranks[3])
        candidates.append({"ticker":t,"research_score":max(0,min(100,score))})
    return candidates

def simulate_forty_score_weighted(quotes,tickers,initial_date,trade_bps=10,vix_trigger=True):
    if len(tickers)!=40 or len(set(tickers))!=40:
        return {"status":"BAD_UNIVERSE","reason":"Expected 40 unique tickers"}
    names=(*tickers,"QQQ","XLK","VIX")
    bars={t:dict(quotes.get(t,{}).get("bars") or []) for t in names}
    dates=sorted(set(bars["QQQ"])&set(bars["XLK"]))
    dates=[d for d in dates if bars["QQQ"][d]>0 and bars["XLK"][d]>0]
    if len(dates)<120 or dates[85]>initial_date:
        return {"status":"INSUFFICIENT_HISTORY","requested_start":initial_date}
    if vix_trigger and len(bars["VIX"])<120:
        return {"status":"INSUFFICIENT_VIX_HISTORY"}
    holdings={}
    last_exposure=None
    selected=[]
    returns=[];benchmark=[];sector_returns=[];fees=[];turnovers=[]
    counts=[];exp_history=[];dates_out=[];trade_events=0;monthly_rebalances=0
    for i in range(85,len(dates)-1):
        day=dates[i]
        if day<initial_date:continue
        prev=dates[i-1]
        exp=vix_target_exposure(bars["VIX"].get(prev)) if vix_trigger else 1.
        if exp is None:return {"status":"MISSING_VIX_CLOSE","date":prev}
        monthly=(not returns or day[:7]!=dates[i-1][:7])
        if monthly:
            selected=trailing_signal_candidates(bars,tickers,dates,i)
            if not selected:return {"status":"NO_POINT_IN_TIME_SIGNALS","date":prev}
            monthly_rebalances+=1
        change=(last_exposure is None or exp!=last_exposure)
        cost=0.
        if monthly or change:
            if exp==0:target={}
            elif monthly or not holdings:
                target=investability_weights(selected,exp)
                if target is None:
                    return {"status":"UNALLOCATABLE_SCORE_CAPS","date":prev,
                            "eligible_count":len(selected)}
            else:
                current=sum(holdings.values())
                target={t:w*exp/current for t,w in holdings.items()} if current>0 else {}
            if any(day not in bars[t] or bars[t][day]<=0 for t in set(target)|set(holdings)):
                return {"status":"MISSING_EXECUTION_CLOSE","date":day}
            delta=sum(abs(target.get(t,0)-holdings.get(t,0)) for t in set(target)|set(holdings))
            cost=delta*trade_bps/10000
            turnovers.append(delta/2);fees.append(cost)
            if delta>1e-10:trade_events+=1
            holdings=target
        last_exposure=exp
        nxt=dates[i+1]
        if any(day not in bars[t] or nxt not in bars[t] or bars[t][day]<=0 or bars[t][nxt]<=0 for t in holdings):
            return {"status":"MISSING_HELD_RETURN","date":day}
        gross=sum(w*(bars[t][nxt]/bars[t][day]-1) for t,w in holdings.items())
        returns.append(gross-cost)
        benchmark.append(bars["QQQ"][nxt]/bars["QQQ"][day]-1)
        sector_returns.append(bars["XLK"][nxt]/bars["XLK"][day]-1)
        dates_out.append(nxt)
        counts.append(len(selected));exp_history.append(sum(holdings.values()))
        if gross>-0.999999:
            holdings={t:w*(bars[t][nxt]/bars[t][day])/(1+gross) for t,w in holdings.items()}
    if len(returns)<100:return {"status":"INSUFFICIENT_HORIZON"}
    metric=_metrics(returns,turnovers,sum(fees)*10000)
    qmetric=_metrics(benchmark,[],0)
    techmetric=_metrics(sector_returns,[],0)
    residual=[a-b for a,b in zip(returns,benchmark)]
    vol=statistics.stdev(residual) if len(residual)>1 else 0
    return {"status":"COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC",
            "strategy_id":"M7-FORTY-HISTORICAL-PRICE-SCORE-SOFTMAX-VIX-v1" if vix_trigger else
                          "M7-FORTY-HISTORICAL-PRICE-SCORE-SOFTMAX-v1",
            "start_date":dates_out[0],"end_date":dates_out[-1],
            "requested_start":initial_date,"metrics":metric,
            "benchmarks":{"QQQ":qmetric,"XLK":techmetric},
            "information_ratio":round(statistics.mean(residual)/vol*math.sqrt(252),3) if vol else None,
            "minimum_active_names":min(counts),"maximum_active_names":max(counts),
            "average_active_names":round(statistics.mean(counts),3),
            "end_active_names":counts[-1],
            "mean_stock_exposure":round(statistics.mean(exp_history),5),
            "trade_events":trade_events,"monthly_rebalances":monthly_rebalances,
            "assumptions":{
                "stock_pool":"40 current stocks; strong survivorship selection bias remains",
                "stock_membership":"only after 65 observed closes ending at prior session",
                "point_in_time_historical_score":
                   "30% 5-day return, 40% 20-day XLK excess, 20% 60-day return, 10% inverse 60-day volatility; cross-sectional percentiles",
                "allocation":
                   "current forward investability softmax SHAPE: 12% equal budget floor, 88% capped softmax with temperature 1.25; 10% invested name cap and 45% invested sector cap",
                "rebalance":"monthly stock scores, daily VIX band exposure adjustment",
                "execution":"signals before session; trade at next close, returns from fill close onward",
                "execution_price_estimation":False,
                "historical_six_factor_investability":False,
                "historical_fundamental_scores_used":False,
                "historical_supply_alpha_used":False,
                "historical_estimated_factors_used":False,
                "cash_annual_yield":0.,
                "one_way_transaction_cost_bps":trade_bps,
                "NOT_DIRECT_BACKTEST_OF_CURRENT_AUTONOMOUS_PAPER_SCORES":True
            }}
