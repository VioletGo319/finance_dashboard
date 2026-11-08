"""Exercise all 5 locales in headless Chromium and report untranslated UI text.

No scraping or network translation: dashboard and dictionaries are self-contained.
"""
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
browser=next((shutil.which(x) for x in ["google-chrome","chromium","google-chrome-stable"] if shutil.which(x)),None)
if browser is None:
    raise SystemExit("Chromium not available; cannot validate language UI")
source=(root/"index.html").read_text(encoding="utf-8")
js=r"""
(function(){
 const pages=['overview','factors','paths','network','events','infrastructure','audit'];
 for(const id of pages){document.querySelector('[data-tab="'+id+'"]')?.click();}
 document.querySelector('[data-tab="paths"]')?.click();
 document.querySelector('#pathRows [data-path-index]')?.click();
 document.querySelector('[data-tab="infrastructure"]')?.click();
 document.querySelector('#infraRows tr[data-infra]')?.click();
 document.querySelector('[data-tab="network"]')?.click();
 document.querySelector('[data-tab="factors"]')?.click();
 const locale=new URLSearchParams(location.search).get('lang')||'en';
 setTimeout(()=>{
   const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
   let node,issues=[];
   const skip=new Set(['SCRIPT','STYLE','NOSCRIPT']);
   while((node=walker.nextNode())){
     const p=node.parentElement;
     if(!p||skip.has(p.tagName)||p.closest('#i18nAudit'))continue;
     if(p.closest('#m7Language'))continue;
     const text=(node.nodeValue||'').replace(/\s+/g,' ').trim();
     if(!text)continue;
     const unrevised=locale==='ja'
       ? /[电储证据资关动变报买预码单项链费统总维经临较该]/u.test(text)
       : (locale!=='zh-CN' && /[\u3400-\u9fff]/u.test(text));
     if(unrevised) issues.push(text);
   }
   const report={locale,selected:window.M7_I18N?.language,issues:[...new Set(issues)].slice(0,100),
      count:[...new Set(issues)].length,
      sector:document.querySelector('#pathCoverageRows')?.textContent?.slice(0,100),
      factors:document.querySelector('#factorHeatmap')?.textContent?.length||0,
      factorNav:document.querySelector('[data-tab="factors"]')?.textContent?.trim(),
      graphNodesLabel:document.getElementById('gNodesLabel')?.textContent?.trim(),
      details:document.getElementById('factorEvidence')?.textContent?.slice(0,500)};
   const el=document.createElement('pre');el.id='i18nAudit';el.setAttribute('data-i18n',encodeURIComponent(JSON.stringify(report)));document.body.append(el);
 },1100);
})();
"""
source=source.replace("</body>","<script>"+js+"</script></body>")
(root/"i18n-coverage.html").write_text(source,encoding="utf-8")
for locale in ["en","zh-CN","fr","es","ja"]:
    cmd=[browser,"--headless","--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
         "--virtual-time-budget=2500","--dump-dom",(root/"i18n-coverage.html").as_uri()+"?lang="+locale]
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    dom=result.stdout.decode("utf-8","replace")
    match=re.search(r'data-i18n="([^"]+)"',dom)
    if not match:
        print(locale,"browser audit failed:",result.stderr.decode("utf-8","replace")[-400:])
        raise SystemExit(1)
    from urllib.parse import unquote
    report=json.loads(html.unescape(unquote(match.group(1))))
    print(locale,"selected="+str(report["selected"]),"untranslated="+str(report["count"]),
          "factors="+str(report["factors"]))
    for issue in report["issues"][:16]:
        print("  ",issue[:160])
    expected_nav={"en":"Factor Research","zh-CN":"因子研究","fr":"Analyse des facteurs",
                  "es":"Análisis de factores","ja":"因子分析"}
    expected_nodes={"en":"NODES","zh-CN":"节点","fr":"NŒUDS","es":"NODOS","ja":"ノード"}
    assert report["selected"]==locale,(locale,report)
    assert report["factorNav"]==expected_nav[locale],(locale,report["factorNav"])
    assert report["graphNodesLabel"]==expected_nodes[locale],(locale,report["graphNodesLabel"])
    assert report["factors"]>800,(locale,report["factors"])
    assert report["count"]==0,(locale,report["issues"][:20])

