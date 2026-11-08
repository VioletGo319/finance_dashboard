"""Conservative point-in-time SEC revenue and share-count retrieval for US issuers.

SEC companyfacts values are stored with filing dates. Never use fiscal-end
date as publication date. Shares×close is only an indicative market-cap proxy,
NOT a provider-verified market cap or an ADR-adjusted equivalent.
"""
from __future__ import annotations
from datetime import date
from urllib.request import Request, urlopen
import json
import os
import time

SEC = "https://data.sec.gov"
REVENUE_TAGS = (
  ("us-gaap","RevenueFromContractWithCustomerExcludingAssessedTax"),
  ("us-gaap","Revenues"), ("us-gaap","SalesRevenueNet"),
  ("us-gaap","RevenueFromContractWithCustomerIncludingAssessedTax"),
  ("ifrs-full","Revenue"), ("ifrs-full","RevenueFromContractsWithCustomers"),
)
SHARE_TAGS=(("dei","EntityCommonStockSharesOutstanding"),
            ("us-gaap","CommonStockSharesOutstanding"))
NET_TAGS=(("us-gaap","NetIncomeLoss"),("ifrs-full","ProfitLoss"))
ALLOWED_FORMS={"10-K","10-K/A","10-Q","10-Q/A","20-F","20-F/A","40-F"}
ANNUAL_FORMS={"10-K","10-K/A","20-F","20-F/A","40-F"}

def fetch_json(url,user_agent):
    if not user_agent or "@" not in user_agent:
        raise ValueError("SEC_USER_AGENT must contain a genuine contact email")
    req=Request(url,headers={"User-Agent":user_agent,"Accept":"application/json"})
    with urlopen(req,timeout=14) as response:
        if response.status!=200:raise ValueError("SEC HTTP "+str(response.status))
        return json.load(response)

def cik_index(user_agent):
    blob=fetch_json("https://www.sec.gov/files/company_tickers.json",user_agent)
    return {str(r["ticker"]).upper():int(r["cik_str"]) for r in blob.values()}

def get_facts(cik,user_agent):
    return fetch_json(f"{SEC}/api/xbrl/companyfacts/CIK{int(cik):010}.json",user_agent)

def as_filed_facts(data,tags,unit,cutoff,annual=False):
    """Historical series keyed by end; choose LAST filing on/before cutoff.

    For historical snapshots rerun this function with a historical cutoff.
    Do not backfill subsequently restated financials before their filing date.
    """
    found=[]
    for priority,(taxonomy,tag) in enumerate(tags):
        values=data.get("facts",{}).get(taxonomy,{}).get(tag,{}).get("units",{}).get(unit,[])
        for fact in values:
            try:
                filed=str(fact["filed"]);end=str(fact["end"])
                if filed>cutoff or end>cutoff or str(fact.get("form")) not in (ANNUAL_FORMS if annual else ALLOWED_FORMS):
                    continue
                value=float(fact["val"])
                if value<=0:continue
                if annual:
                    start=str(fact.get("start",""))
                    duration=(date.fromisoformat(end)-date.fromisoformat(start)).days
                    if not 320<=duration<=395:continue
                found.append({"value":value,"start":fact.get("start"),"end":end,"filed":filed,
                              "form":fact["form"],"tag":tag,"taxonomy":taxonomy,
                              "priority":priority,"accn":fact.get("accn")})
            except (TypeError,ValueError,KeyError):
                continue
    if not found:return []
    # Group by report period, choose lowest-priority tag among entries on latest publication.
    # We prefer a stable standard tag, but never use filings after the cutoff.
    per={}
    for f in found:
        key=f["end"]
        old=per.get(key)
        if old is None or (f["filed"],-f["priority"])>(old["filed"],-old["priority"]):
            per[key]=f
    return sorted(per.values(),key=lambda x:(x["end"],x["filed"]))

