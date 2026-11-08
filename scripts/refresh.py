#!/usr/bin/env python3
"""M7 Supplier Alpha public-data refresh (standard library, fail-closed).
This is a partial research implementation: missing factors remain null.
Do not interpret exploratory scores as investment probabilities.
"""
from __future__ import annotations
import csv
import io
import json
import os
import statistics
import sys
from datetime import date, datetime, timedelta, timezone, time
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
try:
    from scripts.network import graph_snapshot
    from scripts.enrichment import annual_capex_fallback, disclosed_share_change, monitoring_scores, dataset_health
except ModuleNotFoundError:
    from network import graph_snapshot
    from enrichment import annual_capex_fallback, disclosed_share_change, monitoring_scores, dataset_health
TICKERS = tuple(row["ticker"] for row in graph_snapshot()[0]["suppliers"])
CLIENTS = ("AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA")
WEIGHTS = {"acceleration": .30, "demand": .25, "tightness": .15, "customer_momentum": .15, "policy": .10, "residual_momentum": .05}
UA = "M7 Supplier Alpha academic public data research (non-commercial)"
LOCAL_NOW=datetime.now(ZoneInfo("America/New_York"))
AS_OF=LOCAL_NOW.date().isoformat()
# Ignore incomplete current-session bars before official close.
MARKET_CUTOFF=(LOCAL_NOW.date() if LOCAL_NOW.weekday()<5 and LOCAL_NOW.time()>=time(16,15)
               else LOCAL_NOW.date()-timedelta(days=1)).isoformat()

