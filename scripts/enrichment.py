"""Point-in-time disclosures and transparent proxy factor extraction.

The primary SEC fallback is a dated set of audited FY figures, not an API
update.  Only analyst consensus surprises could be labeled a true 'surprise'.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def annual_capex_fallback(as_of):
    file=ROOT/"config"/"capex_primary_seed.json"
    if not file.is_file():return {}
    items=json.loads(file.read_text(encoding="utf-8")).get("companies",[])
    out={}
    for rec in items:
        if rec.get("as_of","9999-99-99")>as_of: continue
        new=rec.get("capex_latest")
        prev=rec.get("capex_prior")
        if not isinstance(new,(int,float)) or not isinstance(prev,(int,float)) or prev<=0:continue
        if not str(rec.get("source","")).startswith("https://"):continue
        out[rec["ticker"]]={"growth":new/prev-1,"filed":rec["as_of"],
            "source":rec["source"],"url":rec["source"],"fy_latest":rec["fy_latest"],
            "fy_prior":rec["fy_prior"],"metric":rec["metric"],
            "method":"annual_capex_yoy_proxy","quality":"audited_annual_primary_source_fallback"}
    return out

def disclosed_share_change(edges,as_of):
    """Only compare two explicitly disclosed revenue-share observations.

    A difference in supplier revenue dependence is NOT proof that customer
    purchases changed; it is a separately labeled relationship proxy.
    """
    latest={}
    for edge in edges:
        if not edge.get("verified") or not edge.get("date") or edge["date"]>as_of:continue
        s=edge.get("revenue_share")
        p=edge.get("prior_revenue_share")
        if not (isinstance(s,(int,float)) and isinstance(p,(int,float))):continue
        if not (0<=s<=100 and 0<=p<=100):continue
        src=edge.get("source")
        if not isinstance(src,str) or not src.startswith("https://"):continue
        ticker=edge.get("supplier")
        obj={"change_pp":round(s-p,5),"supplier":ticker,"customer":edge.get("customer"),
             "current_revenue_pct":s,"prior_revenue_pct":p,"date":edge["date"],
             "source":src,"method":"disclosed_customer_revenue_share_change_pp"}
        latest.setdefault(ticker,[]).append(obj)
    return latest

def five_day_return(bars):
    if len(bars)<6:return None
    base=bars[-6][1]
    return bars[-1][1]/base-1 if base>0 else None

def monitoring_scores(quotes,tickers,peer_rank,residuals):
    """A stand-alone PRICE-ONLY watch score, never a supply-chain Alpha."""
    raw5={t:five_day_return(quotes.get(t,{}).get("bars",[])) for t in tickers}
    r5=[x for x in raw5.values() if x is not None]
    r60=[x for x in residuals.values() if x is not None]
    result={}
    for t in tickers:
        p5=peer_rank(raw5[t],r5)
        pr=peer_rank(residuals.get(t),r60)
        if p5 is None or pr is None: result[t]=None
        else:result[t]=round(.40*p5+.60*pr,2)
    return result

def dataset_health(suppliers,factor_names):
    return {
        "factors_present":{f:sum(s.get("factors",{}).get(f) is not None for s in suppliers) for f in factor_names},
        "monitor_present":sum(s.get("monitor_score") is not None for s in suppliers),
        "provisional_present":sum(s.get("provisional_alpha") is not None for s in suppliers),
        "official_present":sum(s.get("alpha") is not None for s in suppliers),
        "price_present":sum(s.get("close") is not None and s.get("previous_close") is not None for s in suppliers),
    }
