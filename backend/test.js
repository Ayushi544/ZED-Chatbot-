
// ── CONFIG ─────────────────────────────────────────────────────
const API = window.location.hostname==='localhost'?'http://localhost:8000':window.location.origin;
let lang='English', chatBusy=false, fcBusy=false;
let chatHist=[], fcHist=[];
let chatFile=null, activeRec=null, activeRecBtn=null;
const answers={};

// ── ZED 20 OFFICIAL PARAMETERS ─────────────────────────────────
const ALL_PARAMS = [
  {id:'p1',  name:'Leadership',                        level:'Bronze', icon:'👤', note:'Roles, organogram, quality policy, regulatory compliance review.'},
  {id:'p2',  name:'Swachh Workplace',                  level:'Bronze', icon:'🏭', note:'Cleaning SOPs, organised workspaces, periodic cleaning audits.'},
  {id:'p3',  name:'Occupational Safety',               level:'Bronze', icon:'🦺', note:'Safety policy, PPE use, safety training, incident RCA/CAPA, mock drills. ISO 45001 exempts.'},
  {id:'p4',  name:'Measurement of Timely Delivery',    level:'Bronze', icon:'📦', note:'Delivery recording system, contract monitoring, management review.'},
  {id:'p5',  name:'Quality Management',                level:'Bronze', icon:'✅', note:'Quality requirements, training, audits, monitoring. ISO 9001 / IATF exempts.'},
  {id:'p6',  name:'Human Resource Management',         level:'Silver', icon:'👥', note:'HR processes, development plans, skill mapping, review.'},
  {id:'p7',  name:'Daily Works Management',            level:'Silver', icon:'📋', note:'QCD targets aligned to strategy, daily communication, RCA/CAPA, review.'},
  {id:'p8',  name:'Planned Maintenance & Calibration', level:'Silver', icon:'🔧', note:'Maintenance plans, calibration, RCA/CAPA, MTTR/MTBF.'},
  {id:'p9',  name:'Process Control',                   level:'Silver', icon:'⚙️', note:'SOPs, proactive process planning, monitoring, RCA/CAPA, reviews.'},
  {id:'p10', name:'Product Quality & Safety',          level:'Silver', icon:'🔬', note:'Testing/certification, non-conformance RCA/CAPA, management review.'},
  {id:'p11', name:'Material Management',               level:'Silver', icon:'📦', note:'Material planning, inventory control, handling SOPs, RCA/CAPA.'},
  {id:'p12', name:'Energy Management',                 level:'Silver', icon:'⚡', note:'Energy targets, consumption tracking, training, audits. ISO 50001 exempts.'},
  {id:'p13', name:'Environment Management',            level:'Silver', icon:'🌱', note:'Emissions/waste/discharge systems, audits, staff training. ISO 14001 exempts.'},
  {id:'p14', name:'Measurement & Analysis',            level:'Silver', icon:'📊', note:'Senior oversight of defects, rework, COPQ, CSAT, RCA/CAPA.'},
  {id:'p15', name:'Supply Chain Management',           level:'Gold',   icon:'🔗', note:'Vendor selection/evaluation, supply chain sustainability, performance monitoring.'},
  {id:'p16', name:'Risk Management',                   level:'Gold',   icon:'⚠️',  note:'Risk Management Plan, risk assessment and mitigation, senior review.'},
  {id:'p17', name:'Waste Management (Muda/Mura/Muri)', level:'Gold',   icon:'♻️',  note:'7-waste reduction plan, targets, employee training. Lean cert exempts.'},
  {id:'p18', name:'Technology Selection & Upgradation',level:'Gold',   icon:'💡', note:'Proactive technology selection, digitalization/IoT planning.'},
  {id:'p19', name:'Natural Resource Conservation',     level:'Gold',   icon:'🌿', note:'Resource consumption review, non-renewable reduction, employee training.'},
  {id:'p20', name:'Corporate Social Responsibility',   level:'Gold',   icon:'🤝', note:'CSR policy, action plans, community/labour/environment, senior review.'},
];

const LEVEL_PARAMS = {
  Bronze:   ALL_PARAMS.filter(p=>p.level==='Bronze'),
  Silver:   ALL_PARAMS.filter(p=>['Bronze','Silver'].includes(p.level)),
  Gold:     ALL_PARAMS,
  Guidance: ALL_PARAMS.filter(p=>p.level==='Bronze'),
};

