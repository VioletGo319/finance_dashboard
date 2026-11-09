"""Autonomous research PAPER account. No broker connection, no real orders.

A daily close builds a target; the next *distinct completed session* may fill it.
State is persistent through GitHub's daily committed data/quant/paper_state.json.
All orders are simulated at sourced completed closes, not broker executions.
"""
from __future__ import annotations
from datetime import date
import json, math
from pathlib import Path

STARTING_CASH=1000.0
ONE_WAY_COST_BPS=10
MAX_NAME_WEIGHT=0.15
MAX_SECTOR_WEIGHT=0.40
MAX_STOCK_EXPOSURE=1.0
MAX_PRICE_STALENESS_DAYS=5
ALLOCATION_VERSION="INVESTABILITY_SOFTMAX_V2"
# At least 12% of the VIX stock budget is spread evenly across all 40 names.
# The remaining 88% is allocated by confidence-adjusted investability score.
WEIGHT_FLOOR_FRACTION=0.12
SCORE_SOFTMAX_TEMPERATURE=1.25
SCORE_STD_FLOOR=7.5
SCORE_Z_CLIP=2.5
MAX_NAME_STOCK_BUDGET_FRACTION=0.10
MAX_SECTOR_STOCK_BUDGET_FRACTION=0.45


try:
    from scripts.quant_strategy import SECTOR_BANDS, vix_target_exposure
except ModuleNotFoundError:
    from quant_strategy import SECTOR_BANDS, vix_target_exposure

def sector(t):
    return next((name for name,members in SECTOR_BANDS.items() if t in members),"Other")

def valid_close(row,signal_day):
    price=row.get("close")
    stamped=row.get("price_date")
    try:
        lag=(date.fromisoformat(signal_day)-date.fromisoformat(stamped)).days
    except (TypeError,ValueError):return None
    if not isinstance(price,(float,int)) or not math.isfinite(price) or price<=0 or lag<0 or lag>MAX_PRICE_STALENESS_DAYS:
        return None
    return float(price)

def investability_weights(candidates,exposure):
    """Bounded softmax of evidence-adjusted scores + positive eligible-name floor.

    Full investment is redistributed after single-name (15% of NAV) and
    sector (40% of NAV) caps. No ad hoc security price interpolation.
    The 40-stock score is from CURRENT observed+estimated research only; do
    not treat these weights as historical point-in-time allocations.
    """
    if not (0<exposure<=MAX_STOCK_EXPOSURE):return None
    n=len(candidates)
    if n<10 or n>40:return None  # Late-listed securities enter only after valid history
    scores=[]
    names=[]
    for row in candidates:
        score=row.get("research_score")
        ticker=row.get("ticker")
        if (not isinstance(score,(int,float)) or isinstance(score,bool)
             or not math.isfinite(score) or not 0<=score<=100 or not ticker):
            return None
        names.append(ticker);scores.append(float(score))
    if len(set(names))!=n:return None
    avg=sum(scores)/n
    sd=math.sqrt(sum((v-avg)**2 for v in scores)/n)
    denom=max(SCORE_STD_FLOOR,sd)
    strength={
       t:math.exp(SCORE_SOFTMAX_TEMPERATURE*
          max(-SCORE_Z_CLIP,min(SCORE_Z_CLIP,(score-avg)/denom)))
       for t,score in zip(names,scores)}
    # The only invariant cash is 1-exposure; there is no hidden equal-weight
    # 70% allocation as in the previous version.
    weights={t:exposure*WEIGHT_FLOOR_FRACTION/n for t in names}
    max_name=min(MAX_NAME_WEIGHT,exposure*MAX_NAME_STOCK_BUDGET_FRACTION)
    max_sector=min(MAX_SECTOR_WEIGHT,exposure*MAX_SECTOR_STOCK_BUDGET_FRACTION)
    group={t:sector(t) for t in names}
    remaining=exposure-sum(weights.values())
    # Constrained proportional water filling. Whenever an individual or
    # sector reaches its limit, its allocation is frozen and the remainder
    # flows to other available stocks in score-proportional shares.
    for _ in range(4*n):
        if remaining<1e-10:break
        sector_totals={g:sum(weights[t] for t in names if group[t]==g)
                       for g in set(group.values())}
        active=[t for t in names if
                weights[t]<max_name-1e-9 and
                sector_totals[group[t]]<max_sector-1e-9]
        if not active:return None
        z=sum(strength[t] for t in active)
        suggested={t:remaining*strength[t]/z for t in active}
        by_group={}
        for t,d in suggested.items():by_group[group[t]]=by_group.get(group[t],0.)+d
        scales=[1.]
        for t,d in suggested.items():
            if d>0:scales.append(max(0.,max_name-weights[t])/d)
        for g,d in by_group.items():
            if d>0:scales.append(max(0.,max_sector-sector_totals[g])/d)
        scale=min(scales)
        if scale<=1e-11:return None
        for t,d in suggested.items():
            weights[t]+=scale*d
        remaining-=scale*sum(suggested.values())
    if remaining>1e-6:return None
    # Rounding down preserves hard sector and single-stock caps.
    rounded={t:math.floor(max(0.,w)*1e8+1e-9)/1e8 for t,w in weights.items()}
    if (any(w<=0 or w>max_name+1e-9 for w in rounded.values())
        or sum(rounded.values())>exposure+1e-8):
        return None
    for group_name in set(group.values()):
        if sum(rounded[t] for t in names if group[t]==group_name)>max_sector+1e-8:
            return None
    return rounded

