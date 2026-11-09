/* Quantitative research dashboard. Sources, numbers and as-filed dates stay invariant. */
(()=>{
"use strict";
const host=document.getElementById("quantLab");
if(!host)return;
const locales={
en:{lab:"QUANTITATIVE RESEARCH / SYSTEMATIC INVESTING",title:"Investability & Strategy Lab",
subtitle:"40 equities · fundamental screening · execution-lagged diagnostic backtest · source audit",
screen:"INVESTABILITY SCREEN",screenNote:"Current cross-section: Alpha, revenue growth, valuation, size and volatility. Never backfilled into historical returns.",
return:"Strategy total return",cagr:"Annualized CAGR",sharpe:"Sharpe · rf = 0",drawdown:"Maximum drawdown",
benchmark:"BENCHMARK COMPARISON",equity:"Cumulative Growth of $1",draw:"Drawdown",perf:"PORTFOLIO PERFORMANCE",backtest:"Backtest Diagnostics",
rank:"Current Investability Ranking",rankNote:"Full score requires SEC fundamental evidence and ≥75% weighted coverage. Unranked securities remain visible.",
month:"MONTHLY RETURN ATTRIBUTION",trades:"MONTHLY REBALANCE LOG",method:"METHODOLOGY & MODEL RISK",
ticker:"Ticker",score:"Score",status:"Coverage",price:"Close $",cap:"Market cap proxy",revenue:"FY revenue",growth:"Revenue YoY",ps:"P/S proxy",supply:"Supply Alpha†",monitor:"Price monitor",source:"SEC source",
unranked:"Insufficient data",ranked:"Screened",noScore:"Not rankable; missing as-filed fundamentals and/or source coverage.",monthly:"Monthly Returns",positions:"Holdings",tradeDate:"Rebalance close",signalDate:"Signal close",turnover:"One-way turnover",cost:"Estimated cost",none:"No reliable backtest can be computed from this historical window.",
backtestOnly:"PRICE-ONLY DIAGNOSTIC",screenOnly:"CURRENT SCREEN ONLY",notTested:"FULL FUNDAMENTAL+ALPHA STRATEGY IS NOT HISTORICALLY BACKTESTED",
caveat:"Historical backtest uses only prior-close price signals. Current Alpha, today's M7 links, market cap and revenue are never backfilled. The current 40-stock list creates survivorship/selection bias; results are not out-of-sample investment validation.",
sourceWarning:"Market cap = latest close × SEC as-filed shares (indicative, not ADR/split adjusted). P/S and revenue growth are not comparable across all industries without accounting normalization.",
weight:"Screening weights",strategy:"Monthly top 8 · equal weight · max 3 per sector · 10 bps per side · next-session close fill",
coverage:"Fundamental revenue coverage",eligible:"Eligible screening scores",
fetch:"Fetching quant research snapshot…",refresh:"Refresh research snapshot",loading:"Research data not available yet. See the source audit or trigger the daily pipeline.",
trailing:"Backtest window",vol:"Annualized volatility",sortino:"Sortino · rf = 0",turn:"One-way turnover",tradeCost:"Total trading costs",info:"Information ratio vs QQQ",positive:"Positive sessions",days:"Trading sessions",
nav:"Portfolio NAV",priceOnly:"Price-only momentum, not supply Alpha",spy:"QQQ",xlk:"XLK",details:"Factor and source detail",size:"Indicative size (not definitive market cap)",
sourceData:"Financial statements are SEC CompanyFacts as filed; dates and missing records are preserved.",risk:"Critical limitations",statusLine:"Data status",preview:"Current signal ranking does not imply tested portfolio returns.",actions:"Research controls",hideUnranked:"Show ranked only",showAll:"Show all 40",noFact:"No sourced financial statements. Investment ranking remains N/A. Price-only strategy can still be tested.",
shares:"SEC shares as filed",period:"Latest FY period",total:"Total return",actual:"Actual historical prices",validation:"Research diagnostic · not audited live execution",na:"N/A"},
"zh-CN":{lab:"量化研究 / 系统化投资",title:"投资性评估与策略实验室",subtitle:"40家公司 · 基本面筛选 · 滞后执行的诊断回测 · 数据来源审计",
screen:"投资性评分筛选",screenNote:"当前截面综合Alpha、收入增长、估值、规模和波动率。不得将当前数据倒填历史。",
return:"策略累计收益",cagr:"年化复合收益率",sharpe:"夏普比率 · 无风险利率0",drawdown:"最大回撤",benchmark:"基准比较",equity:"单位净值增长",draw:"回撤",perf:"组合表现",backtest:"回测诊断",
rank:"当前投资性排名",rankNote:"完整投资评分要求SEC财报及至少75%加权覆盖率，缺失样本保留。",
month:"月度收益分析",trades:"月度调仓记录",method:"方法与模型风险",ticker:"股票",score:"评分",status:"覆盖率",price:"收盘价 $",cap:"市值代理",revenue:"年营收",growth:"营收同比",ps:"市销率代理",supply:"供应链Alpha†",monitor:"价格监控",source:"SEC来源",
unranked:"数据不足",ranked:"可评分",noScore:"无法评分：缺失点时基本面或可靠数据来源。",monthly:"月度收益",positions:"持仓",tradeDate:"调仓收盘日",signalDate:"信号收盘日",turnover:"单边换手",cost:"预估成本",none:"当前历史窗口不足以计算可靠回测。",
backtestOnly:"仅价格策略诊断",screenOnly:"当前截面评分",notTested:"完整供应链与基本面策略尚未经过正式历史验证",
caveat:"历史回测只使用当时可获得的价格信号，不将今天的供应链评分、关系、估值或财务数据填入过去。现有40股股票池存在幸存者偏差，历史成分股、股价复权及独立样本外检验尚未完成，所示收益仅供研究。",
sourceWarning:"市值＝最近收盘价×SEC申报股数，仅为代理值，未验证ADR与拆股。跨行业市销率、营收增速需谨慎比较。",
weight:"筛选权重",strategy:"月度前8名 · 等权 · 每行业最多3家 · 单边10基点 · 次交易日收盘成交",
coverage:"年营收数据覆盖",eligible:"符合投资评分条件",fetch:"正在读取量化研究快照…",refresh:"刷新研究数据",loading:"尚未生成量化结果。查看数据审计或触发每日更新。",
trailing:"回测时间段",vol:"年化波动率",sortino:"索提诺比率 · 无风险利率0",turn:"单边换手率",tradeCost:"交易总成本",info:"相对QQQ信息比率",positive:"正收益交易日",days:"交易日数",
nav:"组合净值",priceOnly:"仅价格动量，并非供应链Alpha",spy:"QQQ",xlk:"XLK",details:"因子及来源详情",size:"参考规模（非确认市值）",sourceData:"财报来自SEC按申报时点的CompanyFacts，保留缺失与日期。",risk:"重要局限",statusLine:"数据状态",preview:"当前投资评分不等于历史策略收益。",actions:"研究操作",hideUnranked:"仅显示可评分",showAll:"显示全部40家",noFact:"未获取可靠财务数据，投资性评分保持N/A；价格策略仍可单独回测。",shares:"SEC申报股数",period:"最新财年",total:"累计收益",actual:"真实历史行情",validation:"研究诊断，非经审计的实盘成交",na:"N/A"},
fr:{lab:"RECHERCHE QUANTITATIVE / INVESTISSEMENT SYSTÉMATIQUE",title:"Investissabilité et laboratoire de stratégie",subtitle:"40 actions · données financières · exécution différée · audit des sources",screen:"SCORE D'INVESTISSABILITÉ",screenNote:"Coupe actuelle : Alpha, croissance, valorisation, taille et risque. Sans rétroprojection historique.",return:"Performance cumulée",cagr:"CAGR annualisé",sharpe:"Sharpe · taux sans risque 0",drawdown:"Perte maximale",benchmark:"COMPARAISON AUX INDICES",equity:"Croissance d'une unité",draw:"Repli",perf:"PERFORMANCE DU PORTEFEUILLE",backtest:"Diagnostic de backtest",rank:"Classement actuel d'investissabilité",rankNote:"Données SEC et couverture pondérée ≥75 % requises. Les titres incomplets restent visibles.",month:"RENDEMENTS MENSUELS",trades:"JOURNAL DES RÉÉQUILIBRAGES",method:"MÉTHODOLOGIE ET RISQUES",ticker:"Titre",score:"Score",status:"Couverture",price:"Clôture $",cap:"Capitalisation estimée",revenue:"CA annuel",growth:"Croissance CA",ps:"P/S indicatif",supply:"Alpha fournisseur†",monitor:"Suivi des cours",source:"Source SEC",unranked:"Données insuffisantes",ranked:"Noté",noScore:"Score non disponible : données financières temporelles insuffisantes.",monthly:"Rendements mensuels",positions:"Positions",tradeDate:"Clôture de rééquilibrage",signalDate:"Date du signal",turnover:"Rotation unilatérale",cost:"Coût estimé",none:"Historique insuffisant pour produire un backtest fiable.",backtestOnly:"DIAGNOSTIC PRIX UNIQUEMENT",screenOnly:"COUPE ACTUELLE",notTested:"STRATÉGIE ALPHA + FONDAMENTAUX NON BACKTESTÉE HISTORIQUEMENT",caveat:"Le backtest utilise uniquement les prix connus à la veille. Aucun Alpha, réseau de fournisseurs ou donnée financière actuelle n'est rétroprojeté. Biais de survie du groupe de 40 titres.",sourceWarning:"Capitalisation indicative = cours × actions SEC, sans validation des ADR/splits. Les comparaisons intersectorielles de P/S sont limitées.",weight:"Pondérations du score",strategy:"Mensuel : 8 premiers · poids égaux · 3/secteur · 10 pb/sens · clôture séance suivante",coverage:"Couverture revenus",eligible:"Scores éligibles",fetch:"Chargement de la recherche quantitative…",refresh:"Actualiser",loading:"Données quantitatives indisponibles. Vérifiez la collecte automatique.",trailing:"Période testée",vol:"Volatilité annuelle",sortino:"Sortino · taux 0",turn:"Rotation",tradeCost:"Coûts de transaction",info:"Ratio d'information vs QQQ",positive:"Séances positives",days:"Séances",nav:"Valeur du portefeuille",priceOnly:"Momentum des prix, pas Alpha",spy:"QQQ",xlk:"XLK",details:"Facteurs et sources",size:"Taille indicative",sourceData:"Données financières SEC datées au dépôt.",risk:"Limites critiques",statusLine:"État des données",preview:"Le score actuel n'est pas un rendement backtesté.",actions:"Contrôles",hideUnranked:"Titres notés seulement",showAll:"Les 40 titres",noFact:"Sans données financières vérifiées, le classement reste N/A. Le backtest des prix est séparé.",shares:"Actions déposées SEC",period:"Exercice",total:"Rendement total",actual:"Cours historiques",validation:"Diagnostic, pas exécution réelle",na:"N/A"},
es:{lab:"INVESTIGACIÓN CUANTITATIVA / INVERSIÓN SISTEMÁTICA",title:"Inversión y laboratorio de estrategias",subtitle:"40 acciones · fundamentales · ejecución diferida · auditoría de fuentes",screen:"PUNTUACIÓN DE INVERSIÓN",screenNote:"Corte actual: Alfa, crecimiento, valoración, tamaño y riesgo. No se traslada al pasado.",return:"Rentabilidad acumulada",cagr:"CAGR anualizado",sharpe:"Sharpe · tasa libre de riesgo 0",drawdown:"Caída máxima",benchmark:"COMPARACIÓN DE ÍNDICES",equity:"Crecimiento de una unidad",draw:"Caída",perf:"RENDIMIENTO DE CARTERA",backtest:"Diagnóstico de backtest",rank:"Clasificación actual de inversión",rankNote:"Requiere datos SEC y cobertura ponderada ≥75 %. Se muestran valores faltantes.",month:"RETORNOS MENSUALES",trades:"REGISTRO DE REBALANCEOS",method:"METODOLOGÍA Y RIESGOS",ticker:"Símbolo",score:"Puntuación",status:"Cobertura",price:"Cierre $",cap:"Capitalización estimada",revenue:"Ingresos anuales",growth:"Crecimiento ingresos",ps:"P/S aproximado",supply:"Alfa de proveedor†",monitor:"Monitor de precios",source:"Fuente SEC",unranked:"Datos insuficientes",ranked:"Calculado",noScore:"No calculable: faltan datos fundamentales con fecha.",monthly:"Retornos mensuales",positions:"Posiciones",tradeDate:"Cierre del rebalanceo",signalDate:"Fecha de señal",turnover:"Rotación unilateral",cost:"Costo estimado",none:"Historial insuficiente para backtest fiable.",backtestOnly:"DIAGNÓSTICO SOLO PRECIOS",screenOnly:"CORTE ACTUAL",notTested:"LA ESTRATEGIA ALFA + FUNDAMENTALES NO ESTÁ BACKTESTEADA",caveat:"El backtest usa solo precios conocidos previamente. No retroproyecta el Alfa actual, vínculos ni fundamentales. La selección de 40 activos contiene sesgo de supervivencia.",sourceWarning:"Capitalización estimada = cierre × acciones SEC, sin validar ADR o splits. P/S entre sectores no es plenamente comparable.",weight:"Pesos de factores",strategy:"Mensual: 8 mejores · igual peso · 3/sector · 10 pb/lado · cierre siguiente",coverage:"Cobertura de ingresos",eligible:"Puntuaciones válidas",fetch:"Cargando datos cuantitativos…",refresh:"Actualizar",loading:"Datos cuantitativos no disponibles. Revise la actualización automática.",trailing:"Periodo de backtest",vol:"Volatilidad anual",sortino:"Sortino · tasa 0",turn:"Rotación",tradeCost:"Costos de transacción",info:"Ratio de información vs QQQ",positive:"Días positivos",days:"Sesiones",nav:"Valor del portafolio",priceOnly:"Momentum de precios, no Alfa",spy:"QQQ",xlk:"XLK",details:"Factores y fuentes",size:"Tamaño indicativo",sourceData:"Datos SEC según fecha de presentación.",risk:"Limitaciones importantes",statusLine:"Estado de datos",preview:"La puntuación actual no implica rendimiento histórico.",actions:"Controles",hideUnranked:"Solo puntuados",showAll:"Las 40 acciones",noFact:"Sin estados financieros verificados la clasificación es N/A; el backtest de precios es independiente.",shares:"Acciones declaradas SEC",period:"Ejercicio",total:"Retorno total",actual:"Precios históricos",validation:"Diagnóstico, no ejecución real",na:"N/A"},
ja:{lab:"クオンツ研究・システマティック投資",title:"投資適格性と戦略ラボ",subtitle:"40銘柄・財務データ・翌日終値での取引診断・出典監査",screen:"投資適格性スコア",screenNote:"現時点のAlpha、売上成長、割安度、規模、リスク。過去に遡って適用しません。",return:"累積リターン",cagr:"年率CAGR",sharpe:"シャープ比率・無リスク金利0",drawdown:"最大ドローダウン",benchmark:"ベンチマーク比較",equity:"1単位の資産推移",draw:"ドローダウン",perf:"ポートフォリオ実績",backtest:"バックテスト診断",rank:"現在の投資適格性ランキング",rankNote:"SEC財務データと75%以上の加重カバレッジが必要。未評価銘柄も表示。",month:"月次リターン",trades:"月次リバランス履歴",method:"手法とモデルリスク",ticker:"銘柄",score:"スコア",status:"網羅率",price:"終値 $",cap:"時価総額の参考値",revenue:"年間売上高",growth:"売上成長率",ps:"参考P/S",supply:"供給網Alpha†",monitor:"株価モニター",source:"SEC出典",unranked:"データ不足",ranked:"評価可能",noScore:"財務情報や日時情報が不足し採点できません。",monthly:"月次リターン",positions:"保有銘柄",tradeDate:"リバランス終値日",signalDate:"シグナル日",turnover:"片道回転率",cost:"推定コスト",none:"信頼できるバックテストを行う履歴が不足。",backtestOnly:"株価のみの診断",screenOnly:"現時点の断面評価",notTested:"Alpha＋財務情報の複合戦略は歴史的に検証されていません",caveat:"過去のバックテストには前日に判明した株価のみ使用。現在のAlpha、供給関係、時価総額、売上を過去に持ち込んでいません。現行40銘柄には生存者バイアスがあります。",sourceWarning:"参考時価総額＝終値×SEC申告株式数。ADR・株式分割の調整は未検証。業種間のP/S比較には注意。",weight:"評価ウェイト",strategy:"月次上位8銘柄・等ウェイト・業種上限3・片道10bp・翌取引日終値",coverage:"売上データ網羅率",eligible:"評価可能な銘柄",fetch:"クオンツ研究データを読み込み中…",refresh:"更新",loading:"量的分析データがありません。定期収集の状態をご確認ください。",trailing:"検証期間",vol:"年率ボラティリティ",sortino:"ソルティノ・無リスク金利0",turn:"回転率",tradeCost:"取引費用",info:"対QQQ情報比率",positive:"プラスの日",days:"取引日数",nav:"資産曲線",priceOnly:"株価モメンタムのみ。供給網Alphaではありません。",spy:"QQQ",xlk:"XLK",details:"因子と出典",size:"規模の参考値",sourceData:"SEC申告時点に基づく財務データです。",risk:"重要な限界",statusLine:"データ状態",preview:"現時点のスコアは過去のリターンを保証しません。",actions:"操作",hideUnranked:"評価可能のみ",showAll:"全40銘柄",noFact:"検証済み財務情報がなければ採点はN/A。価格のみのバックテストは別表示。",shares:"SEC申告株数",period:"会計年度",total:"累積リターン",actual:"過去の実際の価格",validation:"研究診断であり実際の約定ではありません",na:"N/A"}
};

const labExtras={
en:{scenario:"Backtest scenario",paper:"Forward Paper Portfolio — Current Investability Signal",paperNote:"New research allocations only. First execution is the next completed close, so there are no fabricated prior returns.",noPaper:"Insufficient SEC+Alpha coverage for a forward paper signal.",sensitivity:"Sensitivity: position count and transaction costs",impact:"Scenario total return",forward:"First eligible execution",notFilled:"NOT FILLED",target:"Target allocation",rankWarning:"Returns below are historical PRICE-ONLY, not returns of the forward Alpha+fundamental basket."},
"zh-CN":{scenario:"回测情景",paper:"前瞻模拟组合：当前投资性信号",paperNote:"仅生成研究目标持仓。首次可执行价为后续完成交易日的收盘价，历史收益不作虚构。",noPaper:"财务和Alpha覆盖不足，无法生成前瞻组合。",sensitivity:"稳健性：持仓数量与交易成本",impact:"情景累计收益",forward:"最早可执行时点",notFilled:"尚未成交",target:"目标权重",rankWarning:"下方历史回测仅使用价格信号，不代表前瞻Alpha＋基本面组合的历史收益。"},
fr:{scenario:"Scénario de backtest",paper:"Portefeuille prospectif — signal d'investissabilité",paperNote:"Allocation indicative uniquement ; aucun rendement passé ni exécution réelle ne sont inventés.",noPaper:"Couverture financière insuffisante pour générer un portefeuille prospectif.",sensitivity:"Sensibilité : positions et coûts",impact:"Rendement par scénario",forward:"Première exécution possible",notFilled:"NON EXÉCUTÉ",target:"Poids cible",rankWarning:"Le backtest historique utilise seulement les prix, pas le portefeuille Alpha + fondamentaux."},
es:{scenario:"Escenario de backtest",paper:"Cartera prospectiva — señal de inversión",paperNote:"Asignación solo de investigación; no implica operaciones ejecutadas ni retornos pasados.",noPaper:"Datos fundamentales insuficientes para una cartera prospectiva.",sensitivity:"Sensibilidad: posiciones y costos",impact:"Retorno del escenario",forward:"Primera ejecución posible",notFilled:"SIN EJECUTAR",target:"Peso objetivo",rankWarning:"El backtest histórico usa solo precios, no la cartera Alfa + fundamentales."},
ja:{scenario:"バックテスト設定",paper:"前向きペーパーポートフォリオ・現在の投資適格性シグナル",paperNote:"研究用の目標保有のみ。過去の収益や実際の取引は生成しません。",noPaper:"財務データが不足して前向きのポートフォリオを生成できません。",sensitivity:"感応度：保有数・コスト",impact:"シナリオ累積リターン",forward:"最初の想定約定時点",notFilled:"未約定",target:"目標ウェイト",rankWarning:"下記の過去検証は価格のみ。現在のAlphaと財務を含む組合せではありません。"}
};
for(const [lang,labels] of Object.entries(labExtras))Object.assign(locales[lang],labels);

const factorKeys=["supply_alpha","monitor","growth","value","size","risk"];
const factorTexts={
en:["Supply Alpha†","Price monitor","Revenue growth","Cheap P/S","Size","Low volatility"],
"zh-CN":["供应链Alpha†","价格动量监控","营收增长","低市销率","公司规模","低波动"],
fr:["Alpha fournisseur†","Suivi des prix","Croissance revenus","Valorisation P/S","Taille","Faible volatilité"],
es:["Alfa de proveedor†","Monitor de precios","Crecimiento ingresos","P/S bajo","Tamaño","Baja volatilidad"],
ja:["供給網Alpha†","株価モニター","売上成長","低P/S","規模","低ボラティリティ"]
};
let selectedQuantTicker=null;
function factorDetail(row){
 const d=document.getElementById("qFactorDetail");
 if(!d)return;
 if(!row){d.innerHTML='<div class="q-empty">'+esc(t("noScore"))+'</div>';return;}
 const columns=factorKeys.map((k,i)=>{
  const value=row.component_scores?.[k],weight=row.weights?.[k]??0;
  const label=factorTexts[L()]?.[i]||factorTexts.en[i];
  return '<div class="q-metric" style="display:block"><div class="q-group" style="justify-content:space-between"><span>'+esc(label)+' · '+Math.round(weight*100)+'%</span><strong>'+fmt(value)+'</strong></div>'
      +'<div style="margin:5px 0 0;height:7px;border-radius:3px;background:#233449;overflow:hidden"><div style="height:100%;background:#72dccc;width:'+(value==null?0:Math.min(100,Math.max(0,value)))+'%"></div></div></div>';
 }).join("");
 d.innerHTML='<div class="q-insight"><strong>'+esc(row.ticker)+' · '+(row.investability_score==null?"N/A":fmt(row.investability_score)+'/100')+'</strong>'
  +'<div class="q-muted">'+esc(row.rank_eligible?t("audit_statusCurrent"):t("audit_statusInsufficient"))+' · '+pc(row.factor_coverage,0)+'</div></div>'
  +'<div style="margin-top:8px">'+columns+'</div>'
  +'<div class="q-metric"><span>'+esc(t("scenario_fyEnd"))+'</span><span>'+esc(row.revenue_fy_end||"N/A")+'</span></div>'
  +'<div class="q-metric"><span>'+esc(t("scenario_filed"))+'</span><span>'+esc(row.revenue_filed||"N/A")+'</span></div>'
  +'<div class="q-metric"><span>'+esc(t("source"))+'</span><span>'+link(row.fundamental_source,"SEC ↗")+'</span></div>'
  +'<div class="q-note">'+esc(t("sourceWarning"))+'</div>';
}

const vixLabels={
en:{vixTrigger:"VIX contrarian exposure trigger",vixClose:"Latest VIX close",vixTarget:"Next target stock weight",vixBands:"Exposure bands",vixCompare:"Matched window: VIX trigger vs baseline",vixNoData:"VIX data unavailable: no fabricated VIX backtest",vixCaution:"High VIX adds equity risk during stress and can increase drawdown. Previous close only; cash earns 0%; not validated out of sample.",vixHold:"Hold cash",vixSignal:"Signal / exposure",vixBase:"Original strategy",vixMode:"Selected portfolio",vixVReturn:"VIX total return",vixVDrawdown:"VIX max drawdown",vixBReturn:"Base total return",vixBDrawdown:"Base max drawdown"},
"zh-CN":{vixTrigger:"VIX 逆向仓位触发器",vixClose:"最近 VIX 收盘值",vixTarget:"下一交易日目标股票仓位",vixBands:"仓位分档",vixCompare:"相同窗口：VIX 版本 vs 原策略",vixNoData:"VIX 历史数据不足，不能虚构回测结果",vixCaution:"VIX 高位加仓也可能在下跌继续时放大回撤；仅用前一交易日收盘信号，现金利息按 0% 计算，尚未做样本外验证。",vixHold:"现金仓位",vixSignal:"信号 / 股票仓位",vixBase:"原始策略",vixMode:"所选组合",vixVReturn:"VIX 策略累计收益",vixVDrawdown:"VIX 策略最大回撤",vixBReturn:"原策略累计收益",vixBDrawdown:"原策略最大回撤"},
fr:{vixTrigger:"Déclencheur contrariant VIX",vixClose:"Dernière clôture VIX",vixTarget:"Prochaine exposition actions cible",vixBands:"Paliers d'exposition",vixCompare:"Même fenêtre : VIX vs base",vixNoData:"Historique VIX insuffisant",vixCaution:"Augmenter l'exposition lorsque le VIX monte peut accroître les pertes. Signal clôture précédente, liquidités à 0 %, hors échantillon non validé.",vixHold:"Liquidités",vixSignal:"Signal / exposition",vixBase:"Stratégie de base",vixMode:"Portefeuille choisi",vixVReturn:"Performance VIX",vixVDrawdown:"Repli VIX",vixBReturn:"Performance de base",vixBDrawdown:"Repli de base"},
es:{vixTrigger:"Activador contrarian VIX",vixClose:"Último cierre VIX",vixTarget:"Próxima exposición objetivo",vixBands:"Tramos de exposición",vixCompare:"Mismo período: VIX vs base",vixNoData:"Sin historial VIX suficiente",vixCaution:"Comprar más con VIX alto puede aumentar las pérdidas. Señal al cierre anterior, efectivo al 0 %, sin validación fuera de muestra.",vixHold:"Efectivo",vixSignal:"Señal / exposición",vixBase:"Estrategia base",vixMode:"Cartera seleccionada",vixVReturn:"Retorno VIX",vixVDrawdown:"Caída VIX",vixBReturn:"Retorno base",vixBDrawdown:"Caída base"},
ja:{vixTrigger:"VIX逆張りポジション・トリガー",vixClose:"直近VIX終値",vixTarget:"次回の目標株式比率",vixBands:"保有比率の段階",vixCompare:"同期間のVIX戦略と通常戦略",vixNoData:"VIX履歴不足のため結果なし",vixCaution:"VIX上昇時の買い増しは下落リスクも高めます。前日終値で判断、現金利回り0%、サンプル外未検証。",vixHold:"現金",vixSignal:"シグナル / 株式比率",vixBase:"従来戦略",vixMode:"選択した戦略",vixVReturn:"VIX累積収益",vixVDrawdown:"VIX最大下落",vixBReturn:"通常累積収益",vixBDrawdown:"通常最大下落"}
};
for(const [lang,labels] of Object.entries(vixLabels))Object.assign(locales[lang],labels);
for(const [lang,label] of Object.entries({en:"VIX / stock exposure","zh-CN":"VIX / 股票仓位",fr:"VIX / exposition",es:"VIX / exposición",ja:"VIX / 株式比率"}))locales[lang].vixSignal=label;

const keysAutonomous=["title","subtitle","mode","equity","cash","pnl","fees","pending","positions","audit","empty","notice","phase1","phase2","phase3","phase4","phase5"];
const autonomousLabels={"en":["Autonomous Trading · Paper Portfolio","Scheduled signal → risk checks → next-close simulated fill","PAPER ONLY · LIVE DISABLED","Account equity","Cash","Paper P/L","Simulated fees","Next-session target allocation","Paper positions","Decision / fill audit","No paper ledger yet. First run proposes orders; a later close can fill them.","This is simulated. No broker connected, no real funds, no live orders.","Market data","VIX & ranking","Risk gate","Paper fill","Audit"],"zh-CN":["自主交易 · 模拟账户","定时信号 → 风控检查 → 下一收盘模拟成交","仅模拟交易 · 实盘禁用","模拟净值","现金","模拟盈亏","模拟手续费","下一交易日目标仓位","模拟持仓","决策 / 成交日志","暂无模拟账本；首次运行生成计划，之后的交易日才能成交。","此模块不连接券商、不使用真实资金，也不会下实盘订单。","市场数据","VIX 与选股","风险检查","模拟成交","审计"],"fr":["Trading autonome · Simulation","Signal → risques → simulation au prochain cours","SIMULATION · RÉEL DÉSACTIVÉ","Capital simulé","Liquidités","Résultat","Frais","Allocation prévue","Positions","Journal d'audit","Aucun compte simulé pour le moment","Aucun courtier ni ordre réel.","Marché","VIX","Risques","Simulation","Audit"],"es":["Trading autónomo · Simulación","Señal → riesgo → simulación a cierre siguiente","SIMULACIÓN · REAL DESACTIVADO","Capital simulado","Efectivo","Beneficio","Comisiones","Asignación prevista","Posiciones","Registro de auditoría","Todavía no hay cartera simulada","Sin bróker ni órdenes reales.","Mercado","VIX","Riesgo","Simulación","Auditoría"],"ja":["自動売買 · 仮想口座","シグナル → リスク確認 → 翌終値で仮想約定","仮想売買のみ · 実売買不可","口座残高","現金","損益","手数料","次回の目標保有比率","仮想保有","監査記録","仮想口座データはまだありません","証券会社未接続、実際の注文なし。","市場","VIX","リスク","仮想約定","監査"]};
for(const [lang,labels] of Object.entries(autonomousLabels))keysAutonomous.forEach((k,i)=>{locales[lang]['autonomous_'+k]=labels[i]});
const autoQualityTranslations={"en":["40-Stock Participation & Data Quality","Observed weighted factor coverage","Estimated factor weight","Provisional score","Factor estimation","All names are scored, but estimates are not verified SEC facts. Missing actual prices stop paper fills.","All 40 candidates"],"zh-CN":["40 股参与情况与数据质量","真实因子加权覆盖率","估计因子权重","暂定评分","缺失值估计","40 只股票均获得研究评分，但估计值不等于真实财报；缺失真实价格将停止模拟成交。","全部 40 个候选"],"fr":["Univers de 40 actions et qualité","Couverture observée","Facteurs estimés","Score provisoire","Estimation","Les prix manquants bloquent l'exécution simulée.","40 valeurs"],"es":["Universo de 40 acciones y calidad","Cobertura observada","Factores estimados","Puntuación provisional","Estimación","Los precios ausentes bloquean las operaciones simuladas.","40 valores"],"ja":["40銘柄とデータ品質","観測済み比率","推定比率","暫定スコア","推定","実際の価格が欠ける場合、仮想約定を停止します。","40銘柄"]};
for(const [lang,values] of Object.entries(autoQualityTranslations))values.forEach((v,i)=>locales[lang]["auto_quality_"+["universe","observed","estimated","score","estimation","warning","all"][i]]=v);
const fortyHistoricalLabels={"en":["40-stock Sharpe vs QQQ","Historical equal-weight price-only diagnostic. Forward factor estimates are not backfilled.","Window","40 + VIX","40, no VIX","QQQ","VIX max drawdown","Min stocks","Not yet computed"],"zh-CN":["40 股 Sharpe 对比 QQQ","历史等权价格策略诊断：不倒填当前估计的财务因子，也不代表模拟账户的实际历史收益。","期限","40 股 + VIX","40 股无 VIX","QQQ","VIX 最大回撤","最低参与数","尚未完成计算"],"fr":["Sharpe de 40 actions vs QQQ","Backtest historique équipondéré basé sur les prix.","Période","40 + VIX","40 sans VIX","QQQ","Perte max. VIX","Titres min.","Non calculé"],"es":["Sharpe de 40 acciones vs QQQ","Estudio histórico equiponderado basado en precios.","Período","40 + VIX","40 sin VIX","QQQ","Caída máxima VIX","Acciones mín.","No calculado"],"ja":["40銘柄のシャープ比率 vs QQQ","現在の推定財務因子を過去へ遡及しない株価のみの比較です。","期間","40 + VIX","40 VIXなし","QQQ","VIX最大下落","最低銘柄数","未計算"]};
const fortyHistoricalKeys=["title","note","period","vix","plain","qqq","drawdown","eligible","none"];
for(const [lang,values] of Object.entries(fortyHistoricalLabels))values.forEach((v,i)=>{locales[lang]["forty_"+fortyHistoricalKeys[i]]=v;});
const weightedLabels={"en":["40 Weighted + VIX","40 Weighted, no VIX","40 Equal + VIX","Weighted + VIX total return","Weighted + VIX max drawdown","Weighted price-only proxy (NOT the historical forward fundamental/Alpha score). Monthly price factors use prior closes; same capped allocation shape as autonomous paper; no lookahead.","Forward paper Sharpe","Observed paper sessions","30 returns required","No historical performance assumed from new live plan"],"zh-CN":["40 股评分加权 + VIX","40 股评分加权无 VIX","40 股等权 + VIX","加权 + VIX 累计收益","加权 + VIX 最大回撤","历史加权仅基于当时已知的价格因子（非当前真实基本面／供应链 Alpha 的历史回测）。采用与自主模拟账户相同的权重计算与风控上限，无未来信息倒填。","前瞻模拟 Sharpe","前瞻交易日观测数","至少需 30 个收益日","新账户的历史业绩尚未形成"],"fr":["40 pondérées + VIX","40 pondérées sans VIX","40 égales + VIX","Rendement pondéré VIX","Repli pondéré VIX","Proxy historique fondé seulement sur les prix passés, pas sur les facteurs fondamentaux actuels.","Sharpe futur simulé","Sessions papier","30 rendements requis","Pas de rendements fictifs"],"es":["40 ponderadas + VIX","40 ponderadas sin VIX","40 iguales + VIX","Retorno ponderado VIX","Caída ponderada VIX","Proxy histórico solo con precios pasados, sin datos fundamentales actuales.","Sharpe simulado futuro","Sesiones observadas","Requiere 30 retornos","Sin retornos inventados"],"ja":["40銘柄加重+VIX","40銘柄加重・VIXなし","40銘柄均等+VIX","加重+VIXリターン","加重+VIX最大下落","当時の株価要因のみを使う歴史的比較。現在の財務・サプライチェーン因子は利用しません。","先行仮想シャープ","観測済み日数","30リターン必要","仮想の過去実績なし"]};
const weightedKeys=["wvix","wplain","evix","wreturn","wdraw","wnote","papersharpe","papersessions","paperthreshold","paperwarning"];
for(const [lang,items] of Object.entries(weightedLabels))items.forEach((v,i)=>{locales[lang]["weighted_"+weightedKeys[i]]=v;});
const auditUiLabels={"en":{"syncOk":"Synced with Overview","syncPending":"Snapshot mismatch: Supply Alpha hidden until Overview and Quant share an identical dated source","source":"Supplier model","archived":"Archived 8-stock research screen — not an active paper portfolio","active":"Active: 40-stock investability-weighted VIX paper account (next-close execution only)","high":"≥75% comparable coverage","mid":"50–74% exploratory coverage","low":"<50% limited evidence","all":"All coverage groups","rankCaution":"Ranks are comparable only within similar evidence coverage and factor sets. Missing fundamentals are not zero.","statusComputed":"Calculated historical price diagnostic","statusPending":"Waiting for new sample","statusNotAvailable":"Insufficient historical data","statusCurrent":"Current screening only","statusInsufficient":"Incomplete source coverage","statusPaper":"Awaiting next completed close","sourceDate":"Source date","backend":"Data source"},"zh-CN":{"syncOk":"与总览数据版本一致","syncPending":"数据版本不一致：在总览与量化页的来源快照同步前暂不显示 Supply Alpha","source":"供应链评分模型","archived":"历史 8 股研究篮子已归档，不是当前模拟交易组合","active":"当前有效策略：40 股投资性加权 + VIX 模拟账户（下一收盘日模拟执行）","high":"≥75% 高覆盖","mid":"50–74% 中覆盖探索","low":"<50% 低覆盖仅供参考","all":"所有覆盖分组","rankCaution":"仅建议比较覆盖率和缺失因子结构相近的股票；缺失基本面不等于零。","statusComputed":"已计算的历史价格诊断","statusPending":"尚无足够前瞻交易日","statusNotAvailable":"历史数据不足","statusCurrent":"当前截面评分","statusInsufficient":"数据覆盖不足","statusPaper":"等待下一完整交易日收盘","sourceDate":"来源日期","backend":"数据来源"},"fr":{"syncOk":"Synchronisé avec la vue d’ensemble","syncPending":"Source divergente : Alpha masqué jusqu'à synchronisation","source":"Modèle fournisseur","archived":"Ancien portefeuille de recherche à 8 titres archivé — pas de trading simulé actif","active":"Compte actif : 40 actions pondérées + VIX (simulation)","high":"Couverture ≥75%","mid":"Couverture 50–74%","low":"Couverture <50%","all":"Toutes les couvertures","rankCaution":"Comparer uniquement des titres à couverture et facteurs similaires.","statusComputed":"Diagnostic historique calculé","statusPending":"En attente de données","statusNotAvailable":"Historique insuffisant","statusCurrent":"Sélection actuelle","statusInsufficient":"Couverture insuffisante","statusPaper":"Prochaine clôture simulée","sourceDate":"Date de source","backend":"Source"},"es":{"syncOk":"Sincronizado con Resumen","syncPending":"Fuentes diferentes: Alpha oculto hasta sincronizar","source":"Modelo de proveedores","archived":"Antigua cartera de 8 valores archivada; no es simulación activa","active":"Activa: 40 acciones ponderadas + VIX (simulación)","high":"Cobertura ≥75%","mid":"Cobertura 50–74%","low":"Cobertura <50%","all":"Todas","rankCaution":"Comparar solo grupos con cobertura y factores equivalentes.","statusComputed":"Diagnóstico histórico calculado","statusPending":"Faltan datos","statusNotAvailable":"Historial insuficiente","statusCurrent":"Evaluación actual","statusInsufficient":"Cobertura insuficiente","statusPaper":"Esperando próximo cierre","sourceDate":"Fecha","backend":"Fuente"},"ja":{"syncOk":"概要と同一データ","syncPending":"データ不一致：同期まで Alpha を非表示","source":"供給モデル","archived":"旧8銘柄研究バスケットはアーカイブ済み（仮想取引対象外）","active":"有効な40銘柄加重＋VIX仮想口座","high":"75%以上","mid":"50–74%","low":"50%未満","all":"すべて","rankCaution":"欠損因子とカバレッジが同程度の銘柄のみ比較してください。","statusComputed":"計算済み価格診断","statusPending":"観測不足","statusNotAvailable":"履歴不足","statusCurrent":"現在のスクリーニング","statusInsufficient":"データ不足","statusPaper":"翌終値を待機","sourceDate":"データ日","backend":"データ出典"}};
for(const [lang,fields] of Object.entries(auditUiLabels))Object.assign(locales[lang],Object.fromEntries(Object.entries(fields).map(([k,v])=>["audit_"+k,v])));
let selectedScenario="1Y · VIX Trigger · Top 8 · 10 bps";
let paperState=null,data=null,showOnly=false,quantCoverageFilter="high",chartMode="nav",seriesActive={strategy:true,spy:true,xlk:true};
function L(){return (window.M7_I18N&&window.M7_I18N.language)||"en";}
function t(k){return (locales[L()]||locales.en)[k]||locales.en[k]||k;}
function esc(v){return String(v==null?"":v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function fmt(v,d=2){return typeof v==="number"&&Number.isFinite(v)?v.toLocaleString(L(),{minimumFractionDigits:d,maximumFractionDigits:d}):"N/A";}
function pc(v,d=1){return typeof v==="number"&&Number.isFinite(v)?(v*100).toLocaleString(L(),{minimumFractionDigits:d,maximumFractionDigits:d})+"%":"N/A";}
function compact(v){if(v===null||v===undefined||!Number.isFinite(v))return "N/A";const n=Math.abs(v);return (v/(n>=1e12?1e12:n>=1e9?1e9:n>=1e6?1e6:1)).toFixed(2)+(n>=1e12?"T":n>=1e9?"B":n>=1e6?"M":"");}
function link(url,label){return typeof url==="string"&&url.startsWith("https://")?'<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+esc(label||"SEC ↗")+'</a>':"N/A";}
function metric(name,value,sub){return '<div class="q-kpi"><div class="name">'+esc(name)+'</div><div class="value">'+esc(value)+'</div><div class="sub">'+esc(sub||"")+'</div></div>';}
const validationUi={"en":{"title":"Backtest Validation Gates","historical_universe":"Historical constituents","corporate_actions":"Split/dividend price reconciliation","walk_forward":"Locked walk-forward evaluation","status":"Not verified","warning":"Research diagnostics only. These gates must all pass before performance is treated as validated strategy evidence."},"zh-CN":{"title":"回测可信度验证门槛","historical_universe":"历史时点股票池","corporate_actions":"拆股／分红与复权价格核对","walk_forward":"锁定参数的 Walk-forward 样本外检验","status":"尚未核验","warning":"当前仅为研究性价格回测。上述验证全部通过之前，不得把历史收益视为已验证的策略 Alpha。"},"fr":{"title":"Contrôles de validation du backtest","historical_universe":"Constituants historiques","corporate_actions":"Ajustements fractionnements/dividendes","walk_forward":"Évaluation walk-forward indépendante","status":"Non vérifié","warning":"Résultats exploratoires uniquement; validation incomplète."},"es":{"title":"Controles de validación","historical_universe":"Universo histórico","corporate_actions":"Ajustes de splits y dividendos","walk_forward":"Validación fuera de muestra walk-forward","status":"Sin verificar","warning":"Resultados exploratorios; no constituyen alfa validada."},"ja":{"title":"バックテスト検証ゲート","historical_universe":"過去の構成銘柄","corporate_actions":"株式分割・配当調整","walk_forward":"ウォークフォワード検証","status":"未検証","warning":"これらを検証するまでは探索的な株価診断です。"}};
for(const [lang,labels] of Object.entries(validationUi))Object.assign(locales[lang],Object.fromEntries(Object.entries(labels).map(([k,v])=>["validation_"+k,v])));
function backtestValidationView(q){
 const gates=q?.backtest_validation_gates||{},names=["historical_universe","corporate_actions","walk_forward"];
 return '<section class="q-validation" aria-label="'+esc(t("validation_title"))+'"><h4>'+esc(t("validation_title"))+' · '+(gates.passed_count??0)+' / '+(gates.required_count??3)+'</h4>'
  +names.map(k=>'<div class="q-validation-row"><span>'+esc(t("validation_"+k))+'</span><span>'+esc(t("validation_status"))+'</span></div>').join('')
  +'<p class="q-note">'+esc(t("validation_warning"))+'</p></section>';
}
const scenarioUi={"en":{"backWindow":"Backtest window","fyEnd":"FY ended","filed":"SEC filing date","revenueCovered":"SEC annual revenue available","factorCoverage":"Supplier evidence factor coverage (weighted mean)","completeFactor":"Complete six-factor Alpha","provisionalFactor":"Exploratory six-factor scores","priceData":"Observed latest stock closes","coverageWarning":"Market or financial-field coverage is not supply-chain evidence completeness.","selectionNote":"Selected stock","monthly":"Monthly top {n}","weight":"equal weight","vixOn":"VIX exposure trigger on","vixOff":"VIX trigger off","sector":"max 3 per sector","bps":"bps per side","lag":"following-session close execution","dataStatus":"Data status","riskNote":"Research diagnostic only: historical pool, split/dividend reconciliation and walk-forward checks remain unverified."},"zh-CN":{"backWindow":"回测时间区间","fyEnd":"财年结束日期","filed":"SEC 财报申报日期","revenueCovered":"SEC 年度营收字段覆盖","factorCoverage":"供应链证据因子平均覆盖率","completeFactor":"完整六因子正式评分","provisionalFactor":"探索性六因子评分 †","priceData":"真实最新股票收盘价覆盖","coverageWarning":"行情或财务字段覆盖率不等于供应链证据完整度；探索性评分也不代表六因子全部核实。","selectionNote":"当前选中股票","monthly":"每月排名前 {n} 只","weight":"等权配置","vixOn":"启用 VIX 仓位调整","vixOff":"未启用 VIX 仓位调整","sector":"单板块最多 3 只","bps":"单边交易基点","lag":"次交易日收盘价模拟执行","dataStatus":"数据状态","riskNote":"仅供研究诊断：历史股票池、拆股分红及复权核对、滚动样本外验证仍未完成。"},"fr":{"backWindow":"Période du backtest","fyEnd":"Exercice clos le","filed":"Dépôt SEC","revenueCovered":"Revenu annuel SEC disponible","factorCoverage":"Couverture des preuves de chaîne (moyenne)","completeFactor":"Alpha six facteurs complet","provisionalFactor":"Scores exploratoires","priceData":"Clôtures observées","coverageWarning":"La couverture des prix ou données financières ne démontre pas la complétude des preuves.","selectionNote":"Titre sélectionné","monthly":"Top {n} mensuel","weight":"pondération égale","vixOn":"VIX activé","vixOff":"VIX désactivé","sector":"max. 3 par secteur","bps":"pb par sens","lag":"exécution simulée à la clôture suivante","dataStatus":"Statut","riskNote":"Diagnostic exploratoire : univers historique, splits/dividendes et walk-forward non vérifiés."},"es":{"backWindow":"Período del backtest","fyEnd":"Cierre del ejercicio","filed":"Presentación SEC","revenueCovered":"Ingresos anuales SEC","factorCoverage":"Cobertura media de pruebas de cadena","completeFactor":"Alfa completo de seis factores","provisionalFactor":"Puntuaciones exploratorias","priceData":"Cierres observados","coverageWarning":"La cobertura de precios o datos financieros no equivale a evidencia completa de la cadena.","selectionNote":"Acción seleccionada","monthly":"Top {n} mensual","weight":"igual ponderación","vixOn":"VIX activo","vixOff":"VIX desactivado","sector":"máx. 3 por sector","bps":"pb por lado","lag":"ejecución simulada al cierre siguiente","dataStatus":"Estado","riskNote":"Diagnóstico exploratorio: universo histórico, ajustes y walk-forward pendientes."},"ja":{"backWindow":"バックテスト期間","fyEnd":"対象会計年度末","filed":"SEC提出日","revenueCovered":"SEC年次売上データ","factorCoverage":"サプライチェーン証拠の平均カバー率","completeFactor":"正式6因子スコア","provisionalFactor":"暫定6因子スコア","priceData":"実際の終値データ","coverageWarning":"価格や財務データのカバー率は供給関係の証拠網羅率ではありません。","selectionNote":"選択銘柄","monthly":"月次上位{n}銘柄","weight":"均等配分","vixOn":"VIX有効","vixOff":"VIX無効","sector":"業種上限3銘柄","bps":"片道bp","lag":"翌取引日終値で仮想約定","dataStatus":"データ状態","riskNote":"研究診断のみ。過去の構成銘柄、配当・分割調整、ウォークフォワードは未検証です。"}};
for(const [lang,vals] of Object.entries(scenarioUi))Object.assign(locales[lang],Object.fromEntries(Object.entries(vals).map(([k,v])=>["scenario_"+k,v])));
function pipelineAuditStatus(status){
 const values={
  en:{retrieved:"Retrieved",partial:"Partially retrieved",cached:"Cached data",cached_after_api_failure:"Cached after provider failure",not_configured:"Not configured",not_cached:"No cached data",cache_expired:"Cached data expired"},
  "zh-CN":{retrieved:"已获取",partial:"部分数据已获取",cached:"使用缓存数据",cached_after_api_failure:"接口故障，使用缓存",not_configured:"数据源未配置",not_cached:"无可用缓存",cache_expired:"缓存已过期"},
  fr:{retrieved:"Récupéré",partial:"Partiel",cached:"En cache",cached_after_api_failure:"Cache après panne",not_configured:"Non configuré"},
  es:{retrieved:"Recuperado",partial:"Parcial",cached:"En caché",cached_after_api_failure:"Caché tras fallo",not_configured:"Sin configurar"},
  ja:{retrieved:"取得済み",partial:"一部取得",cached:"キャッシュ",cached_after_api_failure:"障害後キャッシュ",not_configured:"未設定"}
 };
 return (values[L()]||values.en)[status]||t("audit_statusInsufficient");
}
function scenarioDescription(back,key){
 const n=Number.isInteger(back?.top_n)?back.top_n:Number(/Top (\d+)/.exec(key)?.[1]||8);
 const active=Boolean(back?.vix_trigger_enabled??key.includes("VIX Trigger"));
 return [t("scenario_monthly").replace("{n}",n),t("scenario_weight"),t("scenario_sector"),
         String(back?.one_way_bps??10)+" "+t("scenario_bps"),active?t("scenario_vixOn"):t("scenario_vixOff"),t("scenario_lag")].join(" · ");
}
function renderShell(){
 const q=data||{},sc=q.screener||{},available=q.backtest_scenarios||{};
 if(!available[selectedScenario])selectedScenario="1Y · Top 8 · 10 bps";
 const back=available[selectedScenario]||q.backtest||{};
 const horizon=selectedScenario.split(" · ")[0],isVix=selectedScenario.includes("VIX Trigger");
 const baseBack=available[horizon+" · Top 8 · 10 bps"]||{},vixBack=available[horizon+" · VIX Trigger · Top 8 · 10 bps"]||{};
 const vixp=q.vix_trigger_policy||{};
 const m=back.metrics||{},bm=back.benchmarks?.QQQ||{},secs=q.fundamentals_coverage||{};
 const validity=back.status==="COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC";
 const visibleQuantRows=(sc.ranked||[]).filter(x=>(!showOnly||x.rank_eligible) && (
   quantCoverageFilter==="all"||(quantCoverageFilter==="high"&&x.factor_coverage>=.75)||
   (quantCoverageFilter==="mid"&&x.factor_coverage>=.5&&x.factor_coverage<.75)||
   (quantCoverageFilter==="low"&&x.factor_coverage<.5)));
 if(!visibleQuantRows.some(x=>x.ticker===selectedQuantTicker))
   selectedQuantTicker=visibleQuantRows.find(x=>x.rank_eligible)?.ticker||visibleQuantRows[0]?.ticker||null;
 function selectedFYEnd(){
   return (sc.ranked||[]).find(x=>x.ticker===selectedQuantTicker)?.revenue_fy_end||null;
 }
 
 const main=window.M7_LIVE_DATA||{};
 const sameSupplierVersion=Boolean(q.source_snapshot?.fingerprint &&
    main.quant_source_fingerprint===q.source_snapshot.fingerprint &&
    main.as_of===q.source_snapshot.as_of &&
    main.model_version===q.source_snapshot.model_version);
 const mainSupplierByTicker=q.source_alpha_by_ticker||{};
 const localStatus=(status)=>({
   "COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC":t("audit_statusComputed"),
   "HISTORICAL_PRICE_ONLY_RESEARCH_DIAGNOSTIC":t("audit_statusComputed"),
   "CURRENT_CROSS_SECTION_ONLY":t("audit_statusCurrent"),
   "INSUFFICIENT_POINT_IN_TIME_FUNDAMENTALS":t("audit_statusInsufficient"),
   "SCREENING_SCORE_ONLY_NOT_BACKTESTED":t("audit_statusCurrent"),
   "INSUFFICIENT_FULL_HORIZON":t("audit_statusNotAvailable"),
   "INSUFFICIENT_VIX_HISTORY":t("audit_statusNotAvailable")
 }[status]||status||"N/A");

 host.innerHTML='<div class="q-root">'
  +'<div class="q-hero"><div><div class="q-eyebrow">'+esc(t("lab"))+'</div><h2>'+esc(t("title"))+'</h2><div class="q-muted">'+esc(t("subtitle"))+'</div><div class="q-pills" style="margin-top:12px"><span>'+esc(t("screenOnly"))+'</span><span>'+esc(t("backtestOnly"))+'</span><span>'+esc(q.as_of||"N/A")+'</span></div></div><div class="q-actions"><button id="qRefresh" class="q-action">'+esc(t("refresh"))+'</button><div class="q-status">'+esc(t("statusLine"))+': '+esc(pipelineAuditStatus(q.fundamental_audit?.status))+'</div></div></div>'
  +'<div class="q-alert">'+esc(t("notTested"))+' · '+esc(t("caveat"))+'</div>'
  +'<div class="q-status" role="status">'+esc(sameSupplierVersion?t("audit_syncOk"):t("audit_syncPending"))+' · '+esc(t("audit_sourceDate"))+': '+esc(q.source_snapshot?.as_of||"N/A")+' · '+esc(t("audit_source"))+': '+esc(q.source_snapshot?.model_version||"N/A")+'</div>'
   +'<div class="q-insight">'+esc(t("audit_active"))+' · '+esc(q.as_of||"N/A")+'</div>'
  +'<div class="q-panel q-autonomy"><div class="q-head"><div><h3>'+esc(t("autonomous_title"))+'</h3><p>'+esc(t("autonomous_subtitle"))+'</p></div><span class="q-tag ok">'+esc(t("autonomous_mode"))+'</span></div><div class="q-body"><div class="q-auto-flow">'+[1,2,3,4,5].map((i)=>'<span>'+i+' · '+esc(t("autonomous_phase"+i))+'</span>').join('')+'</div><div id="qAutonomous"></div><p class="q-note">'+esc(t("autonomous_notice"))+'</p></div></div>'
   +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("vixTrigger"))+'</h3><p>'+esc(t("vixCaution"))+'</p></div></div><div class="q-body"><div class="q-kpis">'+metric(t("vixClose"),fmt(vixp.latest_vix_close),esc(vixp.latest_vix_date||"N/A")+' · '+esc(vixp.source_provider||""))+metric(t("vixTarget"),pc(vixp.next_target_stock_exposure),t("vixHold")+": "+pc(typeof vixp.next_target_stock_exposure==="number"?1-vixp.next_target_stock_exposure:null))+'</div><div class="q-pills">'+(vixp.bands||[]).map(b=>'<span>VIX '+esc(b.vix)+' → '+pc(b.exposure)+'</span>').join('')+'</div><p class="q-note">'+esc(vixp.execution||"")+' · '+link(vixp.source,"VIX source")+'</p><div id="qVixCompare"></div></div></div>'
  +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("forty_title"))+'</h3><p>'+esc(t("forty_note"))+'</p></div></div><div class="q-scroll" id="qFortyHistorical"></div></div>'
  +'<div class="q-kpis">'+metric(t("return"),pc(m.total_return),"Strategy")
  +metric(t("cagr"),pc(m.cagr_annualized),t("trailing")+": "+esc(back.start_date||"N/A")+" → "+esc(back.end_date||"N/A"))
  +metric(t("sharpe"),fmt(m.sharpe_rf0),t("priceOnly"))
  +metric(t("drawdown"),pc(m.max_drawdown),t("validation"))+'</div>'
  +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("benchmark"))+'</h3><p id="qStrategyDescription">'+esc(scenarioDescription(back,selectedScenario))+'</p></div><div class="q-actions"><button id="qChartNav" aria-pressed="true" class="q-action">'+esc(t("equity"))+'</button><button id="qChartDD" aria-pressed="false" class="q-action">'+esc(t("draw"))+'</button></div></div>'
  +'<div class="q-body q-group"><label class="q-note" for="qScenario">'+esc(t("scenario"))+'</label><select id="qScenario" class="pick">'+Object.keys(q.backtest_scenarios||{}).map(k=>'<option value="'+esc(k)+'" '+(k===selectedScenario?'selected':'')+'>'+esc(k)+'</option>').join('')+'</select><span class="q-note">'+esc(t("rankWarning"))+'</span></div>'
  +'<div class="q-chart" id="qChart"><div class="q-empty">'+esc(t("loading"))+'</div></div><div class="q-legend"><span><i style="background:#64e3cf"></i>'+esc(t("vixMode"))+'</span><span><i style="background:#c8a2ff"></i>'+esc(t("vixBase"))+'</span><span><i style="background:#82b2ff"></i>QQQ</span><span><i style="background:#ebb67d"></i>XLK</span></div></div>'
  +'<div class="q-two"><div class="q-panel"><div class="q-head"><div><h3>'+esc(t("perf"))+'</h3><p>'+esc(t("backtest"))+'</p></div></div><div class="q-body" id="qMetrics"></div></div>'
  +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("screen"))+'</h3><p>'+esc(t("screenNote"))+'</p></div></div><div class="q-body" id="qCoverage"></div></div></div>'
  +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("rank"))+'</h3><p>'+esc(t("audit_rankCaution"))+'</p></div><div class="q-actions"><label class="q-note" for="qCoverageFilter">'+esc(t("status"))+'</label><select class="pick" id="qCoverageFilter">'+["high","mid","low","all"].map(k=>'<option value="'+k+'" '+(k===quantCoverageFilter?'selected':'')+'>'+esc(t("audit_"+k))+'</option>').join('')+'</select><button type="button" id="qFilter" class="q-action" aria-pressed="'+showOnly+'">'+esc(t(showOnly?"showAll":"hideUnranked"))+'</button></div></div><div class="q-scroll"><table class="q-table"><thead><tr>'
  +[t("ticker"),t("score"),t("status"),t("price"),t("cap"),t("revenue"),t("growth"),t("ps"),t("supply"),t("monitor"),t("source")].map(h=>'<th>'+esc(h)+'</th>').join('')
  +'</tr></thead><tbody id="qRanking"></tbody></table></div></div>'
  +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("details"))+'</h3><p>'+esc(t("screenNote"))+'</p></div></div><div class="q-body" id="qFactorDetail"></div></div>'
  +'<div class="q-two"><div class="q-panel"><div class="q-head"><div><h3>'+esc(t("paper"))+'</h3><p>'+esc(t("paperNote"))+'</p></div></div><div class="q-body" id="qPaper"></div></div>'
  +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("sensitivity"))+'</h3></div></div><div class="q-body" id="qScenarioMatrix"></div></div></div>'
  +'<div class="q-two"><div class="q-panel"><div class="q-head"><div><h3>'+esc(t("month"))+'</h3></div></div><div class="q-body" id="qMonthly"></div></div>'
  +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("trades"))+'</h3></div></div><div class="q-scroll" id="qTrades"></div></div></div>'
  +'<div class="q-panel"><div class="q-head"><div><h3>'+esc(t("method"))+'</h3></div></div><div class="q-body"><div class="q-formula">Investability = 0.30×Supply Alpha† + 0.20×Market Monitor + 0.20×Revenue Growth + 0.15×Inverse P/S + 0.05×Size + 0.10×Inverse Volatility<br>Eligibility: ≥ 75% weighted data coverage + ≥ 1 fundamental component</div><p class="q-note">'+esc(t("sourceWarning"))+'</p><p class="q-note">'+esc(t("sourceData"))+'</p><p class="q-note">'+esc(t("risk"))+': '+esc(L()==="en"?(back.limitations||[]).join(" | "):t("scenario_riskNote"))+'</p>'+backtestValidationView(q)+'</div></div>'
  +'</div>';
 renderAutonomous();
 const row=(k,v)=>'<div class="q-metric"><span>'+esc(t(k))+'</span><span>'+esc(v)+'</span></div>';
 document.getElementById("qVixCompare").innerHTML='<div class="q-note">'+esc(t("vixCompare"))+' ('+esc(horizon)+')</div>'+
  [row("vixVReturn",pc(vixBack.metrics?.total_return)),row("vixBReturn",pc(baseBack.metrics?.total_return)),
   row("vixVDrawdown",pc(vixBack.metrics?.max_drawdown)),row("vixBDrawdown",pc(baseBack.metrics?.max_drawdown))].join("")+
  (vixBack.status!=="COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC"?'<div class="q-alert">'+esc(t("vixNoData"))+' · '+esc(vixBack.status||"")+'</div>':"");
 const forties=q.forty_stock_historical_diagnostics||{},
       weighted=q.forty_stock_weighted_price_diagnostics||{};
 document.getElementById("qFortyHistorical").innerHTML=Object.keys(weighted).length
  ?'<div class="q-body"><p class="q-note">'+esc(t("weighted_wnote"))+'</p></div>'
   +'<table class="q-table"><thead><tr>'+[
       t("forty_period"),t("weighted_wvix"),t("weighted_wplain"),
       t("weighted_evix"),"QQQ",t("weighted_wreturn"),t("weighted_wdraw"),t("forty_eligible")
      ].map(k=>'<th>'+esc(k)+'</th>').join('')+'</tr></thead><tbody>'
   +["1Y","3Y","5Y"].map(y=>{
      const a=weighted[y+" · 40 price-score weighted · VIX"]||{};
      const b=weighted[y+" · 40 price-score weighted"]||{};
      const equal=forties[y+" · 40 equal weight · VIX"]||{};
      const valid=a.status==="COMPUTED_PRICE_ONLY_RESEARCH_DIAGNOSTIC";
      return '<tr><td>'+esc(y)+'</td><td><strong>'+fmt(a.metrics?.sharpe_rf0,3)+'</strong></td>'
        +'<td>'+fmt(b.metrics?.sharpe_rf0,3)+'</td>'
        +'<td>'+fmt(equal.metrics?.sharpe_rf0,3)+'</td>'
        +'<td>'+fmt(a.benchmarks?.QQQ?.sharpe_rf0,3)+'</td>'
        +'<td>'+pc(a.metrics?.total_return)+'</td>'
        +'<td>'+pc(a.metrics?.max_drawdown)+'</td>'
        +'<td>'+esc(valid?a.minimum_active_names:"N/A")+'/40</td></tr>';
    }).join('')+'</tbody></table>'
  :'<div class="q-body q-empty">'+esc(t("forty_none"))+'</div>';
 document.getElementById("qMetrics").innerHTML=[
  row("total",pc(m.total_return)+" | QQQ "+pc(bm.total_return)),
  row("cagr",pc(m.cagr_annualized)+" | QQQ "+pc(bm.cagr_annualized)),
  row("vol",pc(m.annualized_volatility)),
  row("sharpe",fmt(m.sharpe_rf0)),row("sortino",fmt(m.sortino_rf0)),row("drawdown",pc(m.max_drawdown)),
  row("info",fmt(back.information_ratio)),row("turn",pc(m.turnover_one_way)),
  row("tradeCost",fmt(m.total_transaction_cost_bps,1)+" bps"),row("positive",pc(m.positive_day_rate)),row("days",String(m.days||"N/A")),
 ].join("");
 document.getElementById("qCoverage").innerHTML=[
  row("scenario_priceData",String(Object.values(mainSupplierByTicker).filter(x=>x?.close!=null).length)+"/40"),
  row("scenario_revenueCovered",(secs.fiscal_revenue??0)+"/40"),
  row("scenario_factorCoverage",pc(Object.values(mainSupplierByTicker).reduce((v,x)=>v+(typeof x?.coverage==="number"?x.coverage:0),0)/Math.max(1,Object.keys(mainSupplierByTicker).length))),
  row("scenario_completeFactor",String(Object.values(mainSupplierByTicker).filter(x=>x?.alpha!=null).length)+"/40"),
  row("scenario_provisionalFactor",String(Object.values(mainSupplierByTicker).filter(x=>x?.provisional_alpha!=null).length)+"/40"),
  row("eligible",(sc.eligible_count??0)+"/40"),
  row("scenario_backWindow",(back.start_date||"N/A")+" → "+(back.end_date||"N/A")),
  '<div class="q-metric"><span>'+esc(t("period"))+'</span><span id="qFiscalPeriod">'+esc(selectedQuantTicker||"N/A")+' · '+esc(selectedFYEnd()||"N/A")+'</span></div>',
  row("priceOnly",localStatus(back.status)),
 ].join("")+'<div style="margin-top:13px" class="q-insight">'+esc(t("scenario_coverageWarning"))+'</div>';
 const rank=(sc.ranked||[]).filter(x=>(!showOnly||x.rank_eligible) && (
  quantCoverageFilter==="all"||
  (quantCoverageFilter==="high"&&x.factor_coverage>=.75)||
  (quantCoverageFilter==="mid"&&x.factor_coverage>=.5&&x.factor_coverage<.75)||
  (quantCoverageFilter==="low"&&x.factor_coverage<.5)));
 if(!rank.some(x=>x.ticker===selectedQuantTicker))selectedQuantTicker=rank.find(x=>x.rank_eligible)?.ticker||rank[0]?.ticker||null;
 const byTicker=mainSupplierByTicker;
 document.getElementById("qRanking").innerHTML=rank.map(x=>{
  const ticker=x.ticker;
  const row=sameSupplierVersion?(byTicker[ticker]||{}):{};
  return '<tr data-q-ticker="'+esc(ticker)+'" class="'+(ticker===selectedQuantTicker?'q-selected':'')+'" aria-selected="'+(ticker===selectedQuantTicker)+'" title="'+esc(localStatus(x.status))+'" tabindex="0" role="button" style="cursor:pointer"><td><strong>'+esc(ticker)+'</strong></td>'
   +'<td>'+(x.rank?'<span class="q-tag ok">'+esc(x.rank)+" · "+fmt(x.investability_score)+'</span>':'<span class="q-tag warm">'+esc(t("unranked"))+'</span>')+'</td>'
   +'<td>'+pc(x.factor_coverage,0)+'</td>'
   +'<td class="q-number">'+fmt(row.close??null)+'</td>'
   +'<td class="q-number">'+compact(x.market_cap_proxy_usd)+'</td>'
   +'<td class="q-number">'+compact(x.revenue_fy_usd)+'</td>'
   +'<td class="q-number">'+pc(x.revenue_growth_yoy)+'</td>'
   +'<td class="q-number">'+fmt(x.price_to_sales_proxy)+'</td>'
   +'<td class="q-number">'+fmt(row.alpha??row.provisional_alpha)+'</td>'
   +'<td class="q-number">'+fmt(row.monitor_score)+'</td>'
   +'<td>'+link(x.fundamental_source,"SEC ↗")+'</td></tr>';
 }).join("")||'<tr><td colspan="11">'+esc(t("noScore"))+'</td></tr>';
 document.getElementById("qPaper").innerHTML='<div class="q-alert">'+esc(t("audit_archived"))+' · '+esc(q.prospective_screen_portfolio?.signal_as_of||"N/A")+'</div>';
 const scenarios=Object.fromEntries(Object.entries(q.backtest_scenarios||{}).filter(([k])=>k.startsWith(selectedScenario.split(" · ")[0]+" · ")));
 document.getElementById("qScenarioMatrix").innerHTML=Object.keys(scenarios).length
  ?Object.entries(scenarios).map(([k,v])=>'<div class="q-metric"><span>'+esc(k)+'</span><span>'+esc(t("impact"))+': '+pc(v.metrics?.total_return)+' · Sharpe '+fmt(v.metrics?.sharpe_rf0)+'</span></div>').join('')
  :'<div class="q-empty">'+esc(t("none"))+'</div>';
 const shown=rank.find(x=>x.ticker===selectedQuantTicker)||rank[0];
 factorDetail(shown);
 document.querySelectorAll("#qRanking [data-q-ticker]").forEach(tr=>tr.addEventListener("click",e=>{
   if(e.target.closest("a"))return;
   selectedQuantTicker=tr.dataset.qTicker;
   factorDetail((sc.ranked||[]).find(x=>x.ticker===selectedQuantTicker));
   document.querySelectorAll("#qRanking [data-q-ticker]").forEach(el=>{
     const selected=el.dataset.qTicker===selectedQuantTicker;
     el.classList.toggle("q-selected",selected);
     el.setAttribute("aria-selected",String(selected));
   });
   const fy=document.getElementById("qFiscalPeriod");
   if(fy)fy.textContent=selectedQuantTicker+" · "+(selectedFYEnd()||"N/A");
 }));
 document.querySelectorAll("#qRanking [data-q-ticker]").forEach(tr=>tr.addEventListener("keydown",e=>{
   if(e.key==="Enter"||e.key===" "){e.preventDefault();tr.click();}
 }));
 const months=back.monthly||[];
 const rr=months.map(x=>'<div class="q-month" title="'+esc(x.month)+' QQQ '+pc(x.qqq)+' XLK '+pc(x.xlk)+'" style="background:'+(x.strategy>=0?"#173f3b":"#492b37")+'"><span>'+esc(x.month)+'</span><strong class="'+(x.strategy>=0?"q-positive":"q-negative")+'">'+pc(x.strategy)+'</strong><small class="q-muted">QQQ '+pc(x.qqq)+'</small></div>').join("");
 document.getElementById("qMonthly").innerHTML=rr?'<div class="q-matrix">'+rr+'</div>':'<div class="q-empty">'+esc(t("none"))+'</div>';
 const trs=(back.trades||[]).slice(-18).reverse();
 document.getElementById("qTrades").innerHTML=trs.length?'<table class="q-table"><thead><tr>'+[t("tradeDate"),t("signalDate"),t("positions"),t("vixSignal"),t("turnover"),t("cost")].map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+trs.map(x=>'<tr><td>'+esc(x.date)+'</td><td>'+esc(x.signal_date)+'</td><td>'+esc((x.tickers||[]).join(", "))+'</td><td>'+fmt(x.vix_close)+' / '+pc(x.target_stock_exposure)+'</td><td>'+pc(x.one_way_turnover)+'</td><td>'+fmt((x.cost_fraction||0)*10000,1)+' bps</td></tr>').join('')+'</tbody></table>':'<div class="q-body q-empty">'+esc(t("none"))+'</div>';
 document.getElementById("qRefresh")?.addEventListener("click",()=>fetchQuant(true));
 document.getElementById("qScenario")?.addEventListener("change",e=>{selectedScenario=e.target.value;renderShell();});

 document.getElementById("qFilter")?.addEventListener("click",()=>{showOnly=!showOnly;renderShell()});
 document.getElementById("qCoverageFilter")?.addEventListener("change",e=>{quantCoverageFilter=e.target.value;renderShell()});
 document.getElementById("qChartNav")?.addEventListener("click",()=>{chartMode="nav";drawChart()});
 document.getElementById("qChartDD")?.addEventListener("click",()=>{chartMode="dd";drawChart()});
 drawChart();
}
function drawChart(){
 const c=document.getElementById("qChart");
 if(!c)return;
 const back=data?.backtest_scenarios?.[selectedScenario]||data?.backtest||{};
 const horizon=selectedScenario.split(" · ")[0];
 const base=data?.backtest_scenarios?.[horizon+" · Top 8 · 10 bps"]||{};
 const baseByDate=Object.fromEntries((base.curve||[]).map(r=>[r.date,r.strategy_nav]));
 const records=(back.curve||[]).map(r=>({...r,baseline_nav:baseByDate[r.date]}));
 if(records.length<10){c.innerHTML='<div class="q-empty">'+esc(t("none"))+'</div>';return;}
 const width=960,height=290,p={l:63,r:25,t:25,b:37},W=width-p.l-p.r,H=height-p.t-p.b;
 const datasets=chartMode==="dd"?[{key:"strategy_nav",label:"Strategy drawdown",color:"#64e3cf"}]:
  [{key:"strategy_nav",label:"Strategy",color:"#64e3cf"},
  ...(selectedScenario.includes("VIX Trigger")&&base.curve?.length?[{key:"baseline_nav",label:"Baseline",color:"#c8a2ff"}]:[]),
  {key:"qqq_nav",label:"QQQ",color:"#82b2ff"},{key:"xlk_nav",label:"XLK",color:"#ebb67d"}];
 const dd=records.map(r=>r.strategy_nav);
 let running=1;const ddval=dd.map(v=>(running=Math.max(running,v),v/running-1));
 const array=chartMode==="dd"?ddval:records.flatMap(x=>datasets.map(ds=>x[ds.key]));
 let low=Math.min(...array),hi=Math.max(...array);if(hi-low<.0001){hi+=.02;low-=.02;}
 const pad=(hi-low)*.13;low-=pad;hi+=pad;
 const x=i=>p.l+i/(records.length-1)*W;
 const y=v=>p.t+(hi-v)/(hi-low)*H;
 const ticks=[0,1,2,3,4].map(i=>{const yy=p.t+i/4*H,v=hi-i/4*(hi-low);return '<g><line x1="'+p.l+'" y1="'+yy+'" x2="'+(width-p.r)+'" y2="'+yy+'" stroke="#29415b" stroke-dasharray="3 5"/><text x="'+(p.l-10)+'" y="'+(yy+4)+'" font-size="11" text-anchor="end" fill="#93a9c5">'+(chartMode==="dd"?pc(v):fmt(v,2))+'</text></g>'}).join("");
 const lines=datasets.map(ds=>{const values=chartMode==="dd"?ddval:records.map(r=>r[ds.key]);
 return '<path d="'+values.map((v,i)=>(i?"L":"M")+x(i).toFixed(2)+" "+y(v).toFixed(2)).join(" ")+'" fill="none" stroke="'+ds.color+'" stroke-width="'+(ds.key==="strategy_nav"?2.8:1.7)+'" stroke-linejoin="round"/>';
 }).join("");
 const xt=[0,.25,.5,.75,1].map(f=>{const i=Math.round(f*(records.length-1));return '<text font-size="11" fill="#91a9c5" x="'+x(i)+'" y="'+(height-9)+'" text-anchor="middle">'+esc(records[i].date.slice(2,7))+'</text>'}).join("");
 c.innerHTML='<svg viewBox="0 0 '+width+' '+height+'" preserveAspectRatio="none" aria-label="Strategy equity curve and benchmark prices">'+ticks+lines+xt+'<rect x="'+p.l+'" y="'+p.t+'" width="'+W+'" height="'+H+'" fill="transparent" id="qPointerArea"/></svg><div id="qTip" class="q-chart-tip" hidden></div>';
 const element=c.querySelector("svg"),area=c.querySelector("#qPointerArea"),tip=c.querySelector("#qTip");
 const show=e=>{
  const rect=element.getBoundingClientRect(),fraction=(e.clientX-rect.left)/Math.max(rect.width,1);
  const i=Math.max(0,Math.min(records.length-1,Math.round((fraction*width-p.l)/W*(records.length-1))));
  const r=records[i],value=chartMode==="dd"?pc(ddval[i]):fmt(r.strategy_nav,3);
  tip.innerHTML='<strong>'+esc(r.date)+'</strong><br>Strategy: '+esc(value)+(chartMode==="nav"?'<br>QQQ '+fmt(r.qqq_nav,3)+' · XLK '+fmt(r.xlk_nav,3)+(Number.isFinite(r.baseline_nav)?'<br>Baseline '+fmt(r.baseline_nav,3):'')+(Number.isFinite(r.stock_exposure)?'<br>Equity '+pc(r.stock_exposure)+' · VIX '+fmt(r.vix_signal_close):''):'');
  tip.hidden=false;tip.style.left=Math.max(0,Math.min(c.clientWidth-155,(e.clientX-c.getBoundingClientRect().left+8)))+'px';tip.style.top='16px';
 };
 area?.addEventListener("pointermove",show);area?.addEventListener("pointerleave",()=>{tip.hidden=true});
 for(const key of ["qChartNav","qChartDD"]){const el=document.getElementById(key);if(el)el.setAttribute("aria-pressed",String((key==="qChartNav")===(chartMode==="nav")));}
}