// ── 5 QUESTIONS PER PARAMETER ──────────────────────────────────
const QUESTIONS = {
  p1:['How clearly are each employee\'s role, responsibility and reporting line written down and shared with them?',
      'How well does your enterprise maintain an up-to-date organisation chart showing all positions?',
      'How regularly does senior leadership review whether the enterprise is meeting its quality and delivery targets?',
      'How systematically does your enterprise track and review compliance with all applicable government regulations and licences?',
      'How effectively are quality, safety, and environmental performance outcomes included in periodic leadership review meetings?'],
  p2:['How thoroughly does your enterprise define and follow cleaning and hygiene procedures suited to your product type and regulatory requirements?',
      'How consistently are your machines, tools and workspaces kept clean and organised as per your defined standards?',
      'To what extent are all areas — shop floor, stores, finished goods area, and toilets — covered by your cleaning practices?',
      'How well does your enterprise conduct and record periodic cleaning audits and act on the findings?',
      'How effectively are employees involved in and aware of their responsibility for a clean, organised workplace?'],
  p3:['How thoroughly does your enterprise identify workplace safety risks and take steps to reduce or eliminate them?',
      'How consistently do all workers — including contract workers — use required Personal Protective Equipment (PPE)?',
      'How regularly and systematically is safety training provided, and how well are training records maintained?',
      'How effectively does your enterprise record and investigate accidents, incidents and near-misses with root cause and corrective action?',
      'How frequently are safety mock drills conducted and how well are fire equipment and emergency exits maintained?'],
  p4:['How systematically does your enterprise record each order\'s expected delivery date alongside the actual dispatch date?',
      'How regularly does your enterprise track whether deliveries are made on time and in full (OTIF)?',
      'When a delivery is delayed, how consistently does your enterprise identify the cause and take steps to prevent recurrence?',
      'How formally does senior management review delivery performance data and make decisions based on it?',
      'To what extent does your enterprise proactively inform customers about expected delays before the due date?'],
  p5:['How clearly are your product quality requirements — dimensions, finish, accepted tolerances — documented and used on the shop floor?',
      'How thoroughly are raw materials, in-process production and finished goods inspected, with results recorded?',
      'How regularly are employees trained on quality requirements, inspection methods, and handling defects?',
      'How consistently does your enterprise conduct quality audits and follow through on corrective and preventive actions?',
      'How actively does senior management review quality performance data — defect rates, complaints, rejection figures — to drive improvement?'],
  p6:['How formally has your enterprise established processes for hiring, onboarding and maintaining employee records?',
      'To what extent does each employee have an individual development or training plan linked to their role?',
      'How comprehensively does your enterprise map employee skills — technical, safety awareness, energy conservation — and address gaps through training?',
      'How regularly are employee training plans reviewed and updated based on actual completion and business needs?',
      'How actively does your enterprise measure employee engagement, gather feedback, and take action on it?'],
  p7:['How clearly are daily production quality, cost and delivery targets linked to longer-term business goals and communicated at shift start?',
      'How systematically is actual versus target QCD performance tracked and made visible to all workers?',
      'When daily targets are not met, how promptly and consistently does your team identify the root cause and implement a corrective action?',
      'How effectively does your enterprise use daily operations data to identify trends and improve performance over time?',
      'How regularly is the effectiveness of your daily management system reviewed by senior leadership?'],
  p8:['How comprehensively and consistently does your enterprise follow a preventive maintenance schedule for all critical machines?',
      'How regularly are measuring instruments calibrated and how well are calibration records and due dates maintained?',
      'When equipment breaks down, how systematically does your enterprise identify the root cause and prevent the same breakdown recurring?',
      'To what extent does your enterprise track equipment downtime and use this data to prioritise maintenance improvements?',
      'How effectively does maintenance performance — breakdown frequency and calibration status — get reviewed in management meetings?'],
  p9:['How thoroughly are Standard Operating Procedures (SOPs) written for critical processes, and how consistently are workers trained on them?',
      'How systematically does your enterprise plan and define process parameters before production begins for each product?',
      'How regularly are critical process parameters monitored and recorded during production to detect deviations early?',
      'When a process deviation occurs, how consistently does your team identify the root cause and implement a corrective action?',
      'How frequently are your process control systems reviewed for effectiveness and used to update SOPs?'],
  p10:['How completely has your enterprise identified all mandatory testing, certification or licensing requirements for your products?',
       'How consistently are your products tested — in-house or at an accredited lab — against applicable standards before dispatch?',
       'How systematically are product non-conformances recorded, investigated by root cause, and resolved with corrective actions?',
       'How current and complete are all your mandatory product certifications, and how proactively are renewals managed?',
       'How regularly does senior management review product quality and safety performance data?'],
  p11:['How systematically does your enterprise plan raw material procurement based on production schedules, shelf life and storage conditions?',
       'How well does your enterprise maintain optimum inventory levels — avoiding both shortages and excess stock?',
       'How consistently are raw materials, in-process goods and finished goods identified, stored safely and handled per documented procedures?',
       'How reliably does your enterprise inspect incoming raw materials and components for quality before they enter production?',
       'How regularly is the effectiveness of your material management reviewed — analysing wastage, stock accuracy or shortage frequency?'],
  p12:['How clearly has your enterprise identified all energy sources and set targets for reducing consumption per unit of production?',
       'How regularly does your enterprise record and compare actual energy consumption against targets, and take corrective actions for excess use?',
       'How thoroughly have employees been trained to understand their role in saving energy in their daily work?',
       'How systematically does your enterprise conduct periodic energy reviews or audits to identify the biggest savings opportunities?',
       'How effectively does your enterprise implement identified energy-saving actions and track the resulting improvements?'],
  p13:['How comprehensively does your enterprise identify all applicable environmental regulations — PCB consents, waste disposal, emission standards — and maintain compliance?',
       'How consistently does your enterprise segregate, label and dispose of different waste types through authorised channels?',
       'How regularly does your enterprise monitor emissions and compare results against applicable regulatory limits?',
       'How systematically does your enterprise conduct environmental audits, act on findings, and verify corrective actions are effective?',
       'How thoroughly are employees trained on their responsibility for waste management, spill prevention and environmental compliance?'],
  p14:['How regularly and thoroughly does senior management review key quality data — defect rates, rework, rejection costs, customer complaints?',
       'How well does your enterprise calculate and track the Cost of Poor Quality (COPQ) to understand its financial impact?',
       'How consistently does your enterprise measure customer satisfaction and use findings to drive improvement?',
       'When quality metrics fall below target, how systematically does your enterprise conduct root cause analysis and implement corrective actions?',
       'How effectively are quality measurement trends communicated across the organisation to promote learning and improvement?'],
  p15:['How formally does your enterprise select, evaluate and periodically re-evaluate suppliers based on quality, delivery and reliability?',
       'To what extent does your enterprise work with suppliers to promote better energy efficiency, waste reduction and responsible resource use?',
       'How consistently does your enterprise monitor supplier performance and use this data to improve supply chain reliability?',
       'How effectively does your enterprise develop weaker suppliers through guidance or shared requirements rather than replacing them?',
       'How proactively does your enterprise review supply chain risks and plan contingencies for critical supplier failure?'],
  p16:['How comprehensively has your enterprise identified key risks — operational, financial, market, regulatory and environmental?',
       'How formally does your enterprise assess each identified risk in terms of likelihood and potential impact?',
       'How effectively has your enterprise defined specific mitigation actions for high-priority risks with owners and timelines?',
       'How regularly does senior management review the risk register and identify any new risks that have emerged?',
       'How well are employees made aware of key risks in their area and their personal role in managing those risks?'],
  p17:['How thoroughly has your enterprise identified and documented the 7 types of waste (overproduction, defects, waiting, transport, inventory, motion, over-processing) in production?',
       'How clearly defined and actively tracked are your waste reduction targets — for example reducing material scrap by a specific percentage?',
       'How well trained are employees in understanding and identifying Muda (waste), Mura (unevenness) and Muri (overburden)?',
       'How consistently does your enterprise monitor waste reduction performance and review progress in management meetings?',
       'How effectively has your enterprise applied lean tools — 5S, Kaizen, visual management — to reduce waste and sustain improvements?'],
  p18:['How proactively does your enterprise evaluate and adopt new technologies based on product quality needs, customer requirements and regulatory changes?',
       'To what extent has your enterprise explored or adopted digital tools — ERP, digital tracking, IoT sensors — to improve efficiency?',
       'How formally does your enterprise plan technology upgrades with a budget, timeline and expected business benefit defined before investment?',
       'How effectively does your enterprise evaluate a technology\'s environmental impact as part of the selection decision?',
       'How systematically does your enterprise review the results of technology investments to verify whether expected improvements were achieved?'],
  p19:['How systematically does your enterprise measure and track consumption of key natural resources — water, fuel, raw materials — per unit of production?',
       'To what extent does your enterprise take steps to reduce dependence on non-renewable resources and adopt renewable alternatives?',
       'How well trained are employees on natural resource conservation practices relevant to their role?',
       'How formally does your enterprise set resource conservation targets and track progress against them?',
       'How effectively does your enterprise share resource conservation progress with customers, suppliers or the community?'],
  p20:['How clearly has your enterprise defined a CSR policy covering fair business practices, employee welfare, environmental responsibility and community engagement?',
       'How specifically are CSR actions planned with defined activities, responsible persons, timelines and budgets?',
       'How consistently does your enterprise demonstrate fair operating practices — timely wages, equal opportunity, compliance with labour laws?',
       'How actively does your enterprise engage with the local community through skill development, health, environment or educational initiatives?',
       'How regularly does senior management review CSR activities and assess their actual impact on employees, community and environment?'],
};

// ── RATING ─────────────────────────────────────────────────────
const LBLS   = ['Excellent','Good','Fair','Poor','Not Aware'];
const CSS    = ['f5','f4','f3','f2','f1'];
const FB_MSG = [
  '✅ Best practice fully implemented. Document and sustain this.',
  '👍 Good progress. Close small gaps to reach Excellent.',
  '⚠️ Some practices in place — consistency and documentation need work.',
  '📌 Best practices are not yet followed here. This is a priority improvement area.',
  '💡 This is a new area. Free handholding support is available from MoMSME to help you get started.',
];

