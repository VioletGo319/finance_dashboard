"""Verified directed M7 supply graph and conservative multi-hop evidence scores.

A supplier -> customer edge weight is a transparent *qualitative evidence proxy*,
NOT a purchase share, Pearson correlation, or probability of transmission.
"""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CLIENTS=("AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA")

def load_universe():
    payload=json.loads((ROOT/"config"/"universe.json").read_text(encoding="utf-8"))
    rows=payload["suppliers"]
    symbols=[r["ticker"] for r in rows]
    if len(rows)!=40 or len(set(symbols))!=40:
        raise ValueError("Expected unique 40-stock universe")
    return payload

def compute_paths(graph, universe, as_of=None):
    """Return path products for directed routes with 1 or 2 edges.

    For A -> B -> C path: weight(A,B) * weight(B,C) * 0.7.
    All edge dates must be <= as_of. Paths are never treated as independent
    probabilities or economic sales shares. Missing links are *unknown*.
    """
    as_of=as_of or date.today().isoformat()
    universe=set(universe)
    types=graph["edge_types"]
    valid=[]
    for e in graph.get("edges",[]):
        if not e.get("verified") or not e.get("date") or e["date"]>as_of:
            continue
        if not str(e.get("source","")).startswith("https://"):
            continue
        weight=types.get(e.get("edge_type"),{}).get("proxy_weight")
        if not isinstance(weight,(int,float)) or not (0<=weight<=1):
            continue
        if e["supplier"] not in universe or e["customer"] not in universe|set(CLIENTS):
            continue
        valid.append({**e,"proxy_weight":float(weight)})
    adjacency={}
    for e in valid: adjacency.setdefault(e["supplier"],[]).append(e)
    paths=[]
    seen=set()
    for supplier in universe:
        for edge in adjacency.get(supplier,[]):
            if edge["customer"] in CLIENTS:
                key=(supplier,edge["customer"],"direct")
                if key not in seen:
                    paths.append({"supplier":supplier,"customer":edge["customer"],"via":None,
                     "hops":1,"path": [supplier,edge["customer"]],
                     "weight":round(edge["proxy_weight"],6),"sources":[edge["source"]],
                     "dates":[edge["date"]],"weight_kind":"evidence_proxy"})
                    seen.add(key)
            middle=edge["customer"]
            if middle in CLIENTS or middle==supplier:continue
            for downstream in adjacency.get(middle,[]):
                target=downstream["customer"]
                if target not in CLIENTS or supplier==target:continue
                key=(supplier,middle,target)
                if key in seen:continue
                seen.add(key)
                paths.append({"supplier":supplier,"customer":target,"via":middle,
                    "hops":2,"path":[supplier,middle,target],
                    "weight":round(edge["proxy_weight"]*downstream["proxy_weight"]*
                        float(graph.get("hop2_discount",.7)),6),
                    "sources":[edge["source"],downstream["source"]],
                    "dates":[edge["date"],downstream["date"]],
                    "weight_kind":"evidence_proxy"})
    paths.sort(key=lambda p:(p["supplier"],p["customer"],p["hops"],p["via"] or ""))
    exposure={}
    for ticker in sorted(universe):
        path_rows=[p for p in paths if p["supplier"]==ticker]
        by_customer={}
        for customer in CLIENTS:
            candidate=[p for p in path_rows if p["customer"]==customer]
            # Capped sum is a descriptive path index, not independent probability.
            if candidate:
                by_customer[customer]=round(min(1.0,sum(p["weight"] for p in candidate)),6)
        exposure[ticker]={"by_customer":by_customer,
            "reach":round(sum(by_customer.values()),6),
            "direct_customers":len({p["customer"] for p in path_rows if p["hops"]==1}),
            "indirect_customers":len({p["customer"] for p in path_rows if p["hops"]==2}),
            "paths":len(path_rows),"verified_in_graph":bool(path_rows),
            "no_path_is_unknown":not bool(path_rows)}
    return {"graph_version":graph["version"],"as_of":as_of,"verified_edges":valid,
            "paths":paths,"exposures":exposure,
            "method":"Directed 1-hop weight / 2-hop product with 0.70 discount; capped sum; qualitative evidence proxy only",
            "caveat":"A missing/unknown path is not evidence of zero economic exposure, and weights are not correlations or procurement fractions."}

def graph_snapshot(as_of=None):
    universe=load_universe()
    graph=json.loads((ROOT/"config"/"supply_graph.json").read_text(encoding="utf-8"))
    out=compute_paths(graph,[r["ticker"] for r in universe["suppliers"]],as_of)
    return universe,out
