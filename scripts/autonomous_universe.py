"""Audited 40-name research universe for the *forward* paper portfolio.

The original evidence-gated SEC screener remains untouched. This supplementary
model supplies a *provisional* score for every ticker, with provenance on
each missing-factor estimate. It NEVER imputes a fill price or a historical
backtest return. All estimates use only currently observed same-date peers.
"""
from __future__ import annotations
import math
from statistics import median

try:
    from scripts.quant_strategy import SECTOR_BANDS
except ModuleNotFoundError:
    from quant_strategy import SECTOR_BANDS

FACTOR_WEIGHTS={"supply_alpha":.30,"monitor":.20,"growth":.20,
                "value":.15,"size":.05,"risk":.10}
MIN_SAME_SECTOR_PEERS=3
ESTIMATE_SHRINKAGE=.50

def sector(symbol):
    return next((name for name,items in SECTOR_BANDS.items() if symbol in items),"Other")

def valid(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)

def create_autonomous_universe(ranked,expected_symbols,as_of):
    """Produce a reproducible, audited score for *each* of the 40 tickers.

    Existing percentile factor scores are already normalized 0..100. Missing
    factors get same-sector cross-sectional median of observed percentiles
    when >=3 peer observations exist, otherwise global observed median, or a
    neutral 50 when *all* peers are missing. Imputed components are shrunk
    toward neutral (lower evidentiary confidence); never marked as observed.
    """
    originals={r["ticker"]:r for r in ranked}
    symbols=list(dict.fromkeys(expected_symbols))
    if len(symbols)!=40:
        raise ValueError("Autonomous universe must contain exactly 40 unique tickers")
    output=[]
    for symbol in symbols:
        row=originals.get(symbol,{})
        original=row.get("component_scores") or {}
        components={};provenance={}
        observed_weight=0.
        for factor,weight in FACTOR_WEIGHTS.items():
            value=original.get(factor)
            if valid(value):
                components[factor]=round(float(value),4)
                provenance[factor]={"kind":"OBSERVED_FACTOR_SCORE","as_of":as_of}
                observed_weight+=weight
                continue
            peers=[originals[t].get("component_scores",{}).get(factor)
                   for t in symbols if t!=symbol and t in originals
                   and sector(t)==sector(symbol)]
            peers=[float(x) for x in peers if valid(x)]
            if len(peers)>=MIN_SAME_SECTOR_PEERS:
                m=median(peers);method="SECTOR_MEDIAN";count=len(peers)
            else:
                peers=[originals[t].get("component_scores",{}).get(factor)
                       for t in symbols if t!=symbol and t in originals]
                peers=[float(x) for x in peers if valid(x)]
                if peers:
                    m=median(peers);method="GLOBAL_MEDIAN";count=len(peers)
                else:
                    m=50.;method="NEUTRAL_NO_PEER_DATA";count=0
            components[factor]=round(50.+ESTIMATE_SHRINKAGE*(m-50.),4)
            provenance[factor]={"kind":"ESTIMATED_FACTOR_SCORE","method":method,
                                "peer_count":count,"as_of":as_of,
                                "not_verified_fundamental":True}
        # Evidence discount: an entirely imputed stock cannot beat a very
        # well-supported observed stock by aggressively extrapolating peers.
        raw_score=sum(weight*components[factor]
                      for factor,weight in FACTOR_WEIGHTS.items())
        confidence=round(observed_weight,4)
        penalized=50.+confidence*(raw_score-50.)
        output.append({
            "ticker":symbol,"sector":sector(symbol),
            "research_score":round(penalized,4),
            "factor_scores":components,
            "factor_provenance":provenance,
            "observed_factor_coverage":confidence,
            "estimated_factor_weight":round(1-confidence,4),
            "estimation_warning":"Factor scores are provisional estimates, not verified SEC values",
            "source_rank_eligible":bool(row.get("rank_eligible",False)),
            "as_of":as_of})
    output.sort(key=lambda r:(-r["research_score"],r["ticker"]))
    for i,row in enumerate(output,1):row["candidate_rank"]=i
    observed=sum(x["observed_factor_coverage"] for x in output)/40
    return {"mode":"FORWARD_ONLY_ESTIMATED_RESEARCH",
            "as_of":as_of,"universe_count":40,"candidates":output,
            "observed_weight_mean":round(observed,4),
            "estimation_method":"observed percentile -> same-sector peer median (>=3), global peer median, neutral 50; shrink estimated component by 50% and entire score by observed factor coverage",
            "price_execution_policy":"NEVER impute prices for trading, mark-to-market or backtests",
            "historical_backtest_compatible":False,
            "warning":"All 40 receive an estimated research score; this is not 40 fully sourced SEC fundamental scores."}