// ── NIC SECTOR GUIDE ───────────────────────────────────────────
const NIC_GUIDE = {
  '10':{nm:'Food Products',top:'P5 Quality, P13 Environment, P2 Swachh Workplace',gap:'No FSSAI licence; organic waste disposal issues; no HACCP',qw:'Get FSSAI; 5S in production area; segregate organic waste'},
  '11':{nm:'Beverages',top:'P12 Energy, P13 Environment, P11 Material',gap:'High water use per litre; plastic waste; no effluent treatment',qw:'Meter water per 1000L produced; segregate plastic; get PCB NOC'},
  '12':{nm:'Tobacco',top:'P3 Safety, P13 Environment, P5 Quality',gap:'Nicotine dust without PPE; tobacco waste disposal; licence gaps',qw:'N95 masks; tobacco licence; waste manifest for disposal'},
  '13':{nm:'Textiles',top:'P13 Environment, P12 Energy, P9 Process',gap:'Dyeing effluent untreated; high electricity in dyeing; no defect tracking',qw:'CETP/ETP connection; electricity per metre; defect tally per shift'},
  '14':{nm:'Wearing Apparel',top:'P5 Quality, P4 Delivery, P9 Process',gap:'No AQL inspection; no delivery tracking; no stitching SOPs',qw:'AQL sampling table; delivery register; stitching SOPs'},
  '15':{nm:'Leather Products',top:'P13 Environment, P3 Safety, P12 Energy',gap:'Chrome effluent; no SDS for chemicals; no PPE for tannery workers',qw:'ETP connection; SDS for all chemicals; gloves/aprons/boots mandatory'},
  '16':{nm:'Wood & Cork',top:'P3 Safety, P12 Energy, P2 Swachh Workplace',gap:'Wood dust explosion risk; unguarded circular saws; kiln energy waste',qw:'Dust extraction units; machine guards; 5S sawdust; meter kiln energy'},
  '17':{nm:'Paper Products',top:'P12 Energy, P13 Environment, P11 Material',gap:'Very high energy in paper machine; chemical effluent from pulping; water waste',qw:'Energy audit; effluent treatment before discharge; water recycling'},
  '18':{nm:'Printing',top:'P13 Environment, P5 Quality, P2 Swachh Workplace',gap:'Solvent/ink waste disposal; VOC emissions; no colour quality control',qw:'Solvent waste manifest; 5S press area; colour measurement tools'},
  '19':{nm:'Petroleum & Coke',top:'P3 Safety, P13 Environment, P16 Risk',gap:'PESO compliance gaps; hydrocarbon emission monitoring; hazardous waste',qw:'Engage PESO consultant; gas detectors; waste manifest'},
  '20':{nm:'Chemicals',top:'P13 Environment, P3 Safety, P10 Product Quality',gap:'No SDS/MSDS; incompatible chemical storage; effluent treatment gaps',qw:'SDS for all chemicals; segregated storage; CETP connection'},
  '21':{nm:'Pharmaceuticals',top:'P5 Quality, P9 Process, P13 Environment',gap:'GMP non-compliance; API effluent; incomplete batch manufacturing records',qw:'GMP self-assessment vs Schedule M; ETP for API effluent; complete BMRs'},
  '22':{nm:'Rubber & Plastics',top:'P12 Energy, P13 Environment, P5 Quality',gap:'High moulding energy; plastic waste; no dimensional control',qw:'Energy metering per press; regrind policy; go/no-go gauges'},
  '23':{nm:'Non-Metallic Minerals',top:'P3 Safety, P12 Energy, P13 Environment',gap:'Silica dust without respirators; high kiln energy; no SPM monitoring',qw:'Dust enclosures; respirators; kiln energy audit; SPM measurement'},
  '24':{nm:'Basic Metals',top:'P12 Energy, P13 Environment, P3 Safety',gap:'High furnace energy; slag disposal without manifest; no mechanical testing',qw:'Furnace efficiency assessment; slag manifest; BIS tensile/hardness tests'},
  '25':{nm:'Fabricated Metal',top:'P5 Quality, P2 Swachh Workplace, P9 Process',gap:'Dimensional rejections; cluttered machine shop; no drawing-based inspection',qw:'Drawing-based inspection checklist; 5S machine shop; calibrate micrometers'},
  '26':{nm:'Electronics',top:'P10 Quality, P8 Maintenance, P13 Environment',gap:'No incoming component inspection; ESD control absent; e-waste without authorisation',qw:'Component AQL incoming; ESD mats and wristbands; e-waste recycler tie-up'},
  '27':{nm:'Electrical Equipment',top:'P10 Quality, P12 Energy, P3 Safety',gap:'No hi-pot/IR testing; copper scrap loss; BEE star rating gaps',qw:'Hi-pot and IR testing SOP; copper scrap tracking; BEE star rating review'},
  '28':{nm:'Machinery',top:'P5 Quality, P4 Delivery, P8 Maintenance',gap:'No acceptance test procedure; delivery delays; no calibration of test instruments',qw:'Machine acceptance test checklist; delivery tracking board; calibrate gauges'},
  '29':{nm:'Motor Vehicles & Auto',top:'P5 Quality, P9 Process, P17 Lean',gap:'PPAP documentation gaps; high scrap; OEE not tracked',qw:'PPAP training; scrap reduction Kaizen; OEE measurement on key machines'},
  '30':{nm:'Other Transport',top:'P3 Safety, P5 Quality, P13 Environment',gap:'No weld procedure qualification; no PPE for welders; paint/VOC emissions',qw:'WPS/PQR for welding; PPE kit for welders; VOC emission compliance'},
  '31':{nm:'Furniture',top:'P5 Quality, P2 Swachh Workplace, P4 Delivery',gap:'Finish quality complaints; cluttered finishing area; no delivery commitment tracking',qw:'5S finishing area; final inspection checklist; delivery promise register'},
  '32':{nm:'Other Manufacturing',top:'P5 Quality, P10 Product Quality, P3 Safety',gap:'BIS/IS mark not obtained; cluttered production; no product safety testing',qw:'Check applicable BIS standards; 5S workbench; product testing plan'},
  '33':{nm:'Repair & Installation',top:'P3 Safety, P5 Quality, P4 Delivery',gap:'No service SOPs; unsafe on-site work; no service call records',qw:'Service SOPs per equipment type; PPE for field team; service call register'},
};

const NIC_PRIORITY = {
  '10':['p5','p13','p2'], '11':['p12','p13','p11'], '12':['p3','p13','p5'],
  '13':['p13','p12','p9'],'14':['p5','p4','p9'],    '15':['p13','p3','p12'],
  '16':['p3','p12','p2'], '17':['p12','p13','p11'],  '18':['p13','p5','p2'],
  '19':['p3','p13','p16'],'20':['p13','p3','p10'],   '21':['p5','p9','p13'],
  '22':['p12','p13','p5'],'23':['p3','p12','p13'],   '24':['p12','p13','p3'],
  '25':['p5','p2','p9'],  '26':['p10','p8','p13'],   '27':['p10','p12','p3'],
  '28':['p5','p4','p8'],  '29':['p5','p9','p17'],    '30':['p3','p5','p13'],
  '31':['p5','p2','p4'],  '32':['p5','p10','p3'],    '33':['p3','p5','p4'],
};