def fetch_text(url):
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json,text/csv,*/*"})
    with urlopen(req, timeout=16) as response:
        if response.status != 200:
            raise ValueError(f"HTTP {response.status}")
        return response.read().decode("utf-8", "replace")

def get_stooq(symbol):
    start = (date.today() - timedelta(days=330)).strftime("%Y%m%d")
    end = date.today().strftime("%Y%m%d")
    url = f"https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d&d1={start}&d2={end}"
    bars = []
    for row in csv.DictReader(io.StringIO(fetch_text(url))):
        try:
            d, p = row["Date"], float(row["Close"])
            if d <= MARKET_CUTOFF and p > 0: bars.append((d, p))
        except (KeyError, TypeError, ValueError):
            pass
    return bars, url, "Stooq EOD"

def get_yahoo(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol)}?range=9mo&interval=1d"
    j = json.loads(fetch_text(url))["chart"]["result"][0]
    q = j["indicators"]["quote"][0]["close"]
    bars = []
    for stamp, p in zip(j.get("timestamp", []), q):
        if p is None or p <= 0: continue
        d = datetime.fromtimestamp(stamp, timezone.utc).date().isoformat()
        if d <= MARKET_CUTOFF: bars.append((d, float(p)))
    return bars, url, "Yahoo chart"

def prices(symbol):
    errors=[]
    for retrieve in (get_stooq, get_yahoo):
        try:
            bars, url, provider = retrieve(symbol)
            bars=sorted(dict(bars).items())
            if len(bars) < 65: raise ValueError("fewer than 65 daily closes")
            if (LOCAL_NOW.date()-date.fromisoformat(bars[-1][0])).days > 7: raise ValueError("stale close")
            if bars[-1][1] <= 0 or bars[-2][1] <= 0: raise ValueError("bad price")
            return {"bars": bars, "url": url, "provider": provider, "error": None}
        except Exception as exc:
            errors.append(f"{retrieve.__name__}: {str(exc)[:130]}")
    return {"bars": [], "url": None, "provider": None, "error": "; ".join(errors)}

def pct_rank(value, peers):
    if value is None: return None
    nums = sorted(x for x in peers if isinstance(x, (int, float)) and not isinstance(x, bool))
    if len(nums) < 3: return None
    return round(100 * (sum(x<value for x in nums) + .5*sum(x==value for x in nums) - .5)/(len(nums)-1), 2)

def twenty_day_return(bars):
    if len(bars) < 21: return None
    return bars[-1][1]/bars[-21][1]-1 if bars[-21][1] else None

def residual(bars, market):
    a = dict(bars)
    b = dict(market)
    sessions = sorted(set(a) & set(b))[-61:]
    if len(sessions) < 61: return None
    xs=[b[sessions[i]]/b[sessions[i-1]]-1 for i in range(1,61)]
    ys=[a[sessions[i]]/a[sessions[i-1]]-1 for i in range(1,61)]
    xm,ym=statistics.mean(xs),statistics.mean(ys)
    variance=sum((x-xm)**2 for x in xs)
    if variance < 1e-14: return None
    beta=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/variance
    return a[sessions[-1]]/a[sessions[-21]]-1 - beta*(b[sessions[-1]]/b[sessions[-21]]-1)

def calculate(base, quotes):
    network=base.get("network") or {"exposures":{}}
    weighted=network.get("exposures",{})
    verified=[e for e in base.get("relationships",[]) if e.get("verified") is True and e.get("date") and e["date"] <= AS_OF and str(e.get("source","")).startswith("https://")]
    out=[]
    benchmark=quotes.get("XLK",{}).get("bars",[])
    raw_customer={}
    raw_residual={}
    for ticker in TICKERS:
        weights=weighted.get(ticker,{}).get("by_customer",{})
        numerator=0.0
        denominator=0.0
        for customer,w in weights.items():
            v=twenty_day_return(quotes.get(customer,{}).get("bars",[]))
            if v is None or not w: continue
            numerator+=w*v
            denominator+=w
        raw_customer[ticker]=(numerator/denominator if denominator else None)
        raw_residual[ticker]=residual(quotes.get(ticker,{}).get("bars",[]),benchmark)
    monitor=monitoring_scores(quotes,TICKERS,pct_rank,raw_residual)
    for original in base.get("suppliers",[]):
        ticker=original["ticker"]
        row=dict(original)
        q=quotes.get(ticker, {})
        bars=q.get("bars", [])
        row.update({"close":round(bars[-1][1],4) if bars else None,
                    "previous_close":round(bars[-2][1],4) if len(bars)>1 else None,
                    "price_date":bars[-1][0] if bars else None,
                    "previous_price_date":bars[-2][0] if len(bars)>1 else None,
                    "price_source":q.get("url"),
                    "price_provider":q.get("provider"),
                    "price_fresh":bool(bars)})
        scores={key:None for key in WEIGHTS}
        scores["demand"]=row.get("factors",{}).get("demand")
        scores["acceleration"]=row.get("factors",{}).get("acceleration")
        scores["tightness"]=pct_rank(weighted.get(ticker,{}).get("reach") if weighted.get(ticker,{}).get("verified_in_graph") else None,
                     [v["reach"] for v in weighted.values() if v.get("verified_in_graph")])
        scores["customer_momentum"]=pct_rank(raw_customer[ticker], list(raw_customer.values()))
        scores["residual_momentum"]=pct_rank(raw_residual[ticker], list(raw_residual.values()))
        # Keep only previously verified structural factors; no guessing missing policy/CapEx.
        for key in WEIGHTS:
            value=scores.get(key)
            if not isinstance(value,(int,float)) or not 0<=value<=100: scores[key]=None
        coverage=sum(WEIGHTS[key] for key,value in scores.items() if key in WEIGHTS and value is not None)
        complete=coverage > 0.9999
        provisional=(sum(WEIGHTS[k]*v for k,v in scores.items() if k in WEIGHTS and v is not None)/coverage
                     if coverage>=.19 and sum(v is not None for v in scores.values())>=2 else None)
        row["network_reach"]=weighted.get(ticker,{}).get("reach") if weighted.get(ticker,{}).get("verified_in_graph") else None
        row["direct_clients"]=weighted.get(ticker,{}).get("direct_customers",0)
        row["indirect_clients"]=weighted.get(ticker,{}).get("indirect_customers",0)
        row["paths"]=weighted.get(ticker,{}).get("paths",0)
        row["third_hop_clients"]=weighted.get(ticker,{}).get("third_hop_clients",0)
        row["factors"]=scores
        row["monitor_score"]=monitor.get(ticker)
        row["monitor_method"]="PRICE ONLY: 60% sector-adjusted 20-day residual rank + 40% five-session price-return rank; NOT M7 supply Alpha"
        row["factor_sources"]=row.get("factor_sources",{})
        row["factor_methods"]=row.get("factor_methods",{})
        row["coverage"]=round(coverage,4)
        row["alpha"]=round(sum(WEIGHTS[k]*scores[k] for k in WEIGHTS),2) if complete else None
        row["provisional_alpha"]=round(provisional,2) if provisional is not None else None
        prev=base.get("_prior_suppliers",{}).get(ticker,{})
        prior_value=prev.get("alpha")
        prior_prov=prev.get("provisional_alpha")
        comparable=prev.get("model_version")==base.get("model_version") and prev.get("coverage")==row["coverage"] and prev.get("price_date")!=row.get("price_date")
        row["previous_alpha"]=prior_value if complete and comparable else None
        row["previous_provisional_alpha"]=prior_prov if not complete and comparable else None
        row["confidence"]="研究探索" if not complete else "六因子已覆盖"
        row["model_version"]=base.get("model_version","v3.1-40-multihop")
        row["explanation"]=(f"已核实客户关系；行情来自 {q.get('provider') or '不可用'}。"
                            +("六因子数据不完整，仅提供带覆盖率的探索性评分。" if not complete else "六因子完整。"))
        hist=list(row.get("history") or [])
        current=row["alpha"] if complete else row["provisional_alpha"]
        if current is not None and (not hist or hist[-1].get("date")!=AS_OF):
            hist.append({"date":AS_OF,"alpha":current,"mode":"official" if complete else "provisional",
                         "model_version":base.get("model_version"),"coverage":row["coverage"]})
        row["history"]=hist[-90:]
        out.append(row)
    result=dict(base)
    result.pop("_prior_suppliers",None)
    result["suppliers"]=out
    result["as_of"]=AS_OF
    dates=[s["price_date"] for s in out if s.get("price_date")]
    result["price_date"]=max(dates) if dates else None
    result["previous_price_date"]=max((s["previous_price_date"] for s in out if s.get("previous_price_date")),default=None)
    result["retrieved_at_utc"]=datetime.now(timezone.utc).isoformat()
    result["mode"]="partial"
    audit=dict(result.get("audit") or {})
    audit["market_prices_present"]=len(dates)
    audit["market_prices_total"]=len(TICKERS)
    audit["official_alpha_count"]=sum(s["alpha"] is not None for s in out)
    audit["provisional_count"]=sum(s["provisional_alpha"] is not None for s in out)
    audit["market_qa_errors"]=[{"ticker":t,"message":quotes[t]["error"]} for t in TICKERS if quotes[t].get("error")]
    audit["verified_graph_paths"]=len(network.get("paths",[]))
    audit["verified_graph_edges"]=len(network.get("verified_edges",[]))
    audit["data_health"]=dataset_health(out,WEIGHTS)
    audit["seed_capex_clients"]=list(base.get("capex_sources",{}))
    audit["model_caveat"]="Strict six-factor Alpha N/A unless all six inputs verified. Research factors may use explicitly labeled audited CapEx YoY / customer-share change proxies; market monitor is PRICE ONLY."
    result["audit"]=audit
    return result


# Public regulatory data is candidate-only unless a human validates the original.
CLIENT_CIK={"AAPL":320193,"MSFT":789019,"GOOGL":1652044,"AMZN":1018724,"NVDA":1045810,"META":1326801,"TSLA":1318605}

def fetch_sec_json(url):
    contact=os.environ.get("SEC_USER_AGENT","")
    if "@" not in contact:
        raise ValueError("SEC_USER_AGENT must include researcher contact email")
    req=Request(url,headers={"User-Agent":contact,"Accept":"application/json"})
    with urlopen(req,timeout=20) as f:
        if f.status!=200: raise ValueError(f"SEC HTTP {f.status}")
        return json.load(f)

def capex_growth(symbol):
    cik=CLIENT_CIK[symbol]
    url=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010}.json"
    obj=fetch_sec_json(url)
    values=obj.get("facts",{}).get("us-gaap",{}).get("PaymentsToAcquirePropertyPlantAndEquipment",{}).get("units",{}).get("USD",[])
    yearly={}
    for v in sorted(values,key=lambda a:a.get("filed","")):
        try:
            if v["filed"]>AS_OF or v["form"] not in ("10-K","10-K/A") or v["val"]<=0:continue
            days=(date.fromisoformat(v["end"])-date.fromisoformat(v["start"])).days
            if 330<=days<=390:yearly.setdefault(v["end"],v)
        except (ValueError,TypeError,KeyError):continue
    items=sorted(yearly.values(),key=lambda a:a["end"])
    if len(items)<2:return None
    latest,prior=items[-1],items[-2]
    if not 280<=(date.fromisoformat(latest["end"])-date.fromisoformat(prior["end"])).days<=450:return None
    if (LOCAL_NOW.date()-date.fromisoformat(latest["filed"])).days>500:return None
    return {"growth":latest["val"]/prior["val"]-1,"filed":latest["filed"],"url":url,"method":"Annual SEC PP&E purchase growth proxy; NOT analyst consensus surprise"}

def collect_filing_candidates(symbol):
    cik=CLIENT_CIK[symbol]
    obj=fetch_sec_json(f"https://data.sec.gov/submissions/CIK{cik:010}.json")
    rec=obj["filings"]["recent"]
    rows=[]
    for i,form in enumerate(rec.get("form",[])):
        if form not in ("8-K","10-K","10-Q"):continue
        filed=rec["filingDate"][i]
        if filed>AS_OF or (LOCAL_NOW.date()-date.fromisoformat(filed)).days>30:continue
        accession=rec["accessionNumber"][i].replace("-","")
        doc=rec["primaryDocument"][i]
        rows.append({"ticker":symbol,"date":filed,"title":f"{symbol} {form}","form":form,
          "source":f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}",
          "status":"UNVERIFIED filing candidate; excluded from scores"})
        if len(rows)>=8:break
    return rows

def collect_policy_candidates():
    from urllib.parse import urlencode
    seen=set();rows=[]
    start=(LOCAL_NOW.date()-timedelta(days=14)).isoformat()
    for term in ("semiconductor","export control","data center"):
        params=urlencode({"conditions[term]":term,"conditions[publication_date][gte]":start,
          "conditions[publication_date][lte]":AS_OF,"order":"newest","per_page":"12"})
        try:
            j=json.loads(fetch_text("https://www.federalregister.gov/api/v1/documents.json?"+params))
            for d in j.get("results",[]):
                num=d.get("document_number")
                if not num or num in seen or d.get("publication_date","")>AS_OF:continue
                seen.add(num)
                rows.append({"date":d.get("publication_date"),"title":d.get("title"),
                  "source":d.get("html_url") or f"https://www.federalregister.gov/d/{num}",
                  "status":"UNREVIEWED policy candidate; excluded from factor scores"})
        except Exception as exc:
            print(f"Federal Register candidate lookup failed: {exc}",file=sys.stderr)
    return sorted(rows,key=lambda a:a.get("date") or "",reverse=True)[:30]

def enrich_regulatory_data(base):
    """Fetch SEC when configured; otherwise use validated, date-scoped annual figures."""
    capex=annual_capex_fallback(AS_OF)
    filings=[]
    if "@" in os.environ.get("SEC_USER_AGENT",""):
        for client in CLIENTS:
            try:
                record=capex_growth(client)
                if record is not None:
                    # Live SEC filing supersedes manual annual benchmark only when newer.
                    prior=capex.get(client)
                    if prior is None or record["filed"]>=prior["filed"]:
                        capex[client]={**record,"source":record["url"],"quality":"sec_companyfacts",
                                       "method":"annual_capex_yoy_proxy"}
                filings.extend(collect_filing_candidates(client))
            except Exception as exc:
                print(f"SEC {client}: {str(exc)[:160]}",file=sys.stderr)
    exposure=base.get("network",{}).get("exposures",{})
    raw_demand={}
    for row in base["suppliers"]:
        ticker=row["ticker"]
        weights=exposure.get(ticker,{}).get("by_customer",{})
        points=[(capex[c]["growth"],w,c) for c,w in weights.items() if c in capex and w>0]
        raw_demand[ticker]=sum(g*w for g,w,_ in points)/sum(w for _,w,_ in points) if points else None
        row.setdefault("factor_sources",{})
        row.setdefault("factor_methods",{})
        if points:
            row["factor_sources"]["demand"]=[capex[c]["source"] for _,_,c in points]
            row["factor_methods"]["demand"]="Audited annual client CapEx YoY, multi-hop-weighted; proxy, NOT analyst-consensus surprise; fiscal years/definitions vary"
    shares=disclosed_share_change(base.get("network",{}).get("verified_edges",[]),AS_OF)
    raw_share={t:sum(r["change_pp"] for r in recs)/len(recs) for t,recs in shares.items()}
    for row in base["suppliers"]:
        t=row["ticker"]
        row.setdefault("factors",{})
        row["factors"]["demand"]=pct_rank(raw_demand[t],[v for v in raw_demand.values() if v is not None])
        row["factors"]["acceleration"]=pct_rank(raw_share.get(t),list(raw_share.values()))
        if t in shares:
            row["factor_sources"]["acceleration"]=[r["source"] for r in shares[t]]
            row["factor_methods"]["acceleration"]="Reported change in customer-revenue concentration (percentage points) proxy; NOT actual order acceleration"
    base["filing_candidates"]=filings[:45]
    base["policy_candidates"]=collect_policy_candidates()
    base["capex_sources"]={k:v["source"] for k,v in capex.items()}
    base["capex_records"]=capex
    base["customer_share_changes"]=[rec for recs in shares.values() for rec in recs]
    base.setdefault("audit",{})["capex_annual_yoy_clients"]=sorted(capex)
    base["audit"]["customer_share_change_suppliers"]=sorted(shares)

def load_infrastructure_attributes(as_of=AS_OF):
    """Load sourced sector capabilities, never inferred customer relationships.

    Treat absent capabilities as UNKNOWN, not as negative or zero exposures.
    Asset values and contract amounts are intentionally not estimated.
    """
    file=ROOT/"config"/"infrastructure_dimensions.json"
    if not file.exists():
        return {"schema_version":"1.0","dimensions":[],"exposures":[],
                "warning":"Classification file unavailable; no exposure claims"}
    raw=json.loads(file.read_text(encoding="utf-8"))
    allowed={"energy","power","storage"}
    dimensions=raw.get("dimensions",[])
    if set(d["id"] for d in dimensions)!=allowed:
        raise ValueError("Infrastructure taxonomy must contain precisely energy, power, storage")
    valid=[]
    seen=set()
    for e in raw.get("exposures",[]):
        ticker=e.get("ticker")
        category=e.get("dimension")
        checked=e.get("verified_on")
        source=e.get("source")
        if ticker not in TICKERS or category not in allowed: raise ValueError("Unknown ticker or infrastructure dimension")
        if (ticker,category) in seen: raise ValueError("Duplicate infrastructure attribute")
        seen.add((ticker,category))
        if e.get("status")!="verified_product" or not isinstance(source,str) or not source.startswith("https://"):
            raise ValueError("Infrastructure attributes must link verified primary evidence")
        if not isinstance(checked,str) or len(checked)!=10: raise ValueError("Missing verification date")
        date.fromisoformat(checked)
        if checked>as_of: continue  # point-in-time cutoff, no future information
        if e.get("customer_verified") is not False: raise ValueError("Product capability is not an M7 contract")
        valid.append(e)
    return {**raw,"exposures":valid,"classification_counts":{
        d:sum(x["dimension"]==d for x in valid) for d in allowed},
        "unverified_is_unknown":True}

def main():
    src=ROOT/"data"/"latest.json"
    base=json.loads(src.read_text(encoding="utf-8"))
    universe,network=graph_snapshot(AS_OF)
    existing={r["ticker"]:r for r in base.get("suppliers",[])}
    base["_prior_suppliers"]=existing
    refreshed=[]
    for spec in universe["suppliers"]:
        old=existing.get(spec["ticker"],{})
        row={"ticker":spec["ticker"],"name":spec["name"],
             "sector":spec["sector"],"cohort":spec["cohort"],
             "model_version":"v3.1-40-multihop",
             "history":[h for h in old.get("history",[]) if h.get("model_version")==base.get("model_version") and h.get("mode") in ("official","provisional")],
             "factors":{key:None for key in WEIGHTS}}
        refreshed.append(row)
    base["suppliers"]=refreshed
    base["universe"]=universe
    base["network"]=network
    base["model_version"]="v3.1-40-multihop"
    base["infrastructure"] = load_infrastructure_attributes()
    universe=tuple(dict.fromkeys(TICKERS+CLIENTS+("XLK",)))
    quotes={}
    for symbol in universe:
        quotes[symbol]=prices(symbol)
        print(f"{symbol}: {len(quotes[symbol]['bars'])} closes; {quotes[symbol].get('error') or 'ok'}",flush=True)
    enrich_regulatory_data(base)
    result=calculate(base,quotes)
    src.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    snapshots=ROOT/"data"/"snapshots"
    snapshots.mkdir(parents=True,exist_ok=True)
    (snapshots/(AS_OF+".json")).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    site=ROOT/"site"
    (site/"data").mkdir(parents=True,exist_ok=True)
    (site/"data"/"latest.json").write_bytes(src.read_bytes())
    print("Price coverage:",result["audit"]["market_prices_present"],"/",len(TICKERS))
    print("Official scores:",result["audit"]["official_alpha_count"])
    return 0

if __name__=="__main__":
    sys.exit(main())