def target_weights(ranked,quotes,vix_close,price_day,require_full=False):
    """All 40 participate when the verified 40-name candidate file is provided.

    Never make up prices. Any missing/aged actual close blocks a 40-name
    portfolio instead of pretending an estimated price could fill an order.
    """
    exposure=vix_target_exposure(vix_close)
    if exposure is None:return None,"VIX_UNAVAILABLE"
    if exposure==0:return {},"CASH_BY_VIX"
    if require_full and (len(ranked)!=40 or len({r.get("ticker") for r in ranked})!=40):
        return None,"INCOMPLETE_40_STOCK_UNIVERSE"
    choices=[];unpriced=[]
    for row in ranked:
        symbol=row.get("ticker")
        if not symbol:continue
        if require_full:
            if not isinstance(row.get("research_score"),(float,int)):
                return None,"MISSING_RESEARCH_SCORE"
        elif not row.get("rank_eligible"):
            continue
        if valid_close(quotes.get(symbol,{}),price_day) is None:
            unpriced.append(symbol)
            continue
        choices.append(row)
        if not require_full and len(choices)>=8:break
    if require_full and unpriced:return None,"UNPRICED_STOCKS:"+",".join(sorted(unpriced))
    if len(choices)<(40 if require_full else 5):
        return None,"INSUFFICIENT_TRADEABLE_STOCKS"
    if require_full:
        # 40 observed+imputed candidate scores already incorporate an
        # evidence-coverage shrinkage. A bounded softmax magnifies genuine
        # score differences; it never uses an estimated stock price.
        weights=investability_weights(choices,exposure)
        if weights is None:return None,"INFEASIBLE_SECTOR_OR_NAME_CAPS"
        if len(weights)!=40 or any(x<=0 for x in weights.values()):
            return None,"ZERO_TARGET_WEIGHT"
        return weights,"READY_ALL_40"
    # Legacy eight-name paper allocation, retained for backwards compatibility.
    n=len(choices)
    weights={r["ticker"]:math.floor(exposure/n*1e8)/1e8 for r in choices}
    return weights,"READY"

def weighting_policy():
    return {
        "allocation_version":ALLOCATION_VERSION,
        "inputs":"40 forward-only investability research scores (estimated factors confidence-shrunk)",
        "weight_formula":"12% equally spread over 40; 88% in capped softmax of (research_score-mean)/max(std,7.5), name <=10% of stock budget and sector <=45% of stock budget",
        "softmax_temperature":SCORE_SOFTMAX_TEMPERATURE,
        "minimum_stock_budget_fraction":WEIGHT_FLOOR_FRACTION,
        "single_name_nav_cap":MAX_NAME_WEIGHT,
        "sector_nav_cap":MAX_SECTOR_WEIGHT,
        "single_name_max_fraction_of_stock_budget":MAX_NAME_STOCK_BUDGET_FRACTION,
        "sector_max_fraction_of_stock_budget":MAX_SECTOR_STOCK_BUDGET_FRACTION,
        "remainder":"Redistribute capped excess to eligible stocks in score-proportional weights",
        "execution_prices":"Observed closes only; no estimated executions",
        "historical_validation":"Not backtested with historical investability scores"
    }