const ISO_CERTS = [
  {id:'iso9001',  label:'ISO 9001 — exempts P5 (Quality Management)'},
  {id:'iatf',     label:'IATF 16949 — exempts P5, P9 (for auto sector)'},
  {id:'iso14001', label:'ISO 14001 — exempts P13 (Environment)'},
  {id:'iso45001', label:'ISO 45001 — exempts P3 (Occupational Safety)'},
  {id:'iso50001', label:'ISO 50001 — exempts P12 (Energy Management)'},
  {id:'whogmp',   label:'WHO-GMP — exempts P5, P9, P10 (for pharma)'},
  {id:'lean',     label:'MSME Lean Cert — exempts P17 (Waste/Lean)'},
];
const ISO_EXEMPT = {
  iso9001:['p5'], iatf:['p5','p9'], iso14001:['p13'],
  iso45001:['p3'], iso50001:['p12'], whogmp:['p5','p9','p10'], lean:['p17'],
};

const CQ_CHIPS = ['What is ZED certification?','How to get Bronze?','80% subsidy — how?','Documents needed?','ISO 9001 benefit?'];
const CQ_QUICK = ['How to apply for Bronze?','What subsidy do I get?','ZED Pledge process?','Which params for Silver?'];
const FC_QUICK = ['How to fix my biggest gap?','What evidence do I need?','Next steps for Bronze?','When can I apply?'];
const GOAL_LABELS = {Bronze:'🥉 Bronze (5 params)',Silver:'🥈 Silver (14 params)',Gold:'🥇 Gold (20 params)',Guidance:'🧭 Guidance Mode'};

// Misc translatable phrases used in dynamic UI
const MISC = [
  '← Best practice in place','Not yet aware →','answered','Goal:',
  'Priority parameter for this sector','Quick win:',
  'Get My Readiness Score & Roadmap →','Analysing your responses…',
  'Please enter your enterprise name.','Please select your NIC sector.','Please select your certification goal.',
  'Ask about ZED certification…','Ask about your results…','e.g. Sharma Textiles Pvt Ltd',
  'Enter to send · Ctrl+Enter for new line','Listening…','Voice not supported in this browser',
  'No speech detected — please try again','Microphone permission denied — allow mic access in your browser',
  'No microphone found','Speech recognition needs an internet connection','Voice output not supported in this browser',
  'Translating page…','Translation needs the backend server — showing English','Translated ✓',
  "I've reviewed your responses. Ask me anything — how to address a specific gap, what evidence to prepare, or what your next steps should be.",
];

// ══════════════════════════════════════════════════════════════
//  I18N — FULL PAGE TRANSLATION
// ══════════════════════════════════════════════════════════════
let TR_MAP = {};   // english -> translated (empty = English)

function T(s){ return (lang!=='English' && TR_MAP[s]) ? TR_MAP[s] : s; }

// Static elements whose textContent gets translated (id -> captured original)
const STATIC_IDS = ['tabChat','tabAssess','wTitle','wDesc','wc1t','wc1d','wc2t','wc2d','wc3t','wc3d',
  'suTitle','lblName','lblSector','lblSectorHint','lblType','lblGoal','lblIso','lblIsoHint',
  'siSuffix','siL1','siL2','siL3',
  'cgBt','cgBd','cgSt','cgSd','cgGt','cgGd','cgUt','cgUd','startBtn',
  'rhParams','rhStr','rhGaps','rhGapsHint','rhRoad','fcHdr','fcIntro','reassessBtn',
  'lsB','lsS','lsG','chatHint','stext'];
const ORIG = {};          // id -> original english text
let OPT_REFS = [];        // [{el, orig}] for <option> and <optgroup>

function captureOriginals(){
  STATIC_IDS.forEach(id=>{
    const el=document.getElementById(id);
    if(el) ORIG[id]=el.textContent.trim();
  });
  OPT_REFS=[];
  document.querySelectorAll('#entSector option, #entSector optgroup, #entType option').forEach(el=>{
    const orig = el.tagName==='OPTGROUP' ? el.label : el.textContent;
    if(orig && orig.trim() && orig.trim()!=='') OPT_REFS.push({el, orig: orig.trim()});
  });
}

function collectStrings(){
  const set=new Set();
  Object.values(ORIG).forEach(s=>s&&set.add(s));
  OPT_REFS.forEach(o=>set.add(o.orig));
  ALL_PARAMS.forEach(p=>{set.add(p.name);set.add(p.note);});
  Object.values(QUESTIONS).forEach(qs=>qs.forEach(q=>set.add(q)));
  LBLS.forEach(s=>set.add(s));
  FB_MSG.forEach(s=>set.add(s));
  CQ_CHIPS.forEach(s=>set.add(s));
  CQ_QUICK.forEach(s=>set.add(s));
  FC_QUICK.forEach(s=>set.add(s));
  Object.values(GOAL_LABELS).forEach(s=>set.add(s));
  ISO_CERTS.forEach(c=>set.add(c.label));
  Object.values(NIC_GUIDE).forEach(g=>{set.add(g.nm);set.add(g.top);set.add(g.gap);set.add(g.qw);set.add(g.qw.split(';')[0].trim());});
  MISC.forEach(s=>set.add(s));
  return [...set];
}

async function loadTranslations(language){
  // cached?
  try{
    const c=localStorage.getItem('zed_tr_'+language);
    if(c){TR_MAP=JSON.parse(c);applyAll();showToast(T('Translated ✓'));return;}
  }catch(e){}

  const texts=collectStrings();
  showToast('🌐 '+language+' — Translating page…',true);
  try{
    const r=await fetch(`${API}/translate`,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({texts,target_language:language}),
      signal:AbortSignal.timeout(180000)});
    if(!r.ok)throw new Error(r.status);
    const d=await r.json();
    if(!d.translated)throw new Error('backend offline');
    TR_MAP={};
    texts.forEach((t,i)=>{TR_MAP[t]=(d.translations&&d.translations[i])||t;});
    try{localStorage.setItem('zed_tr_'+language,JSON.stringify(TR_MAP));}catch(e){}
    hideToast();applyAll();showToast(T('Translated ✓'));
  }catch(e){
    hideToast();TR_MAP={};
    applyAll();
    showToast('⚠️ '+T('Translation needs the backend server — showing English'));
  }
}

function applyAll(){
  document.documentElement.dir = lang==='Urdu' ? 'rtl' : 'ltr';
  // static elements
  STATIC_IDS.forEach(id=>{
    const el=document.getElementById(id);
    if(el && ORIG[id]!==undefined) el.textContent=T(ORIG[id]);
  });
  // dropdown options
  OPT_REFS.forEach(({el,orig})=>{
    if(el.tagName==='OPTGROUP') el.label=T(orig);
    else if(el.value!=='') el.textContent=T(orig);
  });
  // placeholders
  const ci=document.getElementById('chatIn'); if(ci)ci.placeholder=T('Ask about ZED certification…');
  const fi=document.getElementById('fcIn');   if(fi)fi.placeholder=T('Ask about your results…');
  const en=document.getElementById('entName');if(en)en.placeholder=T('e.g. Sharma Textiles Pvt Ltd');
  // chips
  buildChips();
  // ISO grid (preserve checked state)
  const checked=new Set([...document.querySelectorAll('.iso-item input:checked')].map(i=>i.value));
  const ig=document.getElementById('isoGrid');
  if(ig){ig.innerHTML=ISO_CERTS.map(c=>`<label class="iso-item${checked.has(c.id)?' checked':''}" onclick="this.classList.toggle('checked')"><input type="checkbox" value="${c.id}" ${checked.has(c.id)?'checked':''}> ${T(c.label)}</label>`).join('');}
  // sector insight (if visible)
  onSectorChange();
  // re-render questions if user is mid-assessment
  const qs=document.getElementById('questionsStep');
  if(qs && qs.style.display!=='none' && window._buildArgs){
    buildQuestions(window._buildArgs.params, window._buildArgs.nic, window._buildArgs.goal);
    restoreAnswers();
  }
}

