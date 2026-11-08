
/* M7 dashboard i18n: local, no external translation service.
 * Source UI uses Chinese strings. All locale labels and facts preserve raw
 * tickers, dates, prices, URLs and factor calculations.
 */
(() => {
 'use strict';
 const LOCALES = ['en','zh-CN','fr','es','ja'];
 const languageNames = {en:'English','zh-CN':'中文',fr:'Français',es:'Español',ja:'日本語'};
 const values = [["语言","Language","Langue","Idioma","言語"],["数据管道连接中 · 历史证据已标注","Connecting data pipeline · Historical evidence labeled","Connexion au pipeline · Sources historiques identifiées","Conectando datos · Evidencia histórica etiquetada","データ接続中・過去の根拠を表示"],["↓ JSON 模板","↓ JSON template","↓ Modèle JSON","↓ Plantilla JSON","↓ JSONテンプレート"],["↥ 导入日报数据","↥ Import daily data","↥ Importer les données","↥ Importar datos diarios","↥ 日次データを読み込む"],["上游供应链研究看板","Upstream Supply Chain Research Dashboard","Tableau de bord de recherche sur la chaîne d’approvisionnement","Panel de investigación de la cadena de suministro","上流サプライチェーン研究ダッシュボード"],["扩展研究池 · 40家（12核心 + 28候选）","Expanded universe · 40 stocks (12 core + 28 candidates)","Univers élargi · 40 titres (12 principaux + 28 candidats)","Universo ampliado · 40 acciones (12 principales + 28 candidatas)","拡張ユニバース・40銘柄（中核12＋候補28）"],["六因子 · 固定权重","Six factors · Fixed weights","Six facteurs · Pondérations fixes","Seis factores · Pesos fijos","6因子・固定ウェイト"],["直接关系 / 二级关系分层","Direct and indirect links separated","Liens directs et indirects distincts","Vínculos directos e indirectos separados","直接・間接関係を区別"],["展示模式：模拟分数","Display mode: Illustrative scores","Mode : scores illustratifs","Modo: puntuaciones ilustrativas","表示モード：サンプルスコア"],["总览 · Alpha","Overview · Alpha","Vue d’ensemble · Alpha","Resumen · Alpha","概要・アルファ"],["因子研究","Factor Research","Analyse des facteurs","Análisis de factores","因子分析"],["供应链网络","Supply Network","Réseau d’approvisionnement","Red de suministro","サプライチェーンネットワーク"],["多跳 · 路径乘积","Multi-hop · Path Products","Multi-sauts · Produits des chemins","Multisalto · Productos de rutas","多段・経路積"],["政策与事件","Policy & Events","Politiques et événements","Políticas y eventos","政策・イベント"],["能源 · 电力 · 储能","Energy · Power · Storage","Énergie · Électricité · Stockage","Energía · Electricidad · Almacenamiento","エネルギー・電力・蓄電"],["数据审计","Data Audit","Audit des données","Auditoría de datos","データ監査"],["固定供应商池","Supplier Universe","Univers des fournisseurs","Universo de proveedores","サプライヤー銘柄群"],["美股及美股交易 ADR · 比较样本不变","US-listed shares & ADRs · Fixed sample","Actions et ADR cotés aux États-Unis · Échantillon fixe","Acciones y ADR cotizados en EE. UU. · Muestra fija","米国上場株・ADR・固定サンプル"],["综合 Alpha 均值","Mean Composite Alpha","Alpha composite moyen","Alfa compuesto medio","総合アルファ平均"],["有证据的客户关系","Documented Customer Links","Relations clients documentées","Relaciones con clientes documentadas","根拠のある顧客関係"],["仅统计附原始网址的明确关系","Count documented links with primary sources only","Liens explicites avec sources primaires uniquement","Solo vínculos documentados con fuentes primarias","一次資料付きの確認済み関係のみ"],["价格数据完整度","Price Data Coverage","Couverture des cours","Cobertura de precios","価格データ網羅率"],["当前 / 前一交易日正式收盘价","Latest / previous trading-session closes","Clôtures des deux dernières séances","Cierres de las dos últimas sesiones","直近・前取引日の終値"],["供应链投资观察评分（†为探索性）","Supply Chain Investment Research Scores († exploratory)","Scores d’investissement de la chaîne († exploratoires)","Puntuaciones de investigación de inversión († exploratorias)","サプライチェーン投資研究スコア（†参考値）"],["点击股票查看六因子拆解；表头可排序","Select a stock to examine six factors; click headers to sort","Sélectionnez un titre pour voir les six facteurs ; triez via les en-têtes","Seleccione una acción para ver los seis factores; ordene por columnas","銘柄を選択して6因子を表示・列見出しで並べ替え"],["模拟评分","Illustrative score","Score illustratif","Puntuación ilustrativa","サンプルスコア"],["股票 ↕","Ticker ↕","Symbole ↕","Símbolo ↕","銘柄 ↕"],["Δ分数 ↕","Δ Score ↕","Δ Score ↕","Δ Puntuación ↕","スコア変化 ↕"],["最新收盘价 ↕","Latest Close ↕","Dernière clôture ↕","Último cierre ↕","直近終値 ↕"],["前收盘价 ↕","Prior Close ↕","Clôture précédente ↕","Cierre anterior ↕","前日終値 ↕"],["日涨跌 ↕","Daily Change ↕","Variation du jour ↕","Variación diaria ↕","日次騰落 ↕"],["证据覆盖 ↕","Evidence Coverage ↕","Couverture des preuves ↕","Cobertura de evidencia ↕","根拠網羅率 ↕"],["供应商研究卡","Supplier Research Detail","Profil de recherche du fournisseur","Ficha de investigación del proveedor","サプライヤー調査詳細"],["可点击排行榜切换公司","Select a row to switch companies","Sélectionnez une ligne pour changer d’entreprise","Seleccione una fila para cambiar de empresa","行を選択して会社を切替"],["研究解释","Research Interpretation","Interprétation de recherche","Interpretación de investigación","研究上の解釈"],["证据覆盖：—","Evidence coverage: —","Couverture des preuves : —","Cobertura de evidencia: —","根拠網羅率：—"],["查看相关证据 →","View Evidence →","Voir les sources →","Ver evidencia →","関連証拠を見る →"],["Alpha 分数历史","Alpha Score History","Historique du score Alpha","Historial de puntuación Alfa","アルファスコア履歴"],["检验因子是否领先股价，而不是只反映价格变化","Test whether signals lead prices rather than merely reflect them","Tester si les signaux précèdent les cours","Comprobar si las señales anticipan los precios","指標が株価に先行するかを検証"],["演示趋势，非历史真实评分。","Illustrative trend, not observed historical scores.","Tendance illustrative, pas de scores historiques observés.","Tendencia ilustrativa, no puntuaciones históricas reales.","実際の履歴ではなく例示の推移"],["事件速览","Event Highlights","Événements clés","Eventos destacados","イベント概要"],["已公开的历史事件，非实时新闻","Published historical events; not live news","Événements historiques publiés ; pas d’actualité en direct","Eventos históricos publicados; no noticias en vivo","公開済みの過去イベント（速報ではありません）"],["查看全部 →","View All →","Tout voir →","Ver todo →","すべて表示 →"],["横截面因子热力图","Cross-sectional Factor Heatmap","Carte thermique des facteurs","Mapa de calor de factores","クロスセクション因子ヒートマップ"],["数值范围 0–100；基于公开数据、可审计的点时计算数据","0–100 values; source-audited point-in-time data","Valeurs 0–100 ; données datées et vérifiables","Valores 0–100; datos auditables en el momento","0–100、日時付き検証可能なデータ"],["因子贡献拆分","Factor Contribution Breakdown","Décomposition des contributions","Desglose de aportaciones factoriales","因子寄与度内訳"],["贡献 = 因子分数 × 固定权重；不代表收益贡献","Contribution = factor score × weight; not investment return","Contribution = score × poids ; pas un rendement","Contribución = factor × peso; no es rentabilidad","寄与度＝因子スコア×固定ウェイト（収益ではない）"],["研究假设","Research Hypothesis","Hypothèse de recherche","Hipótesis de investigación","研究仮説"],["固定因子方法与权重","Fixed Factor Methods & Weights","Méthodes et pondérations fixes","Métodos y pesos fijos","固定因子手法とウェイト"],["跨日不得无说明地调整权重或标准化口径","Do not change weights or scaling across dates without disclosure","Ne pas modifier les poids ou la normalisation sans explication","No cambiar pesos ni normalización sin explicación","説明なしで日付間のウェイトや標準化を変更しない"],["多层供应链 · 路径乘积模型","Multilayer Supply Chain · Path Product Model","Chaîne multi-niveaux · Produit des chemins","Cadena multinivel · Producto de rutas","多層サプライチェーン・経路積モデル"],["路径计算","Path Calculation","Calcul des chemins","Cálculo de rutas","経路計算"],["定性关系证据代理值","qualitative evidence-link proxy","indice qualitatif des liens documentés","índice cualitativo de vínculos documentados","定性的な証拠連携代理値"],["上市研究样本","Listed Research Universe","Univers de recherche coté","Universo bursátil de investigación","上場調査対象"],["12核心 + 28候选","12 core + 28 candidates","12 principaux + 28 candidats","12 principales + 28 candidatos","中核12＋候補28"],["已核验网络边","Verified Graph Edges","Arêtes du graphe vérifiées","Aristas verificadas","確認済みネットワーク辺"],["仅使用来源和披露日期齐备的边","Only dated edges with traceable sources","Arêtes datées avec source traçable uniquement","Solo aristas fechadas con fuente verificable","出典と公開日を確認できる辺のみ"],["可计算的两跳路径","Computable Two-hop Paths","Chemins à deux sauts calculables","Rutas calculables de dos saltos","計算可能な2ホップ経路"],["暂不把未知关系视为0","Unknown links are not treated as zero","Les liens inconnus ne sont pas assimilés à zéro","Los vínculos desconocidos no son cero","不明な関係をゼロとみなさない"],["全部供应商","All Suppliers","Tous les fournisseurs","Todos los proveedores","全サプライヤー"],["直接 + 二级路径","Direct + Indirect Paths","Chemins directs et indirects","Rutas directas e indirectas","直接・間接経路"],["仅一级直接路径","One-hop Only","Un seul saut","Solo un salto","1ホップのみ"],["仅二级乘积路径","Two-hop Products Only","Produits à deux sauts","Solo productos de dos saltos","2ホップ積のみ"],["仅三级乘积路径","Three-hop Products Only","Produits à trois sauts","Solo productos de tres saltos","3ホップ積のみ"],["全部 M7 客户","All M7 Customers","Tous les clients M7","Todos los clientes M7","M7顧客すべて"],["起点供应商","Origin Supplier","Fournisseur d’origine","Proveedor de origen","起点サプライヤー"],["路径","Path","Chemin","Ruta","経路"],["目标七巨头","M7 Destination","Client M7 cible","Cliente M7 objetivo","M7到達先"],["跳数","Hops","Sauts","Saltos","ホップ数"],["证据路径权重","Evidence Path Weight","Poids du chemin documenté","Peso de la ruta documentada","根拠経路ウェイト"],["核验","Verification","Vérification","Verificación","検証"],["40家公司 · 网络可达性","40 Stocks · Network Reach","40 titres · Portée du réseau","40 acciones · Alcance de red","40銘柄・ネットワーク到達度"],["按已核验路径的累积代理强度排序，非业务收入规模排名","Ranked by documented path index, not revenue","Classement par indice de chemin, pas par chiffre d’affaires","Ordenado por índice de ruta, no por ingresos","根拠経路指数順であり売上高順位ではありません"],["股票","Ticker","Symbole","Símbolo","銘柄"],["行业环节","Supply Chain Segment","Segment de la chaîne","Segmento de suministro","産業セグメント"],["直接客户","Direct Customers","Clients directs","Clientes directos","直接顧客"],["二级客户","Indirect Customers","Clients indirects","Clientes indirectos","間接顧客"],["可核验路径数","Verified Paths","Chemins vérifiés","Rutas verificadas","確認済み経路数"],["关联代理指数","Linkage Proxy Index","Indice de liaison indirecte","Índice proxy de vínculo","連携代理指数"],["七巨头 × 上游供应商二部图","M7 × Upstream Suppliers Bipartite Graph","Graphe biparti M7 × fournisseurs","Grafo bipartito M7 × proveedores","M7×上流サプライヤー二部グラフ"],["只看有来源关系","Verified Links Only","Liens vérifiés uniquement","Solo vínculos verificados","証拠付きのみ"],["七巨头","Magnificent Seven","Magnificent Seven","Siete Magníficas","マグニフィセント・セブン"],["供应商","Suppliers","Fournisseurs","Proveedores","サプライヤー"],["已公开披露","Publicly Disclosed","Publiquement documenté","Divulgado públicamente","公開済み"],["待验证，不参与有效关系统计","Unverified · Excluded","Non vérifié · Exclu","Sin verificar · Excluido","未検証・集計対象外"],["关系证据明细","Relationship Evidence","Preuves des relations","Evidencia de relaciones","関係の証拠詳細"],["披露时点、收入份额、合同金额和证据来源严格分列","Separate dates, revenue shares, contract values and sources","Dates, parts du revenu, contrats et sources séparés","Fechas, cuotas de ingresos, contratos y fuentes por separado","公開日・売上割合・契約額・出典を分離"],["网络模型约束","Graph Model Constraints","Contraintes du graphe","Restricciones del grafo","ネットワークモデル制約"],["避免关系图推断中常见的数据污染","Avoid common graph data leakage","Éviter les fuites de données du graphe","Evitar filtración de datos del grafo","グラフのデータ漏洩を防ぐ"],["时间约束","Point-in-time Rule","Règle temporelle","Regla temporal","時点制約"],["数值约束","Value Rule","Règle numérique","Regla numérica","数値制約"],["层级约束","Tier Rule","Règle des niveaux","Regla de niveles","階層制約"],["缺失机制","Missing-data Rule","Gestion des données manquantes","Datos faltantes","欠損データの扱い"],["合作与合同事件库","Partnership & Contract Events","Événements contrats et partenariats","Eventos de contratos y alianzas","提携・契約イベント"],["全部事件","All Events","Tous les événements","Todos los eventos","全イベント"],["合同与供应","Contracts & Supply","Contrats et fourniture","Contratos y suministro","契約・供給"],["战略投资","Strategic Investment","Investissement stratégique","Inversión estratégica","戦略投資"],["财报披露","Financial Disclosures","Publications financières","Divulgaciones financieras","決算開示"],["政策观察台","Policy Monitor","Veille réglementaire","Monitor de políticas","政策モニター"],["能源 · 电力 · 储能：三维研究属性","Energy · Power · Storage: Research Dimensions","Énergie · Électricité · Stockage : dimensions","Energía · Electricidad · Almacenamiento: dimensiones","エネルギー・電力・蓄電：研究軸"],["分类 v1.0","Classification v1.0","Classification v1.0","Clasificación v1.0","分類 v1.0"],["全部属性","All Attributes","Tous les attributs","Todos los atributos","全属性"],["能源 · Energy","Energy","Énergie","Energía","エネルギー"],["电力 · Power","Electric Power","Électricité","Electricidad","電力"],["储能 · Storage","Energy Storage","Stockage d’énergie","Almacenamiento de energía","蓄電"],["全部 12 家供应商","All 40 Suppliers","40 fournisseurs","40 proveedores","全40社"],["只显示已核验产品关联","Verified Products Only","Produits vérifiés uniquement","Solo productos verificados","検証済み製品のみ"],["上市公司","Listed Company","Société cotée","Empresa cotizada","上場企業"],["研究维度","Research Dimension","Dimension de recherche","Dimensión de investigación","研究分野"],["供应链角色及产品","Role & Products","Rôle et produits","Función y productos","役割と製品"],["证据类型","Evidence Type","Type de preuve","Tipo de evidencia","証拠種別"],["资料来源","Source","Source","Fuente","情報源"],["模型独立性","Independent Factors","Facteurs indépendants","Factores independientes","独立した研究軸"],["数据质量与审计状态","Data Quality & Audit Status","Qualité et audit des données","Calidad y auditoría de datos","データ品質・監査状況"],["为量化回测和论文复现预留的核验面板","Research audit for reproducible backtests","Audit pour backtests reproductibles","Auditoría para backtests reproducibles","再現可能なバックテスト用監査"],["导入规范","Import Format","Format d’importation","Formato de importación","インポート仕様"],["页面不主动联网抓价格或新闻；数据需外部管道提供","Data comes from the external pipeline, not this webpage","Données issues du pipeline, pas de cette page","Datos del sistema externo, no de esta página","データは外部パイプラインから取得"],["工作流","Workflow","Flux de travail","Flujo de trabajo","ワークフロー"],["下载可填充模板","Download Template","Télécharger le modèle","Descargar plantilla","テンプレートを保存"],["下载示例 JSON","Download Sample JSON","Télécharger le JSON d’exemple","Descargar JSON de ejemplo","サンプルJSONを保存"],["恢复演示","Restore Sample","Restaurer l’exemple","Restaurar ejemplo","サンプルに戻す"],["已核实来源索引","Verified Sources","Sources vérifiées","Fuentes verificadas","確認済み出典"],["直接链接到 SEC、公司 IR/公告和美国政府发布源","Links to SEC filings, company IR and government releases","Liens SEC, IR d’entreprise et publications officielles","Enlaces a SEC, relaciones con inversores y fuentes oficiales","SEC・企業IR・米政府の一次資料"],["严格 Alpha + 探索评分分离 · 非投资建议","Full Alpha separated from exploratory scores · Not financial advice","Alpha complet distinct des scores exploratoires · Pas un conseil financier","Alfa completo separado del exploratorio · No es asesoramiento financiero","正式アルファと参考値を区別・投資助言ではありません"],["原始公告 ↗","Original Announcement ↗","Annonce originale ↗","Anuncio original ↗","原文発表 ↗"],["查看原始文件 ↗","View Source ↗","Voir la source ↗","Ver fuente ↗","原資料を見る ↗"],["官方资料 ↗","Official Source ↗","Source officielle ↗","Fuente oficial ↗","公式資料 ↗"],["查看原始产品资料 ↗","View Product Source ↗","Voir la source produit ↗","Ver fuente de producto ↗","製品原資料を見る ↗"],["查看政府文件 ↗","Government Document ↗","Document officiel ↗","Documento oficial ↗","政府文書 ↗"],["原始证据 ","Source Evidence ","Preuve originale ","Evidencia original ","原資料 "]];
 const lookup = new Map(values.map(row => [row[0], {en:row[1],'zh-CN':row[0],fr:row[2],es:row[3],ja:row[4]}]));
 const originalText = new WeakMap();
 const originalAttrs = new WeakMap();
 const ignore = new Set(['SCRIPT','STYLE','NOSCRIPT','CODE','PRE','TEXTAREA','OPTIONGROUP']);
 let current = 'en';
 function stored() {
   try { const v = new URLSearchParams(location.search).get('lang') || localStorage.getItem('m7-language'); return LOCALES.includes(v) ? v : 'en'; }
   catch (_) { return 'en'; }
 }
 const selector = document.getElementById('m7Language');
 current = stored();
 function exact(text, lang=current) {
   const row = lookup.get(text);
   return row ? (row[lang] || row.en || text) : null;
 }
 const patterns = [
   [/^数据截面：(.*)$/, a=>['Data snapshot: '+a,'Données au : '+a,'Datos al: '+a,'データ基準日：'+a]],
   [/^最新收盘价：(.*?)；前一交易日：(.*?)。正式报告必须使用已完成交易日、同一行情口径。$/, (a,b)=>['Latest close: '+a+'; prior session: '+b+'. Only completed sessions and consistent sources.','Dernière clôture : '+a+' ; séance précédente : '+b+'. Séances clôturées et sources cohérentes.','Último cierre: '+a+'; sesión anterior: '+b+'. Solo sesiones cerradas y fuentes coherentes.','直近終値：'+a+'、前取引日：'+b+'。確定終値・同一情報源を使用。']],
   [/^相较上次 ([+\-]?[0-9.]+)分$/, a=>['Change vs prior: '+a+' pts','Variation : '+a+' pts','Cambio: '+a+' pts','前回比：'+a+'ポイント']],
   [/^证据覆盖率：([0-9]+%)$/, a=>['Evidence coverage: '+a,'Couverture des preuves : '+a,'Cobertura de evidencia: '+a,'根拠網羅率：'+a]],
   [/^当前展示 ([0-9]+) 条记录；资料口径截至 (.*)。单条产品证据不是 M7 直接供应合同。$/, (a,b)=>['Showing '+a+' records; source cutoff '+b+'. Product evidence does not prove a direct M7 contract.','Affichage de '+a+' lignes ; date des sources '+b+'. Une fiche produit ne prouve pas de contrat direct avec M7.','Mostrando '+a+' registros; fecha de fuentes '+b+'. La evidencia de producto no demuestra contratos directos con M7.','表示：'+a+'件、資料基準：'+b+'。製品情報はM7直接契約の証明ではありません。']],
   [/^([0-9]+)家已核验$/, a=>[a+' verified',a+' vérifiés',a+' verificados',a+'社確認済み']],
   [/^([0-9]+)家正式 \/ ([0-9]+)家试算$/, (a,b)=>[a+' full / '+b+' exploratory',a+' complets / '+b+' exploratoires',a+' completos / '+b+' exploratorios',a+'正式／'+b+'参考']],
   [/^([0-9]+)家探索评分 †$/, a=>[a+' exploratory scores †',a+' scores exploratoires †',a+' puntuaciones exploratorias †',a+'参考スコア †']],
   [/^成功导入 ([0-9]+) 家供应商记录（请自行核验来源）$/, a=>['Imported '+a+' supplier records; verify sources','Importation de '+a+' fournisseurs ; vérifiez les sources','Importados '+a+' proveedores; verifique las fuentes',a+'社のデータを読み込みました。出典を確認してください']],
   [/^研究数据已自动更新至 (.*)$/,a=>['Research data updated: '+a,'Données actualisées : '+a,'Datos actualizados: '+a,'データ更新：'+a]],
   [/^数据更新时间 (.*?)；模型 (.*?)。$/, (a,b)=>['Data updated: '+a+'; model: '+b+'.','Mise à jour : '+a+' ; modèle : '+b+'.','Actualizado: '+a+'; modelo: '+b+'.','更新：'+a+'、モデル：'+b+'。']]
 ];
 function renderValue(source) {
   if(current==='zh-CN') return source;
   const start = source.match(/^\s*/)[0];
   const end = source.match(/\s*$/)[0];
   const core = source.slice(start.length, source.length-end.length);
   if(!core) return source;
   const matched = exact(core);
   if(matched !== null) return start+matched+end;
   for(const [re,fn] of patterns){
     const match=core.match(re);
     if(match) return start+fn(...match.slice(1))[['en','fr','es','ja'].indexOf(current)]+end;
   }
   // Long Chinese source disclosures are preserved verbatim rather than
   // being silently machine-translated or changing their factual meaning.
   return source;
 }
 function translateNode(node) {
   if(!node || !node.parentElement || ignore.has(node.parentElement.tagName))return;
   const latest=node.nodeValue;
   const old=originalText.get(node);
   const source=old && latest===old.last ? old.source : latest;
   const translated=renderValue(source);
   originalText.set(node,{source,last:translated});
   if(translated!==latest) node.nodeValue=translated;
 }
 function translateAttrs(element){
   if(!element || element.nodeType!==1)return;
   for(const attribute of ['placeholder','title','aria-label']){
     if(!element.hasAttribute(attribute))continue;
     const now=element.getAttribute(attribute);
     let old=originalAttrs.get(element)||{};
     const entry=old[attribute];
     const source=entry && entry.last===now ? entry.source : now;
     const value=renderValue(source);
     old[attribute]={source,last:value};originalAttrs.set(element,old);
     if(value!==now)element.setAttribute(attribute,value);
   }
 }
 function apply(){
   const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
   const nodes=[];let node;
   while((node=walker.nextNode()))nodes.push(node);
   for(const n of nodes)translateNode(n);
   for(const el of document.body.querySelectorAll('[placeholder],[title],[aria-label]')) translateAttrs(el);
   document.documentElement.lang=current;
   document.title = ({
      en:'M7 Supplier Alpha | Research Dashboard',
      'zh-CN':'M7供应链Alpha | 研究看板',
      fr:'M7 Supplier Alpha | Tableau de bord de recherche',
      es:'M7 Supplier Alpha | Panel de investigación',
      ja:'M7サプライヤーAlpha | 研究ダッシュボード'
   })[current];
 }
 let queued=false;
 function schedule(){
   if(queued)return;queued=true;
   requestAnimationFrame(()=>{queued=false;apply()});
 }
 function selectLanguage(locale){
   current=LOCALES.includes(locale)?locale:'en';
   if(selector)selector.value=current;
   try{localStorage.setItem('m7-language',current)}catch(_){}
   apply();
 }
 if(selector){
   selector.innerHTML=LOCALES.map(l=>'<option value="'+l+'">'+languageNames[l]+'</option>').join('');
   selector.value=current;
   selector.addEventListener('change',()=>selectLanguage(selector.value));
 }
 const observer=new MutationObserver(schedule);
 observer.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['placeholder','title','aria-label']});
 apply();
 window.M7_I18N={languages:LOCALES,get language(){return current},setLanguage:selectLanguage,translate:renderValue,strings:lookup.size};
})();