const autoWeightLabels={"en":["Top 10 share of NAV","Bottom 10 share of NAV","Top / bottom concentration","Total stock allocation","Score-weighted: 12% minimum diversification + 88% confidence-adjusted softmax (temperature 1.25). Individual names capped at 10% of invested equity budget; sectors at 45% (also 15% / 40% NAV hard limits). Estimated factors are labeled and never backfilled into historical returns.","vs. equal weight"],"zh-CN":["前 10 名总仓位","后 10 名总仓位","前后十名仓位倍数","股票总仓位","投资性评分加权：12% 基础仓位均匀分散至 40 股，88% 按置信度折减后的评分 Softmax 分配（温度 1.25）。单股最多占股票仓位 10%，单行业最多 45%（并保留净值 15%／40% 的硬上限）。估计值会标注，不能倒填历史回测。","相对等权"],"fr":["Top 10 allocation","10 derniers","Concentration","Exposition totale","Allocation pondérée: 12% également réparti, 88% softmax (température 1,25). Max 10% du budget actions par titre et 45% par secteur; facteurs estimés signalés.","vs égal"],"es":["Peso top 10","Peso últimos 10","Concentración","Exposición total","Ponderación por puntuación: 12% diversificado + 88% softmax (temperatura 1,25). Máximo 10% del presupuesto de acciones por título y 45% por sector.","vs equiponderación"],"ja":["上位10銘柄の配分","下位10銘柄の配分","配分比率","株式配分合計","投資スコア加重: 12%均等、88%信頼度調整ソフトマックス（温度1.25）。各銘柄は株式枠の10%、各セクター45%が上限。","均等配分比"]};
const autoWeightKeys=["top","bottom","spread","total","note","multiplier"];
for(const [lang,labels] of Object.entries(autoWeightLabels))labels.forEach((value,i)=>{locales[lang]["auto_w_"+autoWeightKeys[i]]=value;});
function renderUniverseQuality(universe,weights){
 if(!universe||!Array.isArray(universe.candidates))return "";
 const c=universe.candidates;
 const ranked=c.slice().sort((a,b)=>(weights[b.ticker]??-1)-(weights[a.ticker]??-1));
 const active=ranked.filter(r=>typeof weights[r.ticker]==="number");
 const total=active.reduce((sum,r)=>sum+(weights[r.ticker]||0),0);
 const equal=active.length?total/active.length:0;
 const top10=ranked.slice(0,10).reduce((sum,r)=>sum+(weights[r.ticker]||0),0);
 const bottom10=ranked.slice(-10).reduce((sum,r)=>sum+(weights[r.ticker]||0),0);
 const maxW=Math.max(...Object.values(weights).filter(Number.isFinite),0.00001);
 const summary=active.length===40&&total>0
  ?'<div class="q-auto-weight-summary">'
   +'<div><small>'+esc(t("auto_w_top"))+'</small><strong>'+pc(top10,2)+'</strong></div>'
   +'<div><small>'+esc(t("auto_w_bottom"))+'</small><strong>'+pc(bottom10,2)+'</strong></div>'
   +'<div><small>'+esc(t("auto_w_spread"))+'</small><strong>'+(bottom10>0?fmt(top10/bottom10,2)+"×":"N/A")+'</strong></div>'
   +'<div><small>'+esc(t("auto_w_total"))+'</small><strong>'+pc(total,2)+'</strong></div>'
   +'</div>':"";
 return '<h4>'+esc(t("auto_quality_universe"))+' ('+c.length+'/40)</h4>'
  +'<p class="q-note">'+esc(t("auto_w_note"))+'</p>'+summary
  +'<div class="q-scroll"><table class="q-table"><thead><tr>'
  +['Ticker',t("auto_quality_score"),t("auto_quality_observed"),t("auto_quality_estimated"),t("autonomous_pending"),t("auto_w_multiplier")].map(k=>'<th>'+esc(k)+'</th>').join('')
  +'</tr></thead><tbody>'
  +ranked.map((r,i)=>{
    const w=weights[r.ticker],pct=typeof w==="number"?w/maxW*100:0;
    return '<tr><td><strong>'+esc(r.ticker)+'</strong> <small>#'+esc(r.candidate_rank||i+1)+'</small></td>'
      +'<td class="q-number">'+fmt(r.research_score,2)+'</td>'
      +'<td class="q-number">'+pc(r.observed_factor_coverage,0)+'</td>'
      +'<td class="q-number">'+pc(r.estimated_factor_weight,0)+'</td>'
      +'<td class="q-auto-weight-cell"><div><b>'+pc(w,2)+'</b><div class="q-auto-weight-track"><div style="width:'+pct.toFixed(2)+'%"></div></div></div></td>'
      +'<td class="q-number">'+(typeof w==="number"&&equal>0?fmt(w/equal,2)+"×":"N/A")+'</td></tr>';
  }).join('')+'</tbody></table></div>';
}
const paperAuditEvents={
en:{ORDER_PROPOSED:"Order proposed (paper)",PAPER_FILLED:"Simulated fill",NO_ORDER:"Order blocked by risk gate",UNFILLED_ORDER_REWEIGHTED_BY_INVESTABILITY:"Pending order reweighted by investability",UNFILLED_ORDER_UPGRADED_TO_40:"Pending allocation expanded to 40 names",FILL_REJECTED_MISSING_PRICE:"Simulated fill rejected: missing price",NO_SIGNAL_VIX_UNAVAILABLE:"No VIX signal; trading paused"},
"zh-CN":{ORDER_PROPOSED:"已生成模拟订单计划",PAPER_FILLED:"已完成模拟成交",NO_ORDER:"风控阻止下单",UNFILLED_ORDER_REWEIGHTED_BY_INVESTABILITY:"待执行订单按投资性重新加权",UNFILLED_ORDER_UPGRADED_TO_40:"待执行组合升级为40股",FILL_REJECTED_MISSING_PRICE:"缺少真实收盘价，模拟成交被拒绝",NO_SIGNAL_VIX_UNAVAILABLE:"缺失 VIX 信号，交易暂停"},
fr:{ORDER_PROPOSED:"Ordre simulé proposé",PAPER_FILLED:"Exécution simulée",NO_ORDER:"Ordre bloqué par le risque",UNFILLED_ORDER_REWEIGHTED_BY_INVESTABILITY:"Ordre en attente repondéré",UNFILLED_ORDER_UPGRADED_TO_40:"Allocation élargie à 40 titres",FILL_REJECTED_MISSING_PRICE:"Prix manquant, exécution rejetée",NO_SIGNAL_VIX_UNAVAILABLE:"Signal VIX absent, pause"},
es:{ORDER_PROPOSED:"Orden simulada propuesta",PAPER_FILLED:"Ejecución simulada",NO_ORDER:"Orden bloqueada por riesgo",UNFILLED_ORDER_REWEIGHTED_BY_INVESTABILITY:"Orden pendiente reponderada",UNFILLED_ORDER_UPGRADED_TO_40:"Asignación ampliada a 40",FILL_REJECTED_MISSING_PRICE:"Precio ausente, ejecución rechazada",NO_SIGNAL_VIX_UNAVAILABLE:"Sin señal VIX, pausa"},
ja:{ORDER_PROPOSED:"仮想注文計画を生成",PAPER_FILLED:"仮想約定",NO_ORDER:"リスク管理により注文停止",UNFILLED_ORDER_REWEIGHTED_BY_INVESTABILITY:"未約定注文を投資性で再加重",UNFILLED_ORDER_UPGRADED_TO_40:"40銘柄に拡張",FILL_REJECTED_MISSING_PRICE:"価格欠損で仮想約定を拒否",NO_SIGNAL_VIX_UNAVAILABLE:"VIX信号欠損・停止"}
};
const riskText={
en:"Caps on invested stock budget: single name 10%, sector 45% · simulated cost 10 bps/side",
"zh-CN":"股票投资仓位内：单股上限 10%，单行业上限 45% · 模拟交易成本单边 10 基点",
fr:"Plafonds sur budget actions : titre 10 %, secteur 45 % · coût fictif 10 pb par côté",
es:"Límites del presupuesto invertido: acción 10 %, sector 45 % · 10 pb por lado",
ja:"株式枠の上限：1銘柄10％、セクター45％ · 仮想取引コスト片道10bp"
};
function paperEventLabel(code){return paperAuditEvents[L()]?.[code]||paperAuditEvents.en[code]||String(code).replaceAll("_"," ");}
function autoMoney(v){return typeof v==="number"&&Number.isFinite(v)?"$"+v.toLocaleString(L(),{minimumFractionDigits:2,maximumFractionDigits:2}):"N/A";}
function renderAutonomous(){
 const el=document.getElementById("qAutonomous");if(!el)return;
 const a=paperState;if(!a){el.innerHTML='<div class="q-empty">'+esc(t("autonomous_empty"))+'</div>';return;}
 const paperUiTranslations={"en":["Paper account active (simulation)","Paper account halted; inspect the audit log"],"zh-CN":["模拟交易账户运行中","模拟账户已暂停，请检查审计日志"],"fr":["Compte simulé actif","Compte simulé suspendu; voir le journal"],"es":["Cuenta simulada activa","Cuenta simulada detenida; revise el registro"],"ja":["仮想口座運用中","仮想口座停止中・監査ログを確認"]};
 for(const [lang,values] of Object.entries(paperUiTranslations)){
  locales[lang].audit_paperActive=values[0];locales[lang].audit_paperHalted=values[1];
 }
 const paperStatusMap={"AWAITING_NEXT_CLOSE":t("audit_statusPaper"),"PAPER_ACTIVE":t("audit_paperActive"),"INSUFFICIENT_OBSERVED_PAPER_SESSIONS":t("audit_statusPending")};
 const pending=a.pending||{},weights=pending.weights||{},positions=a.positions_value||{},log=(a.audit||[]).slice(-10).reverse();
 const cells=(items,formatter)=>Object.entries(items).map(([k,v])=>'<tr><td>'+esc(k)+'</td><td>'+formatter(v)+'</td></tr>').join('');
 const mini=(title,rows)=>'<div><h4>'+esc(title)+'</h4><div class="q-scroll"><table class="q-table"><tbody>'+ (rows||'<tr><td>—</td></tr>')+'</tbody></table></div></div>';
 el.innerHTML='<div class="q-auto-kpis">'
  +metric(t("autonomous_equity"),autoMoney(a.equity),esc(a.last_price_day||""))
  +metric(t("autonomous_cash"),autoMoney(a.cash),t("autonomous_mode"))
  +metric(t("autonomous_pnl"),autoMoney(a.unrealized_pnl),"vs $1,000")
  +metric(t("autonomous_fees"),autoMoney(a.total_fees),esc(a.trade_count||0)+" simulated fills")
  +metric(t("weighted_papersharpe"),fmt(a.forward_performance?.sharpe_rf0,3),
          esc(paperStatusMap[a.forward_performance?.status]||t("audit_statusPending")))
  +metric(t("weighted_papersessions"),String(a.forward_performance?.observed_sessions??0),
          t("weighted_paperthreshold"))+'</div>'
  +'<div class="q-status q-auto-state">'+esc(a.status?.startsWith("HALTED_")?t("audit_paperHalted"):paperStatusMap[a.status]||a.status)+' · '+esc(pending.signal_day||a.last_price_day||"N/A")+'</div>'
  +'<div class="q-two">'+mini(t("autonomous_pending"),cells(weights,pc))+mini(t("autonomous_positions"),cells(positions,autoMoney))+'</div>'
  +renderUniverseQuality(data?.autonomous_universe,pending.weights||{})
  +'<h4>'+esc(t("autonomous_audit"))+'</h4><div class="q-auto-log">'+log.map(e=>'<div><span>'+esc(e.date)+'</span><strong>'+esc(paperEventLabel(e.event))+'</strong></div>').join('')+'</div>'
  +'<div class="q-note">'+esc(riskText[L()]||riskText.en)+'</div>';
}
async function fetchPaper(force=false){
 try{
  const res=await fetch("data/quant/paper_state.json?ts="+(force?Date.now():Math.floor(Date.now()/600000)),{cache:"no-store"});
  if(!res.ok)throw Error("no ledger");
  const value=await res.json();
  if(value.mode!=="PAPER_ONLY"||value.live_enabled!==false)throw Error("invalid mode");
  paperState=value;
 }catch(_){paperState=null}
 renderAutonomous();
}