function restoreAnswers(){
  Object.keys(answers).forEach(pid=>{
    Object.entries(answers[pid]).forEach(([qi,score])=>{
      const inp=document.querySelector(`input[name="${pid}_q${qi}"][value="${score}"]`);
      if(inp){inp.checked=true;setFeedback(pid,qi,score);}
    });
    updParamScore(pid);
  });
  updProgress();
}

// ── INIT ───────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded',()=>{
  captureOriginals();
  checkStatus();
  buildChips();
  document.getElementById('isoGrid').innerHTML = ISO_CERTS.map(c=>`<label class="iso-item" onclick="this.classList.toggle('checked')"><input type="checkbox" value="${c.id}"> ${c.label}</label>`).join('');
  document.getElementById('chatIn').addEventListener('input',updChatBtn);
  ALL_PARAMS.forEach(p=>{ answers[p.id]={}; });
  // warm TTS voices (Chrome loads them async)
  if('speechSynthesis' in window){speechSynthesis.getVoices();speechSynthesis.onvoiceschanged=()=>speechSynthesis.getVoices();}
});

function buildChips(){
  const cc=document.getElementById('chatChips');
  if(cc)cc.innerHTML = CQ_CHIPS.map(q=>`<button class="chip" onclick="chatSendTxt('${e2(T(q))}')">${T(q)}</button>`).join('');
  const cq=document.getElementById('chatQuick');
  if(cq)cq.innerHTML = CQ_QUICK.map(q=>`<button class="qchip" onclick="chatSendTxt('${e2(T(q))}')">${T(q)}</button>`).join('');
  const fq=document.getElementById('fcQuick');
  if(fq)fq.innerHTML = FC_QUICK.map(q=>`<button class="qchip" onclick="fcSendTxt('${e2(T(q))}')" style="font-size:11px">${T(q)}</button>`).join('');
}

function updChatBtn(){
  const h=document.getElementById('chatIn').value.trim()!==''||chatFile;
  document.getElementById('chatSend').disabled=!h||chatBusy;
}

// ── TAB ────────────────────────────────────────────────────────
function switchTab(n,btn){
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('panel-'+n).classList.add('active');
}

// ── LANGUAGE ───────────────────────────────────────────────────
function setLang(v){
  lang=v;
  stopSpeak();
  if(v==='English'){TR_MAP={};applyAll();return;}
  loadTranslations(v);
}

// ── STATUS ─────────────────────────────────────────────────────
async function checkStatus(){
  try{
    const r=await fetch(`${API}/health`,{signal:AbortSignal.timeout(6000)});
    const d=await r.json();
    document.getElementById('sdot').style.background='#4ade80';
    document.getElementById('stext').textContent=d.rag_loaded?'AI + RAG ready':'AI connected';
  }catch{
    document.getElementById('sdot').style.background='#f87171';
    document.getElementById('stext').textContent='offline';
  }
  updChatBtn();
}

// ── SECTOR CHANGE ──────────────────────────────────────────────
function onSectorChange(){
  const nic=document.getElementById('entSector').value;
  const box=document.getElementById('sectorInsight');
  if(!nic||!NIC_GUIDE[nic]){if(box)box.style.display='none';return;}
  const g=NIC_GUIDE[nic];
  document.getElementById('siSectorName').textContent=T(g.nm);
  document.getElementById('siTop').textContent=T(g.top);
  document.getElementById('siGap').textContent=T(g.gap);
  document.getElementById('siQw').textContent=T(g.qw);
  box.style.display='block';
}

// ── START ASSESSMENT ───────────────────────────────────────────
function startAssessment(){
  const name=document.getElementById('entName').value.trim();
  const nic=document.getElementById('entSector').value;
  const goalEl=document.querySelector('input[name="certGoal"]:checked');
  if(!name){alert(T('Please enter your enterprise name.'));return;}
  if(!nic){alert(T('Please select your NIC sector.'));return;}
  if(!goalEl){alert(T('Please select your certification goal.'));return;}

  const goal=goalEl.value;
  ALL_PARAMS.forEach(p=>{answers[p.id]={};});

  const isoCerts=[...document.querySelectorAll('.iso-item input:checked')].map(i=>i.value);
  const exempted=new Set();
  isoCerts.forEach(c=>{ (ISO_EXEMPT[c]||[]).forEach(p=>exempted.add(p)); });

  let paramsToShow = goal==='Guidance'
    ? ALL_PARAMS.filter(p=>p.level==='Bronze')
    : LEVEL_PARAMS[goal] || LEVEL_PARAMS.Bronze;
  paramsToShow = paramsToShow.filter(p=>!exempted.has(p.id));

  window._assessState = { name, nic, goal, isoCerts, paramsToShow };
  buildQuestions(paramsToShow, nic, goal);

  document.getElementById('setupStep').style.display='none';
  document.getElementById('questionsStep').style.display='block';
  document.getElementById('assessWrap').scrollTop=0;
}

// ── BUILD QUESTION UI ──────────────────────────────────────────
function buildQuestions(params, nic, goal){
  window._buildArgs = {params, nic, goal};
  const container=document.getElementById('questionsStep');
  const priority=NIC_PRIORITY[nic]||[];
  const totalQ=params.length*5;

  let html=`
    <div class="prog-wrap" id="progWrap">
      <div class="prog-bar"><div class="prog-fill" id="progFill" style="width:0%"></div></div>
      <div class="prog-meta">
        <span class="prog-txt" id="progTxt">0 / ${totalQ} ${T('answered')}</span>
        <span class="prog-cert">${T('Goal:')} ${T(GOAL_LABELS[goal]||goal)}</span>
      </div>
    </div>`;

  params.forEach((p,pi)=>{
    const isPriority=priority.includes(p.id);
    const g=NIC_GUIDE[nic];
    const tip=isPriority&&g?`⭐ ${T('Priority parameter for this sector')} — ${T('Quick win:')} ${T(g.qw.split(';')[0].trim())}.`:'';
    const qs=QUESTIONS[p.id]||[];

    html+=`<div class="pcard" id="pc_${p.id}">
      <div class="pcard-hdr">
        <span class="pcard-icon">${p.icon}</span>
        <span class="pcard-name">${isPriority?'⭐ ':''}${T(p.name)}</span>
        <span class="pcard-score" id="psc_${p.id}"></span>
      </div>
      ${tip?`<div class="pcard-tip">${tip}</div>`:''}`;

    qs.forEach((q,qi)=>{
      const nm=`${p.id}_q${qi}`;
      const qNum=pi*5+qi+1;
      const pills=LBLS.map((lb,ri)=>{
        const score=5-ri;
        return `<label class="ropt r${score}"><input type="radio" name="${nm}" value="${score}" onchange="onAns('${p.id}',${qi},${score})"><div class="rpill"><div class="rdot"></div><div class="rpill-lbl">${T(lb)}</div></div></label>`;
      }).join('');

      html+=`<div class="qblock" id="qb_${p.id}_${qi}">
        <div class="qnum">Q${qNum} <button class="q-spk" onclick="speakQ('${p.id}',${qi})" title="🔊">🔊</button></div>
        <div class="qtext" id="qt_${p.id}_${qi}">${T(q)}</div>
        <div class="scale-hint"><span>${T('← Best practice in place')}</span><span>${T('Not yet aware →')}</span></div>
        <div class="rrow">${pills}</div>
        <div class="qfb" id="qf_${p.id}_${qi}"></div>
      </div>`;
    });

    html+=`</div>`;
  });

  html+=`<div class="submit-area">
    <button class="submit-btn" id="aSubmit" onclick="doSubmit()">${T('Get My Readiness Score & Roadmap →')}</button>
  </div>`;

  container.innerHTML=html;
  window._totalQ=totalQ;
}