def new_state():
    return {"schema_version":"1.0","mode":"PAPER_ONLY","live_enabled":False,
            "status":"AWAITING_FIRST_FUTURE_FILL","starting_cash":STARTING_CASH,
            "cash":STARTING_CASH,"shares":{},"pending":None,"last_price_day":None,
            "last_allocation_month":None,"last_target_exposure":None,
            "last_fill_day":None,"trade_count":0,"total_fees":0.0,
            "equity":STARTING_CASH,"unrealized_pnl":0.0,
            "equity_history":[],"audit":[]}

def _log(state,day,event,**kwargs):
    state["audit"].append({"date":day,"event":event,**kwargs})
    state["audit"]=state["audit"][-200:]

def _mark_to_market(state,quotes,price_day):
    positions={}
    total=state["cash"]
    for t,sh in state["shares"].items():
        price=valid_close(quotes.get(t,{}),price_day)
        if price is None:return None
        positions[t]=round(sh*price,6)
        total+=sh*price
    state["equity"]=round(total,6)
    state["unrealized_pnl"]=round(total-state["starting_cash"],6)
    state["positions_value"]=positions
    state["cash_weight"]=round(state["cash"]/total,6) if total>0 else None
    return total

def _execute_pending(state,quotes,price_day):
    order=state.get("pending")
    if not order or price_day<=order["signal_day"]:return
    if state.get("last_fill_day")==price_day:return
    weights=order["weights"]
    if any(valid_close(quotes.get(t,{}),price_day) is None for t in set(weights)|set(state["shares"])):
        state["status"]="HALTED_MISSING_PRICE"
        _log(state,price_day,"FILL_REJECTED_MISSING_PRICE")
        return
    nav=_mark_to_market(state,quotes,price_day)
    if nav is None or nav<=0:
        state["status"]="HALTED_BAD_EQUITY"
        return
    # Sell first, then buy; self-financing, fractional shares, 10 bps each side.
    desired={t:nav*w for t,w in weights.items()}
    fills=[]
    for t in sorted(set(weights)|set(state["shares"])):
        p=valid_close(quotes.get(t,{}),price_day)
        before=state["shares"].get(t,0.0)
        target_value=desired.get(t,0.0)
        after=target_value/p
        change=after-before
        if abs(change*p)<0.01:continue
        if change<0:
            fee=-change*p*ONE_WAY_COST_BPS/10000
            state["cash"]+=-change*p-fee
            state["shares"][t]=after
            fills.append({"ticker":t,"side":"SELL","shares":round(-change,7),"price":p,"fee":round(fee,6)})
    for t in sorted(weights):
        p=valid_close(quotes.get(t,{}),price_day)
        before=state["shares"].get(t,0.0)
        budget=max(0.0,desired[t]-before*p)
        if budget<0.01:continue
        # Cash guard includes the fee in required spending.
        spend=min(budget,state["cash"]/(1+ONE_WAY_COST_BPS/10000))
        if spend<0.01:continue
        fee=spend*ONE_WAY_COST_BPS/10000
        state["cash"]-=spend+fee
        change=spend/p
        state["shares"][t]=before+change
        fills.append({"ticker":t,"side":"BUY","shares":round(change,7),"price":p,"fee":round(fee,6)})
    state["shares"]={k:v for k,v in state["shares"].items() if v>1e-10}
    state["cash"]=round(max(0.0,state["cash"]),8)
    fees=sum(f["fee"] for f in fills)
    state["total_fees"]=round(state["total_fees"]+fees,6)
    state["trade_count"]+=len(fills)
    state["last_fill_day"]=price_day
    state["pending"]=None
    _log(state,price_day,"PAPER_FILLED",source_signal=order["signal_day"],
         fills=fills,fees=round(fees,6))
    state["status"]="PAPER_ACTIVE"

