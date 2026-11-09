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

def target_weights(ranked,quotes,vix_close,price_day):
    """Point-in-time screen ONLY; never use current values for historical PnL."""
    exposure=vix_target_exposure(vix_close)
    if exposure is None:return None,"VIX_UNAVAILABLE"
    if exposure==0:return {},"CASH_BY_VIX"
    choices=[];counts={}
    for row in ranked:
        if not row.get("rank_eligible"):continue
        symbol=row.get("ticker")
        if not symbol or valid_close(quotes.get(symbol,{}),price_day) is None:continue
        group=sector(symbol)
        if counts.get(group,0)>=3:continue
        choices.append(symbol);counts[group]=counts.get(group,0)+1
        if len(choices)>=8:break
    if len(choices)<5:return None,"INSUFFICIENT_RANKED_LIQUID_NAMES"
    # Respect each name <=15%, sector <=40%. Unallocated budget remains cash.
    proposed={s:exposure/len(choices) for s in choices}
    group_totals={}
    for s,w in proposed.items():group_totals[sector(s)]=group_totals.get(sector(s),0)+w
    weights={s:round(min(w,MAX_NAME_WEIGHT,w*min(1.0,MAX_SECTOR_WEIGHT/group_totals[sector(s)])),8)
             for s,w in proposed.items()}
    return weights,"READY"

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

def update_paper_state(previous,quant,quotes,price_day):
    state=json.loads(json.dumps(previous)) if previous else new_state()
    state["mode"]="PAPER_ONLY";state["live_enabled"]=False
    if state.get("last_price_day") and price_day<state["last_price_day"]:
        state["status"]="HALTED_DATE_REGRESSION"
        return state
    if state.get("last_price_day")==price_day:
        return state  # replay-safe on repeated nightly refresh
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
    weights,reason=target_weights(quant.get("screener",{}).get("ranked",[]),quotes,vix_close,price_day)
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
    state["risk_limits"]={"max_name_weight":MAX_NAME_WEIGHT,
      "max_sector_weight":MAX_SECTOR_WEIGHT,"max_gross_stock_exposure":MAX_STOCK_EXPOSURE,
      "maximum_price_staleness_days":MAX_PRICE_STALENESS_DAYS,
      "transaction_cost_bps_per_side":ONE_WAY_COST_BPS,
      "cash_interest":0,"margin":False,"short_selling":False}
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