// ── ANSWER HANDLER ─────────────────────────────────────────────
function setFeedback(pid,qi,score){
  const ri=5-score;
  const fb=document.getElementById(`qf_${pid}_${qi}`);
  if(!fb)return;
  const prefix=['✅','👍','⚠️','📌','💡'][ri];
  const msg=T(FB_MSG[ri]).replace(/^([✅👍⚠️📌💡]\s*)/,'');
  fb.innerHTML=`<span style="flex-shrink:0;font-size:14px">${prefix}</span><span>${msg}</span>`;
  fb.className=`qfb show ${CSS[ri]}`;
}
function onAns(pid,qi,score){
  answers[pid][qi]=score;
  setFeedback(pid,qi,score);
  updParamScore(pid);
  updProgress();
}

function updParamScore(pid){
  const ans=answers[pid];const filled=Object.keys(ans).length;if(!filled)return;
  const pct=Math.round(Object.values(ans).reduce((s,v)=>s+v,0)/(filled*5)*100);
  const el=document.getElementById(`psc_${pid}`);
  if(el){
    const col=pct>=70?'#1b5e20':pct>=50?'#e65100':'#c62828';
    const bg=pct>=70?'#e8f5e9':pct>=50?'#fff3e0':'#ffebee';
    el.textContent=`${pct}%`;el.style.color=col;el.style.background=bg;
  }
}

function updProgress(){
  const total=window._totalQ||100;
  let answered=0;
  ALL_PARAMS.forEach(p=>{answered+=Object.keys(answers[p.id]).length;});
  const pct=Math.round(answered/total*100);
  const el=document.getElementById('progFill');
  if(el)el.style.width=pct+'%';
  const txt=document.getElementById('progTxt');
  if(txt)txt.textContent=`${answered} / ${total} ${T('answered')} (${pct}%)`;
}

// ── SUBMIT ─────────────────────────────────────────────────────
async function doSubmit(){
  const {name,nic,goal,isoCerts,paramsToShow}=window._assessState||{};
  const btn=document.getElementById('aSubmit');
  btn.disabled=true;btn.textContent=T('Analysing your responses…');

  try{
    const r=await fetch(`${API}/assessment`,{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({enterprise_name:name,nic_code:nic,enterprise_type:document.getElementById('entType').value,
        cert_goal:goal,answers,iso_certifications:isoCerts,language:lang}),
      signal:AbortSignal.timeout(45000)
    });
    if(!r.ok) throw new Error(r.status);
    showResult(await r.json(), paramsToShow);
  }catch{
    showResult(buildFallback(nic, document.getElementById('entType').value, paramsToShow), paramsToShow);
  }
  btn.disabled=false;btn.textContent=T('Get My Readiness Score & Roadmap →');
}

function buildFallback(nic,type,paramsToShow){
  let tRaw=0,tMax=0;const pScores={};
  const bronzeIds=['p1','p2','p3','p4','p5'];
  const silverIds=['p1','p2','p3','p4','p5','p6','p7','p8','p9','p10','p11','p12','p13','p14'];
  paramsToShow.forEach(p=>{
    const ans=answers[p.id];const ks=Object.keys(ans);
    if(!ks.length){pScores[p.id]={name:p.name,level:p.level,pct:0,answered:0};return;}
    const raw=Object.values(ans).reduce((s,v)=>s+v,0);const mx=ks.length*5;
    const pct=Math.round(raw/mx*100);pScores[p.id]={name:p.name,level:p.level,pct,answered:ks.length};
    tRaw+=raw;tMax+=mx;
  });
  const overall=tMax>0?Math.round(tRaw/tMax*100):0;
  const bIds=paramsToShow.filter(p=>bronzeIds.includes(p.id)).map(p=>p.id);
  const sIds=paramsToShow.filter(p=>silverIds.includes(p.id)).map(p=>p.id);
  const lvlScore=(ids)=>{let r=0,m=0;ids.forEach(id=>{const pr=pScores[id];if(pr&&pr.answered>0){r+=pr.pct*pr.answered*5/100;m+=pr.answered*5;}});return m>0?Math.round(r/m*100):0;};
  const bScore=lvlScore(bIds),sScore=lvlScore(sIds),gScore=lvlScore(Object.keys(pScores));
  const bE=bScore>=50,sE=sScore>=55&&bE,gE=gScore>=60&&sE;
  let lbl,note;
  const goal = window._assessState?.goal || 'Advise';
  
  if (goal === 'Bronze') {
    lbl = bE ? 'Bronze Level Ready 🥉' : 'Building Foundations';
    note = bE ? `Good start. Bronze score: ${bScore}%.` : `Focus on the 5 Bronze parameters first. Bronze score: ${bScore}%.`;
  } else if (goal === 'Silver') {
    lbl = sE ? 'Silver Level Ready 🥈' : (bE ? 'Bronze Level Ready 🥉' : 'Building Foundations');
    note = sE ? `Strong foundation. Silver score: ${sScore}%.` : `Needs improvement for Silver.`;
  } else {
    if(gE){lbl='Gold Level Ready 🥇';note=`Outstanding — all parameters strong. Gold score: ${gScore}%.`;}
    else if(sE){lbl='Silver Level Ready 🥈';note=`Strong foundation. Silver score: ${sScore}%. Build P15–P20 for Gold.`;}
    else if(bE){lbl='Bronze Level Ready 🥉';note=`Good start. Bronze score: ${bScore}%. Build P6–P14 for Silver.`;}
    else{lbl='Building Foundations';note=`Focus on the 5 Bronze parameters first. Bronze score: ${bScore}%.`;}
  }
  const sub={Micro:{Bronze:'80% subsidy — net cost ~₹2,000',Silver:'60% subsidy — net cost ~₹16,000',Gold:'50% subsidy — net cost ~₹45,000'},Small:{Bronze:'80% subsidy',Silver:'60% subsidy',Gold:'50% subsidy'},Medium:{Bronze:'80% subsidy',Silver:'60% subsidy',Gold:'50% subsidy'}};
  const certLevel=gE?'Gold':sE?'Silver':bE?'Bronze':'Pre-Bronze';
  const g=NIC_GUIDE[nic]||{};
  const sorted=Object.values(pScores).filter(p=>p.answered>0).sort((a,b)=>b.pct-a.pct);
  const strengths=sorted.filter(p=>p.pct>=70).map(p=>p.name);
  const gaps=sorted.filter(p=>p.pct<50).map(p=>p.name);
  const roadmap=`Your ZED Improvement Roadmap

Week 1–2: Immediate Actions
• Take ZED Pledge at zed.msme.gov.in and link your UDYAM registration
• Engage a ZED Master Trainer (free through MoMSME programme)
${gaps.length?`• Priority gaps to address first: ${gaps.slice(0,3).join(', ')}`:''}

Week 3–4: Documentation & Quick Wins
• Sector focus (${g.nm||'your sector'}): ${g.qw||'Review sector-specific guidance'}
• Prepare objective evidence for your strongest parameters first

Month 2: Apply for Certification
• Submit Bronze self-assessment on ZED portal
• Certification cost: ₹10,000 with 80% subsidy (net ~₹2,000)
• Engage accredited assessment agency for desktop review

Financial Support Available:
• Handholding & Consultancy: up to ₹2,00,000
• Technology Upgradation: up to ₹3,00,000
• Testing & Certification support: 75% subsidy up to ₹50,000`;
  return{score:overall,bronze_score:bScore,silver_score:sScore,gold_score:gScore,readiness:lbl,readiness_note:note,subsidy_eligible:(sub[type]||sub.Micro)[certLevel]||'Take ZED Pledge for ₹10,000 joining reward',bronze_eligible:bE,silver_eligible:sE,gold_eligible:gE,strengths,gaps,param_scores:pScores,roadmap};
}