def extract_fundamentals(facts,cutoff,ticker="",cik=None):
    rev=as_filed_facts(facts,REVENUE_TAGS,"USD",cutoff,annual=True)
    shares=as_filed_facts(facts,SHARE_TAGS,"shares",cutoff)
    income=as_filed_facts(facts,NET_TAGS,"USD",cutoff,annual=True)
    src=f"{SEC}/api/xbrl/companyfacts/CIK{int(cik):010}.json" if cik else None
    recent_revenues=[x for x in rev if (date.fromisoformat(cutoff)-date.fromisoformat(x["end"])).days<=650]
    latest=recent_revenues[-1] if recent_revenues else None
    prior=next((v for v in reversed(rev[:-1]) if latest and 300<=(date.fromisoformat(latest["end"])-date.fromisoformat(v["end"])).days<=430),None)
    sr=shares[-1] if shares else None
    if sr and (date.fromisoformat(cutoff)-date.fromisoformat(sr["end"])).days>550:sr=None
    # Foreign ADRs can use ordinary shares; reject proxy market capitalization.
    forms={f["form"] for f in (recent_revenues[-2:]+shares[-2:])}
    is_foreign="20-F" in forms or "20-F/A" in forms or "40-F" in forms
    if latest is None: prior=None
    net=next((n for n in reversed(income) if latest and n["end"]==latest["end"]),None)
    return {
      "ticker":ticker,"cik":cik,"source":src,"cutoff":cutoff,
      "revenue_fy_usd":latest["value"] if latest else None,
      "revenue_previous_fy_usd":prior["value"] if prior else None,
      "revenue_growth_yoy":(latest["value"]/prior["value"]-1) if latest and prior else None,
      "revenue_fy_end":latest["end"] if latest else None,
      "revenue_filed":latest["filed"] if latest else None,
      "revenue_tag":latest["tag"] if latest else None,
      "revenue_form":latest["form"] if latest else None,
      "shares_outstanding":sr["value"] if sr and not is_foreign else None,
      "shares_as_of":sr["end"] if sr and not is_foreign else None,
      "shares_filed":sr["filed"] if sr and not is_foreign else None,
      "shares_tag":sr["tag"] if sr and not is_foreign else None,
      "net_income_fy_usd":net["value"] if net else None,
      "foreign_adr_caution":is_foreign,
      "market_cap_method":"indicative SEC-reported shares × latest close; no ADR/split adjustment verification",
      "data_quality":"SEC as-filed annual FY data (filing cutoff), not point-in-time price-confirmed market cap",
      "historical_revenue_filings":rev[-12:],
      "historical_share_filings":shares[-20:] if not is_foreign else [],
    }

def gather_fundamentals(tickers,cutoff,user_agent=None):
    user_agent=user_agent if user_agent is not None else os.environ.get("SEC_USER_AGENT","")
    audit={"source":"SEC EDGAR companyfacts", "cutoff":cutoff, "sec_user_agent_configured":"@" in user_agent,
           "errors":{}, "revenue_covered":0,"share_count_covered":0}
    if "@" not in user_agent:
        audit["status"]="not_configured"
        return {},audit
    try:
        index=cik_index(user_agent)
    except Exception as exc:
        audit["status"]="cik_mapping_unavailable"
        audit["errors"]["cik_index"]=str(exc)[:180]
        return {},audit
    out={}
    for ticker in tickers:
        cik=index.get(ticker)
        if cik is None:
            audit["errors"][ticker]="Ticker not found in SEC company_tickers index"
            continue
        try:
            facts=get_facts(cik,user_agent)
            out[ticker]=extract_fundamentals(facts,cutoff,ticker,cik)
        except Exception as exc:
            audit["errors"][ticker]=str(exc)[:180]
        time.sleep(.11)
    audit["status"]="partial" if audit["errors"] else "retrieved"
    audit["revenue_covered"]=sum(x.get("revenue_fy_usd") is not None for x in out.values())
    audit["share_count_covered"]=sum(x.get("shares_outstanding") is not None for x in out.values())
    return out,audit
