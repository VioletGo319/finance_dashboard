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
     if(locale!=='zh-CN' && /[\u3400-\u9fff]/.test(text))issues.push(text);
   }
   const report={locale,selected:window.M7_I18N?.language,issues:[...new Set(issues)].slice(0,100),
      count:[...new Set(issues)].length,
      sector:document.querySelector('#pathCoverageRows')?.textContent?.slice(0,100),
      factors:document.querySelector('#factorHeatmap')?.textContent?.length||0};
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
    for issue in report["issues"][:25]:
        print("  ",issue[:160])