function showResult(d,paramsToShow){
  document.getElementById('questionsStep').style.display='none';
  const rw=document.getElementById('resultWrap');rw.style.display='block';

  document.getElementById('rScore').textContent=d.score||0;
  document.getElementById('rLabel').textContent=d.readiness||'—';
  document.getElementById('rNote').textContent=d.readiness_note||'—';
  document.getElementById('rSubsidy').textContent=d.subsidy_eligible||'—';
  document.getElementById('rBScore').textContent=(d.bronze_score||0)+'%';
  document.getElementById('rSScore').textContent=(d.silver_score||0)+'%';
  document.getElementById('rGScore').textContent=(d.gold_score||0)+'%';

  const {name,nic,goal}=window._assessState||{};
  document.querySelector('.lsbox.b').style.display = (goal === 'Bronze' || goal === 'Guidance') ? 'block' : 'none';
  document.querySelector('.lsbox.s').style.display = (goal === 'Silver' || goal === 'Guidance') ? 'block' : 'none';
  document.querySelector('.lsbox.g').style.display = (goal === 'Gold' || goal === 'Guidance') ? 'block' : 'none';


  document.getElementById('rPills').innerHTML=['Bronze','Silver','Gold'].map((l,i)=>{
    const ok=[d.bronze_eligible,d.silver_eligible,d.gold_eligible][i];
    return`<span class="cpill ${ok?'yes':'no'}">${ok?'✅':'—'} ${l}</span>`;
  }).join('');

  const bars=document.getElementById('pbarList');bars.innerHTML='';
  (paramsToShow||ALL_PARAMS).forEach(p=>{
    const pr=(d.param_scores||{})[p.id];
    if(!pr||(!pr.answered&&!pr.exempted))return;
    const pct=pr.pct||0;
    const col=pct>=70?'var(--t)':pct>=50?'#ef6c00':'#c62828';
    bars.innerHTML+=`<div class="pbar-row"><div class="pbar-lbl">${p.icon} ${T(p.name)}</div><div class="pbar-track"><div class="pbar-fill" style="width:${pct}%;background:${col}"></div></div><div class="pbar-pct">${pct}%</div></div>`;
  });

  const str=d.strengths||[];const gaps=d.gaps||[];
  const sc=document.getElementById('rStrengthsCard');
  sc.style.display=str.length?'block':'none';
  document.getElementById('rStrengths').innerHTML=str.map(s=>`<span class="tag ok">${T(s)}</span>`).join('');
  const gc=document.getElementById('rGapsCard');
  gc.style.display=gaps.length?'block':'none';
  document.getElementById('rGaps').innerHTML=gaps.map(g=>`<span class="tag gap">${T(g)}</span>`).join('');
  document.getElementById('rRoadmap').textContent=d.roadmap||'—';

  const {name,nic,goal}=window._assessState||{};
  const g2=NIC_GUIDE[nic]||{};
  window._fcContext=`Enterprise: ${name||'MSME'}. Sector: ${g2.nm||nic}. Goal: ${goal}. Score: ${d.score}%. Readiness: ${d.readiness}. Gaps: ${gaps.join(', ')||'none'}. Strengths: ${str.join(', ')||'none'}.`;
  fcHist=[];

  document.getElementById('assessWrap').scrollTop=0;
}

function resetAssess(){
  document.getElementById('resultWrap').style.display='none';
  document.getElementById('questionsStep').style.display='none';
  document.getElementById('questionsStep').innerHTML='';
  document.getElementById('setupStep').style.display='block';
  ALL_PARAMS.forEach(p=>{answers[p.id]={};});
  window._buildArgs=null;
  document.getElementById('assessWrap').scrollTop=0;
  document.querySelectorAll('input[name="certGoal"]').forEach(r=>r.checked=false);
}

// ── FOLLOW-UP CHAT ─────────────────────────────────────────────
function fcKey(e){if(e.key==='Enter'&&!e.shiftKey&&!e.ctrlKey){e.preventDefault();fcSend();}}
async function fcSend(){const box=document.getElementById('fcIn');const q=box.value.trim();if(!q||fcBusy)return;box.value='';rsz(box);await fcSendTxt(q);}
async function fcSendTxt(q){
  if(fcBusy)return;
  addMsg('fcMsgs','user',q);fcHist.push({role:'user',content:q});
  fcBusy=true;document.getElementById('fcSend').disabled=true;showTyping('fcMsgs');
  try{
    const ctx=window._fcContext||'';
    const r=await fetch(`${API}/chat`,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:q,history:fcHist.slice(-4),language:lang,context:ctx}),
      signal:AbortSignal.timeout(30000)});
    if(!r.ok)throw new Error(r.status);
    const d=await r.json();
    rmTyping('fcMsgs');addMsg('fcMsgs','bot',d.reply,d.source);
    fcHist.push({role:'assistant',content:d.reply});
  }catch(e){
    rmTyping('fcMsgs');addErr('fcMsgs',`Cannot reach server: ${e.message}`);
  }
  fcBusy=false;
  document.getElementById('fcSend').disabled=false;
  scrl('fcMsgs');
}

// ── MAIN CHAT ──────────────────────────────────────────────────
function chatKey(e){if(e.key==='Enter'&&!e.shiftKey&&!e.ctrlKey){e.preventDefault();chatSend();}}
async function chatSend(){
  const box=document.getElementById('chatIn');const q=box.value.trim();
  if((!q&&!chatFile)||chatBusy)return;
  box.value='';rsz(box);
  await chatSendTxt(q||(chatFile?`(file: ${chatFile.name})`:''),(chatFile||null));
  chatFile=null;
  document.getElementById('chatFB').style.display='none';
  document.getElementById('chatFI').value='';
}
async function chatSendTxt(q,file=null){
  if(chatBusy)return;rmEl('chatWelcome');
  addMsg('chatMsgs','user',q,null,false,file);chatHist.push({role:'user',content:q});
  chatBusy=true;document.getElementById('chatSend').disabled=true;showTyping('chatMsgs');
  try{
    const r=await fetch(`${API}/chat`,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:q,history:chatHist.slice(-6),language:lang}),
      signal:AbortSignal.timeout(30000)});
    if(!r.ok)throw new Error(r.status);
    const d=await r.json();
    rmTyping('chatMsgs');addMsg('chatMsgs','bot',d.reply,d.source);
    chatHist.push({role:'assistant',content:d.reply});
  }catch(e){
    rmTyping('chatMsgs');addErr('chatMsgs',e.name==='TimeoutError'?'Response timed out.':e.message);
  }
  chatBusy=false;updChatBtn();scrl('chatMsgs');
}