def paper_performance(history):
    """Observed forward paper daily Sharpe; never infer from a historical backtest.

    A minimum of 30 observed close-to-close returns is required before
    showing an annualized Sharpe. Until then the value is explicitly N/A.
    """
    clean=[h for h in history if isinstance(h.get("equity"),(float,int))
           and h["equity"]>0 and isinstance(h.get("date"),str)]
    # No duplicate observations from repeated runs on a closed market.
    clean=sorted({h["date"]:h for h in clean}.values(),key=lambda h:h["date"])
    if len(clean)<31:
        return {"status":"INSUFFICIENT_OBSERVED_PAPER_SESSIONS",
                "observed_sessions":len(clean),
                "minimum_return_sessions":30,
                "sharpe_rf0":None,"max_drawdown":None,
                "observed_total_return":None,"cagr_annualized":None,
                "source":"paper ledger future completed closes only"}
    returns=[clean[i]["equity"]/clean[i-1]["equity"]-1
             for i in range(1,len(clean))]
    try:
        from scripts.quant_strategy import _metrics
    except ModuleNotFoundError:
        from quant_strategy import _metrics
    m=_metrics(returns,[],0)
    return {"status":"COMPUTED_FROM_FORWARD_PAPER_CLOSES",
            "observed_sessions":len(clean),"return_sessions":len(returns),
            "minimum_return_sessions":30,
            "sharpe_rf0":m["sharpe_rf0"],
            "max_drawdown":m["max_drawdown"],
            "observed_total_return":m["total_return"],
            "cagr_annualized":m["cagr_annualized"],
            "source":"paper ledger future completed closes only",
            "not_from_backtest":True}