async function fetchQuant(force=false){
 if(!data)host.innerHTML='<div class="q-empty">'+esc(t("fetch"))+'</div>';
 try{
  const response=await fetch("data/quant/latest.json?ts="+(force?Date.now():Math.floor(Date.now()/600000)),{cache:"no-store"});
  if(!response.ok)throw Error("quant API status "+response.status);
  const obj=await response.json();
  if(!obj.screener||!obj.backtest)throw Error("invalid quant research snapshot");
  data=obj;renderShell();fetchPaper(force);
 }catch(e){
  if(data)renderShell();
  else host.innerHTML='<div class="q-panel"><div class="q-body q-empty">'+esc(t("loading"))+' <a href="https://github.com/VioletGo319/finance_dashboard/actions" target="_blank">GitHub Actions ↗</a></div></div>';
 }
}
function renderLocale(){if(data)renderShell();else fetchQuant();}
document.getElementById("m7Language")?.addEventListener("change",()=>setTimeout(renderLocale,30));
window.addEventListener("m7-supplier-snapshot-updated",()=>{if(data)renderShell()});
document.querySelector('[data-tab="quant"]')?.addEventListener("click",()=>{if(data)renderShell();else fetchQuant();});
window.M7QuantLab={refresh:fetchQuant,get data(){return data}};
fetchQuant();
})();