// ── FILE ───────────────────────────────────────────────────────
function hFile(inp){
  const f=inp.files[0];if(!f)return;
  chatFile=f;
  document.getElementById('chatFN').textContent=f.name;
  document.getElementById('chatFB').style.display='inline-flex';
  updChatBtn();
}
function clrFile(){
  chatFile=null;
  document.getElementById('chatFB').style.display='none';
  document.getElementById('chatFI').value='';
  updChatBtn();
}

// ══════════════════════════════════════════════════════════════
//  VOICE — SPEECH-TO-TEXT (input) + TEXT-TO-SPEECH (output)
// ══════════════════════════════════════════════════════════════
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
const LC={English:'en-IN',Hindi:'hi-IN',Bengali:'bn-IN',Telugu:'te-IN',Marathi:'mr-IN',Tamil:'ta-IN',Gujarati:'gu-IN',Kannada:'kn-IN',Malayalam:'ml-IN',Punjabi:'pa-IN',Odia:'or-IN',Urdu:'ur-PK'};
const REC_ERR={
  'no-speech':'No speech detected — please try again',
  'not-allowed':'Microphone permission denied — allow mic access in your browser',
  'service-not-allowed':'Microphone permission denied — allow mic access in your browser',
  'audio-capture':'No microphone found',
  'network':'Speech recognition needs an internet connection',
};

// Speech-to-text: works on any input — pass input id + button id
function togVoice(inputId='chatIn', btnId='chatVB'){
  if(!SR){showToast(T('Voice not supported in this browser'));return;}
  // toggle off if same button active
  if(activeRec){
    const wasSame = activeRecBtn===btnId;
    stopRec();
    if(wasSame)return;
  }
  const rec=new SR();
  rec.lang=LC[lang]||'en-IN';
  rec.interimResults=true;
  rec.continuous=false;
  rec.maxAlternatives=1;
  const inp=document.getElementById(inputId);
  const btn=document.getElementById(btnId);
  rec.onstart=()=>{
    activeRec=rec;activeRecBtn=btnId;
    if(btn){btn.classList.add('rec');btn.textContent='🔴';}
    showToast('🎙️ '+T('Listening…'),true);
  };
  rec.onresult=(e)=>{
    let fin='',inter='';
    for(let j=e.resultIndex;j<e.results.length;j++){
      if(e.results[j].isFinal)fin+=e.results[j][0].transcript;
      else inter+=e.results[j][0].transcript;
    }
    inp.value=(fin||inter).trim();
    rsz(inp);
    if(inputId==='chatIn')updChatBtn();
  };
  rec.onerror=(e)=>{
    const msg=REC_ERR[e.error]||('Voice error: '+e.error);
    showToast('⚠️ '+T(msg));
    stopRec();
  };
  rec.onend=()=>stopRec();
  try{rec.start();}catch(err){showToast('⚠️ '+T('Voice not supported in this browser'));}
}
function stopRec(){
  if(activeRec){try{activeRec.stop();}catch(e){}}
  const btn=activeRecBtn?document.getElementById(activeRecBtn):null;
  if(btn){btn.classList.remove('rec');btn.textContent='🎙️';}
  hideToast();
  activeRec=null;activeRecBtn=null;
}

// Text-to-speech
function speak(text){
  if(!('speechSynthesis' in window)){showToast(T('Voice output not supported in this browser'));return;}
  speechSynthesis.cancel();
  const clean=String(text).replace(/[✅👍⚠️📌💡🥉🥈🥇🧭⭐📄📚✦🔊•]/g,'').replace(/\*\*/g,'').trim();
  if(!clean)return;
  const u=new SpeechSynthesisUtterance(clean);
  const code=LC[lang]||'en-IN';
  u.lang=code;
  const voices=speechSynthesis.getVoices();
  const v=voices.find(x=>x.lang===code)||voices.find(x=>x.lang&&x.lang.startsWith(code.split('-')[0]));
  if(v)u.voice=v;
  u.rate=0.95;u.pitch=1;
  speechSynthesis.speak(u);
}
function stopSpeak(){if('speechSynthesis' in window)speechSynthesis.cancel();}
function speakRow(btn){
  const row=btn.closest('.msg-row');
  const b=row?row.querySelector('.bubble'):null;
  if(b)speak(b.textContent);
}
function speakQ(pid,qi){
  const el=document.getElementById(`qt_${pid}_${qi}`);
  if(el)speak(el.textContent);
}

// ── UI HELPERS ─────────────────────────────────────────────────
function addMsg(cId,role,text,src,isRag=false,file=null){
  const c=document.getElementById(cId);const row=document.createElement('div');row.className=`msg-row ${role}`;
  const icon=role==='user'?'👤':'🏭';let content=fmt(text);
  if(file&&role==='user')content=`📎 <em style="font-size:11px;opacity:.75">${esc(file.name)}</em><br>${content}`;
  const spk=role==='bot'?`<button class="spk-btn" title="🔊" onclick="speakRow(this)">🔊</button>`:'';
  row.innerHTML=`<div class="av">${icon}</div><div class="bubble">${content}</div>${spk}`;
  if(src&&role==='bot'){const w=document.createElement('div');w.style.cssText='display:flex;flex-direction:column;align-items:flex-start';w.appendChild(row);const s=document.createElement('div');s.className='src-tag';s.textContent=src==='groq'?'✦ AI · ZED knowledge base':'📚 ZED guidance';s.style.paddingLeft='36px';w.appendChild(s);c.appendChild(w);}
  else c.appendChild(row);
  scrl(cId);
}
function addErr(cId,m){const c=document.getElementById(cId);const row=document.createElement('div');row.className='msg-row bot';row.innerHTML=`<div class="av">🏭</div><div class="err-bubble">⚠️ ${esc(m)}</div>`;c.appendChild(row);scrl(cId);}
function showTyping(cId){const c=document.getElementById(cId);const el=document.createElement('div');el.className='msg-row bot';el.id=cId+'_t';el.innerHTML=`<div class="av">🏭</div><div class="typing"><div class="td"></div><div class="td"></div><div class="td"></div></div>`;c.appendChild(el);scrl(cId);}
function rmTyping(cId){document.getElementById(cId+'_t')?.remove();}
function rmEl(id){document.getElementById(id)?.remove();}
function scrl(id){const e=document.getElementById(id);if(e)e.scrollTop=e.scrollHeight;}
function rsz(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,100)+'px';}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function e2(s){return s.replace(/\\/g,'\\\\').replace(/'/g,"\\'");}
function fmt(t){let s=esc(t);s=s.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>');s=s.replace(/^[•\-] (.+)$/gm,'<span style="display:block;padding-left:10px">• $1</span>');s=s.replace(/^(\d+)\. (.+)$/gm,'<span style="display:block;padding-left:10px">$1. $2</span>');s=s.replace(/\n/g,'<br>');return s;}
function showToast(m,p=false){const t=document.getElementById('vToast');t.textContent=m;t.classList.add('show');clearTimeout(window._toastT);if(!p)window._toastT=setTimeout(()=>t.classList.remove('show'),2500);}
function hideToast(){document.getElementById('vToast').classList.remove('show');}