def update_paper_state(previous,quant,quotes,price_day):
    state=json.loads(json.dumps(previous)) if previous else new_state()
    state["mode"]="PAPER_ONLY";state["live_enabled"]=False
    if state.get("last_price_day") and price_day<state["last_price_day"]:
        state["status"]="HALTED_DATE_REGRESSION"
        return state
    if state.get("last_price_day")==price_day:
        # The snapshot can be regenerated before the next market session.
        # Reweight only a still-unfilled proposal from this completed close;
        # never rewrite past trades or change a position already executed.
        universe=quant.get("autonomous_universe") or {}
        candidates=universe.get("candidates") or []
        old=state.get("pending")
        if (len(candidates)==40 and old and old.get("signal_day")==price_day
            and not state.get("shares") and not state.get("last_fill_day")
            and old.get("allocation_version")!=ALLOCATION_VERSION):
            new,reason=target_weights(candidates,quotes,
                quant.get("vix_trigger_policy",{}).get("latest_vix_close"),
                price_day,require_full=True)
            if new is not None and len(new)==40:
                old["weights"]=new
                old["estimated_notional"]=round(state["equity"]*sum(new.values()),4)
                old["status"]="AWAITING_NEXT_COMPLETED_CLOSE"
                old["allocation_version"]=ALLOCATION_VERSION
                old["score_as_of"]=universe.get("as_of")
                old["weighting"]="confidence_adjusted_investability_softmax_with_caps"
                state["candidate_universe_count"]=40
                state["allocation_method"]="40_STOCK_INVESTABILITY_WEIGHTED"
                state["weighting_policy"]=weighting_policy()
                _log(state,price_day,"UNFILLED_ORDER_REWEIGHTED_BY_INVESTABILITY",
                     actual_fill_count=0,estimated_factor_scores=True,
                     top_weights=[[t,w] for t,w in sorted(new.items(),key=lambda kv:-kv[1])[:5]])
        state["forward_performance"]=paper_performance(state.get("equity_history",[]))
        return state  # no same-day execution; only unfilled plan may migrate
    vix=quant.get("vix_trigger_policy",{})
    vix_date=vix.get("latest_vix_date")
    vix_close=vix.get("latest_vix_close")
    if vix_date!=price_day or vix_target_exposure(vix_close) is None:
        state["status"]="HALTED_MISSING_VIX"
        _log(state,price_day,"NO_SIGNAL_VIX_UNAVAILABLE")
        return state
    _execute_pending(state,quotes,price_day)
    if state["status"].startswith("HALTED_"):return state
    nav=_mark_to_market(state,quotes,price_day)
    if nav is None:
        state["status"]="HALTED_MISSING_POSITION_PRICE"
        return state
    candidate_rows=(quant.get("autonomous_universe") or {}).get("candidates")
    full_universe=bool(candidate_rows)
    weights,reason=target_weights(candidate_rows if full_universe else
          quant.get("screener",{}).get("ranked",[]),
          quotes,vix_close,price_day,require_full=full_universe)
    state["candidate_universe_count"]=len(candidate_rows) if full_universe else None
    state["allocation_method"]="40_STOCK_INVESTABILITY_WEIGHTED" if full_universe else "LEGACY_8_STOCK"
    if full_universe:state["weighting_policy"]=weighting_policy()
    if weights is None:
        state["status"]="HALTED_"+reason
        _log(state,price_day,"NO_ORDER",reason=reason)
        state["last_price_day"]=price_day
        return state
    exposure=vix_target_exposure(vix_close)
    rebalance=(state["last_allocation_month"]!=price_day[:7] or
               state["last_target_exposure"]!=exposure)
    # If a prior order just filled, a VIX regime change can produce a fresh
    # next-session order; no same-close signal execution.
    if rebalance and state.get("pending") is None:
        state["pending"]={"signal_day":price_day,"weights":weights,
                          "target_stock_exposure":exposure,"vix":vix_close,
                          "estimated_notional":round(nav*sum(weights.values()),4),
                          "candidate_count":state["candidate_universe_count"],
                          "estimated_factor_scores":full_universe,
                          "allocation_version":ALLOCATION_VERSION if full_universe else "LEGACY_EQUAL",
                          "score_as_of":(quant.get("autonomous_universe") or {}).get("as_of") if full_universe else None,
                          "weighting":"confidence_adjusted_investability_softmax_with_caps" if full_universe else "equal",
                          "status":"AWAITING_NEXT_COMPLETED_CLOSE"}
        state["last_allocation_month"]=price_day[:7]
        state["last_target_exposure"]=exposure
        _log(state,price_day,"ORDER_PROPOSED",target=weights,vix=vix_close,
             execution="NEXT_COMPLETED_CLOSE_ONLY")
    state["last_price_day"]=price_day
    state["status"]="AWAITING_NEXT_CLOSE" if state.get("pending") else "PAPER_ACTIVE"
    history=state["equity_history"]
    if not history or history[-1]["date"]!=price_day:
        history.append({"date":price_day,"equity":round(state["equity"],6),
                        "cash":round(state["cash"],6)})
    state["equity_history"]=history[-1500:]
    state["forward_performance"]=paper_performance(state["equity_history"])
    state["risk_limits"]={"max_name_weight":MAX_NAME_WEIGHT,
      "max_sector_weight":MAX_SECTOR_WEIGHT,"max_gross_stock_exposure":MAX_STOCK_EXPOSURE,
      "maximum_price_staleness_days":MAX_PRICE_STALENESS_DAYS,
      "transaction_cost_bps_per_side":ONE_WAY_COST_BPS,
      "cash_interest":0,"margin":False,"short_selling":False,
      "execution_price_imputation":False,"candidate_pool_target":40,
      "max_name_fraction_of_stock_budget":MAX_NAME_STOCK_BUDGET_FRACTION,
      "max_sector_fraction_of_stock_budget":MAX_SECTOR_STOCK_BUDGET_FRACTION}
    state["paper_only_notice"]="Simulated at observed completed market closes, not broker fills. No live order API, no real funds or account connected."
    return state

def persist_paper(quant,quotes,price_day,root):
    root=Path(root)
    path=root/"data/quant/paper_state.json"
    prior=json.loads(path.read_text()) if path.is_file() else None
    updated=update_paper_state(prior,quant,quotes,price_day)
    raw=json.dumps(updated,indent=2,ensure_ascii=False)+"\n"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(raw)
    public=root/"site/data/quant/paper_state.json"
    public.parent.mkdir(parents=True,exist_ok=True)
    public.write_text(raw)
    return updated
