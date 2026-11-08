"""Directed, dated multi-hop supplier evidence graph.

Weights are QUANTITATIVE LABELS FOR EVIDENCE QUALITY, not actual customer
spend fractions, statistical correlations, profits or transmission probabilities.
We only infer routes where every segment was affirmatively disclosed.
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
    symbols=[row["ticker"] for row in rows]
    if len(symbols)!=40 or len(set(symbols))!=40:
        raise ValueError("The fixed v3 research universe must contain exactly 40 unique tickers")
    return payload

def compute_paths(graph,universe,as_of=None):
    """Multiply edge proxy weights along simple supplier -> M7 paths.

    If edges are w1, w2,...,wk, then path strength is
    (product of edges) * hop_discount ** (k - 1).

    Missing edges are UNKNOWN. Multiple paths share nodes and are not
    independent probabilities; per-destination aggregation is descriptive.
    """
    as_of=as_of or date.today().isoformat()
    members=set(universe)
    allowed=members|set(CLIENTS)
    types=graph["edge_types"]
    valid=[]
    for e in graph.get("edges",[]):
        if not e.get("verified") or not e.get("date") or e["date"]>as_of:
            continue
        if not str(e.get("source","")).startswith("https://"):
            continue
        weight=types.get(e.get("edge_type"),{}).get("proxy_weight")
        if not isinstance(weight,(float,int)) or not 0<=weight<=1:
            continue
        if e["supplier"] not in members or e["customer"] not in allowed:
            continue
        valid.append({**e,"proxy_weight":float(weight)})
    adj={}
    for edge in valid: adj.setdefault(edge["supplier"],[]).append(edge)
    paths=[]
    seen=set()
    max_hops=max(1,min(3,int(graph.get("max_hops",2))))
    discount=float(graph.get("hop2_discount",.7))
    if not 0<=discount<=1: raise ValueError("Invalid hop discount")
    for origin in sorted(members):
        def walk(now,nodes,edges,product):
            if len(edges)>=max_hops:return
            for edge in adj.get(now,[]):
                destination=edge["customer"]
                if destination in nodes:continue
                next_nodes=nodes+[destination]
                next_edges=edges+[edge]
                next_product=product*edge["proxy_weight"]
                if destination in CLIENTS:
                    key=tuple(next_nodes)
                    if key in seen:continue
                    seen.add(key)
                    hops=len(next_edges)
                    paths.append({"supplier":origin,"customer":destination,
                        "via":next_nodes[1] if hops>1 else None,
                        "via_nodes":next_nodes[1:-1],"hops":hops,
                        "path":next_nodes,"weight":round(next_product*discount**(hops-1),6),
                        "sources":[e["source"] for e in next_edges],
                        "dates":[e["date"] for e in next_edges],
                        "edge_weights":[e["proxy_weight"] for e in next_edges],
                        "weight_kind":"evidence_proxy"})
                elif destination in members:
                    walk(destination,next_nodes,next_edges,next_product)
        walk(origin,[origin],[],1.0)
    paths.sort(key=lambda p:(p["supplier"],p["customer"],p["hops"],p["path"]))
    exposures={}
    for ticker in sorted(members):
        ps=[p for p in paths if p["supplier"]==ticker]
        by_customer={}
        for client in CLIENTS:
            selections=[p["weight"] for p in ps if p["customer"]==client]
            if selections:by_customer[client]=round(min(1.0,sum(selections)),6)
        exposures[ticker]={
            "by_customer":by_customer,
            "reach":round(sum(by_customer.values()),6),
            "direct_customers":len({p["customer"] for p in ps if p["hops"]==1}),
            "indirect_customers":len({p["customer"] for p in ps if p["hops"]>=2}),
            "third_hop_clients":len({p["customer"] for p in ps if p["hops"]==3}),
            "paths":len(ps),"verified_in_graph":bool(ps),
            "no_path_is_unknown":not bool(ps)}
    return {"graph_version":graph["version"],"as_of":as_of,
        "verified_edges":valid,"paths":paths,"exposures":exposures,
        "method":"Directed 1–3 hop evidence proxy path product; per extra hop × 0.70; capped sum per M7 client.",
        "caveat":"These numbers are not dollar shares, statistical correlations or forecast probabilities. No verified path is Unknown, not zero."}

def graph_snapshot(as_of=None):
    universe=load_universe()
    graph=json.loads((ROOT/"config"/"supply_graph.json").read_text(encoding="utf-8"))
    result=compute_paths(graph,[r["ticker"] for r in universe["suppliers"]],as_of)
    return universe,result
