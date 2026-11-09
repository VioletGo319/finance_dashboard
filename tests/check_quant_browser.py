"""Run the actual Quant Lab UI in Chrome with repository's non-synthetic snapshot."""
from pathlib import Path
import json,re,subprocess,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
BROWSER=next((shutil.which(x) for x in ("google-chrome","chromium","google-chrome-stable") if shutil.which(x)),None)
if not BROWSER:
    print("Chrome unavailable; skip browser smoke test (JS syntax CI still enforced)")
    sys.exit(0)
data_path=ROOT/"data"/"quant"/"latest.json"
if not data_path.exists():
    print("Quant snapshot not yet published; skip DOM smoke until first successful pipeline refresh")
    sys.exit(0)
data=json.loads(data_path.read_text())
assert len(data.get("screener",{}).get("ranked",[]))==40
if data.get('benchmark_primary')!='QQQ':
    print('Legacy SPY snapshot; skip DOM smoke until refreshed QQQ history is published')
    sys.exit(0)
assert len(data.get("backtest",{}).get("curve",[]))>20
page=(ROOT/"index.html").read_text(encoding="utf-8")
payload=json.dumps(data,ensure_ascii=False).replace("</script>","<\\/script>")
inject=f"""<script>
const QUANT_SMOKE_DATA={payload};
const originalFetch=window.fetch.bind(window);
window.fetch=(input,opts)=>String(input).includes('data/quant/latest.json')?
 Promise.resolve({{ok:true,json:async()=>QUANT_SMOKE_DATA}}):originalFetch(input,opts);
</script>
"""
# Source is in the same directory as assets; browser can read scripts from file URL.
anchor='<script src="quant-lab.js?v=quant1"></script>'
assert anchor in page
page=page.replace(anchor,inject+anchor)
audit="""<script>
 setTimeout(()=>{
  const first=document.querySelector('#rankingBody tr[data-ticker]')?.dataset.ticker;
  const overviewMatches=Boolean(first&&first===document.getElementById('selectedTicker')?.textContent);
  document.documentElement.dataset.overviewSelection=overviewMatches?'PASS':'FAIL';
  document.querySelector('[data-tab="audit"]')?.click();
  const auditContent=document.querySelector('#auditRows')?.textContent||'';
  const auditSeparated=(auditContent.includes('完整六因子正式评分')&&auditContent.includes('探索性六因子评分'))
    ||(auditContent.includes('Official complete six-factor Alpha')&&auditContent.includes('Exploratory six-factor score'));
  document.documentElement.dataset.auditSeparated=auditSeparated?'PASS':'FAIL';
  document.querySelector('[data-tab="quant"]')?.click();
  setTimeout(()=>{
   try{
    const data=window.M7QuantLab?.data;
    const rows=document.querySelectorAll('#qRanking tr').length;
    const expectedHigh=data?.screener?.ranked?.filter(x=>x.factor_coverage>=.75)?.length||0;
    const coverage=document.querySelector('#qCoverageFilter');
    const defaultGroupIsHigh=coverage?.value==='high';
    if(coverage){
      coverage.value='all';
      coverage.dispatchEvent(new Event('change'));
    }
    const allRows=document.querySelectorAll('#qRanking tr').length;
    const graph=document.querySelector('#qChart svg path');
    const bench=document.querySelector('#qMetrics')?.textContent||'';
    const scenarios=document.querySelector('#qScenario')?.options?.length||0;
    const paper=document.querySelector('#qPaper')?.textContent||'';
    const chosen='5Y · Top 5 · 10 bps';
    const scenarioSelect=document.getElementById('qScenario');
    let dynamicScenario=false, fiscalSeparated=false, metricUpdated=false;
    if(scenarioSelect && [...scenarioSelect.options].some(x=>x.value===chosen)){
      scenarioSelect.value=chosen;
      scenarioSelect.dispatchEvent(new Event('change',{bubbles:true}));
      const d=document.getElementById('qStrategyDescription')?.textContent.toLowerCase()||'';
      const fy=document.getElementById('qFiscalPeriod')?.textContent||'';
      const range=document.getElementById('qCoverage')?.textContent||'';
      const expected=data.backtest_scenarios[chosen];
      const metric=document.getElementById('qMetrics')?.textContent||'';
      dynamicScenario=d.includes('top 5')&&!d.includes('top 8')&&d.includes('10');
      fiscalSeparated=Boolean(fy)&&!fy.includes(expected.start_date+' → '+expected.end_date)
        &&range.includes('Backtest window')&&range.includes('FY');
      metricUpdated=metric.includes((100*expected.metrics.total_return).toFixed(1).slice(0,3));
    }
    document.documentElement.dataset.quantDynamicScenario=dynamicScenario?'PASS':'FAIL';
    document.documentElement.dataset.quantFiscalVsWindow=fiscalSeparated?'PASS':'FAIL';
    document.documentElement.dataset.quantMetricUpdated=metricUpdated?'PASS':'FAIL';
    document.documentElement.dataset.quantDetail='overview:'+overviewMatches+',audit:'+auditSeparated
       +',dynamic:'+dynamicScenario+',fiscal:'+fiscalSeparated+',metrics:'+metricUpdated
       +',rows:'+rows+'/'+expectedHigh+',all:'+allRows+',graph:'+Boolean(graph)
       +',bench:'+bench.includes('QQQ')+',scenarios:'+scenarios+',paper:'+paper.length;
    const success=data?.screener?.eligible_count>0 && data?.backtest?.curve?.length>20 &&
       rows===expectedHigh && expectedHigh>0 && allRows===40 && defaultGroupIsHigh && !!graph && bench.includes('QQQ') && scenarios>=4 &&
       paper.length>0 && overviewMatches && auditSeparated && dynamicScenario && fiscalSeparated && metricUpdated;
    document.documentElement.dataset.quantSmoke=success?'PASS':'FAIL';
    document.documentElement.dataset.quantRows=rows;
    document.documentElement.dataset.quantAllRows=allRows;
    document.documentElement.dataset.quantExpectedHigh=expectedHigh;
    document.documentElement.dataset.quantScenarios=scenarios;
    const sel=document.getElementById('qScenario');
    if(sel&&sel.options.length){
       sel.value=sel.options[0].value;sel.dispatchEvent(new Event('change'));
       document.documentElement.dataset.quantScenario=sel.value;
    }
   }catch(e){document.documentElement.dataset.quantSmoke='ERROR:'+String(e.message)}
  },800);
 },350);
</script>"""
page=page.replace("</body>",audit+"</body>")
tmp=ROOT/"quant-browser-smoke.html"
tmp.write_text(page)
cmd=[BROWSER,"--headless","--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
     "--virtual-time-budget=4500","--dump-dom",tmp.as_uri()]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
match=re.search(r'data-quant-smoke="([^"]+)"',r.stdout)
status=match.group(1) if match else None
print("Quant smoke:",status)
if status!="PASS":
    for key in ("data-quant-detail","data-overview-selection","data-audit-separated","data-quant-dynamic-scenario","data-quant-fiscal-vs-window","data-quant-metric-updated"):
        m=re.search(re.escape(key)+r'="([^"]*)"',r.stdout)
        print(key+":",m.group(1) if m else "N/A")
    print("Missing data/DOM; browser stderr:",r.stderr[-900:])
    raise SystemExit(1)
print("Quant research UI checked 5Y Top 5 scenario description, SEC fiscal period separation, current metrics, selected ranking, and distinct Alpha audit counts.")
