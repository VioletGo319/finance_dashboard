"""Build the quantified investment screener and separate, auditable price-only backtest."""
from __future__ import annotations
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
import json,os
try:
    from scripts.quant_fundamentals import gather_fundamentals
    from scripts.quant_strategy import investment_score, simulate_daily_close, volatility_daily
except ModuleNotFoundError:
    from quant_fundamentals import gather_fundamentals
    from quant_strategy import investment_score, simulate_daily_close, volatility_daily

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data"/"quant"

def load_cached(cutoff):
    file=BASE/"fundamentals_cache.json"
    if not file.is_file():return {},{"status":"not_cached"}
    try:
        obj=json.loads(file.read_text(encoding="utf-8"))
        d=obj.get("as_of","")
        if not d or d>cutoff:return {},{"status":"invalid_date"}
        if (date.fromisoformat(cutoff)-date.fromisoformat(d)).days>14:return {},{"status":"cache_expired"}
        return obj.get("facts") or {},{"status":"cached","cache_as_of":d}
    except (KeyError,ValueError,TypeError,AttributeError):
        return {},{"status":"invalid_cache"}

def collect_fundamentals(tickers,as_of):
    BASE.mkdir(parents=True,exist_ok=True)
    facts,cache_status=load_cached(as_of)
    if len(facts)>=min(30,len(tickers)):return facts,cache_status
    user_agent=os.environ.get("SEC_USER_AGENT","")
    new,audit=gather_fundamentals(tickers,as_of,user_agent=user_agent)
    if new:
        # Never preserve future filing facts. A previously cached record may
        # survive a transient SEC failure, but remains dated in the output.
        facts={**facts,**new}
        (BASE/"fundamentals_cache.json").write_text(json.dumps({
            "as_of":as_of,"facts":facts,
            "data_source":"SEC companyfacts with SEC filed cutoff; ADR adjustment not assumed",
        },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        audit["status"]="retrieved" if not audit.get("errors") else "partial"
        audit["cached_records_used"]=len(facts)-len(new)
    elif facts:
        audit["status"]="cached_after_api_failure"
        audit["cached_records_used"]=len(facts)
    return facts,audit

def build_quant(result,quotes,as_of,write=True):
    tickers=[r["ticker"] for r in result.get("suppliers",[])]
    facts,audit=collect_fundamentals(tickers,as_of)
    meta={}
    for row in result.get("suppliers",[]):
        t=row["ticker"];s=dict(row)
        history=quotes.get(t,{}).get("bars",[])
        closes=[v for _,v in history]
        vol=volatility_daily(closes,60)
        s["realized_vol_60d"]=vol*(252**.5) if vol is not None else None
        meta[t]=s
    ranked=investment_score(tickers,facts,meta)
    backtest=simulate_daily_close(quotes,tickers,top_n=8,trade_bps=10)
    if backtest.get("status")=="COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC":
        portfolio_status="HISTORICAL_PRICE_ONLY_RESEARCH_DIAGNOSTIC"
    else:portfolio_status="NOT_COMPUTABLE"
    payload={"schema_version":"1.0","as_of":as_of,
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "universe":tickers,"fundamental_audit":audit,
        "fundamentals_filing_cutoff":as_of,
        "fundamentals_coverage":{"fiscal_revenue":sum(x.get("revenue_fy_usd") is not None for x in facts.values()),
          "revenue_growth":sum(x.get("revenue_growth_yoy") is not None for x in facts.values()),
          "shares_outstanding":sum(x.get("shares_outstanding") is not None for x in facts.values())},
        "screener":{"status":"CURRENT_CROSS_SECTION_ONLY",
          "as_of":as_of,"formula":"30% sourced supply-chain exploratory Alpha (if 45%+ coverage), 20% price monitor, 20% revenue growth, 15% inverse P/S, 5% log market cap, 10% inverse realized volatility; available weights renormalized, min 75% and at least one fundamental factor",
          "universe_survivorship":"Current 40 names, not historical constituents",
          "ranked":ranked,
          "eligible_count":sum(x["rank_eligible"] for x in ranked),
          "warning":"Not a return forecast. Price×SEC shares is indicative, stale-share/ADR/split checks are required before live investing. Revenue data from 10-K/20-F as filed.",
        },
        "backtest":{"status":portfolio_status,**backtest},
        "separation_rule":"Current 2026 supply Alpha/revenue metrics are NEVER fed into historical price-only backtest. To backtest the full ranking, accumulate or reconstruct as-filed metrics and point-in-time graph edges.",
        "not_included":["survivorship-bias-free historical membership","corporate-action/dividend independently validated prices","historical fundamentals published after each rebalance","historical six-factor Alpha","slippage/market impact measured from executions"],
    }
    if write:
        BASE.mkdir(parents=True,exist_ok=True)
        (BASE/"latest.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        history=BASE/"snapshots";history.mkdir(parents=True,exist_ok=True)
        (history/(as_of+".json")).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        site=ROOT/"site"/"data"/"quant";site.mkdir(parents=True,exist_ok=True)
        (site/"latest.json").write_bytes((BASE/"latest.json").read_bytes())
    return payload
