/* NepDate राशिफल भिडियो builder — one source for editor preview, design boards and MP4 render */
(function(g){
const G=["M28 85C8 55 15 15 50 35C85 15 92 55 72 85M50 35V92","M18 18C22 48 78 48 82 18M50 52a20 20 0 1 0 .1 0","M35 28V74M65 28V74M18 18Q50 32 82 18M18 84Q50 70 82 84","M82 38C70 12 25 12 20 42M18 62C30 88 75 88 80 58M30 30a7 7 0 1 0 .1 0M70 70a7 7 0 1 0 .1 0","M38 62a10 10 0 1 0 .1 0M46 58C42 25 70 10 80 32C86 48 70 60 68 78C67 88 78 92 88 85","M14 25V72M14 32C14 20 34 20 34 34V72M34 34C34 20 54 20 54 34V72M54 34C54 20 76 20 76 42V66C76 82 88 84 90 70M62 72C82 92 96 72 86 62","M12 80H88M12 64H34C18 45 28 18 50 18C72 18 82 45 66 64H88","M14 25V72M14 32C14 20 34 20 34 34V72M34 34C34 20 54 20 54 34V72M54 34C54 20 76 20 76 42V78L90 64M76 78L90 90","M18 84L84 18M54 18H84V48M30 56L58 84","M12 26C24 18 42 20 42 42V72M42 42C44 22 70 20 76 46C82 68 60 76 62 86C64 96 88 92 90 76","M12 38L31 24L50 38L69 24L88 38M12 70L31 56L50 70L69 56L88 70","M26 14C52 40 52 60 26 86M74 14C48 40 48 60 74 86M16 50H84"];
const CATS={t:["यात्रा","#2E9F6B",'<path d="M3 11l18-8-8 18-2-8z"/>'],h:["स्वास्थ्य","#1AA6A6",'<path d="M12 21C5 15 3 11 3 8a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 3-2 7-9 13z"/>'],f:["परिवार","#E0568B",'<path d="M3 11l9-8 9 8v9H3z"/>'],r:["सम्बन्ध","#8E5BD9",'<circle cx="8" cy="12" r="4"/><circle cx="16" cy="12" r="4"/>'],m:["आर्थिक","#C48A00",'<circle cx="12" cy="12" r="9"/><path d="M12 7v10M9 10h6"/>'],w:["कार्यक्षेत्र","#3B82E0",'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V4h6v3"/>'],g:["आजको सन्देश","#D32F2F",'<path d="M12 2l3 6.9 7.5.7-5.7 5 1.7 7.4L12 18l-6.5 4 1.7-7.4-5.7-5 7.5-.7z"/>']};
const RULES=[["t",["यात्रा","दिशा"]],["h",["स्वास्थ्य","खानपान"]],["f",["परिवार","घर"]],["r",["साथी","भेटघाट","सम्पर्क","मित्र","साझेदारी"]],["m",["आर्थिक","लेनदेन","खर्च","बजेट","पैसा","लाभ","बचत"]],["w",["जागिर","कार्यक्षेत्र","काम","व्यापार","योजना","अध्ययन","नेतृत्व","मेहनत"]]];
function autoCat(s){for(const [k,ws] of RULES) if(ws.some(w=>s.includes(w))) return k; return "g";}
function clusters(t){const o=[];let prev="";for(const ch of t){if(o.length&&(/\p{M}/u.test(ch)||prev==="\u094d"||prev==="\u200d"||prev==="\u200c"||ch==="\u200d"||ch==="\u200c"))o[o.length-1]+=ch;else o.push(ch);prev=ch;}return o;}
function rng(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const esc=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const STAT=`body{margin:0}
.dg{font-family:'Noto Sans Devanagari',FreeSans,sans-serif}
.c{opacity:0;animation:ty .01s linear forwards}
@keyframes ty{to{opacity:1}}
@keyframes relo{0%,99.4%{display:block}99.5%,100%{display:none}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes spinr{to{transform:rotate(-360deg)}}
@keyframes tw{0%,100%{opacity:.15;transform:scale(.6)}50%{opacity:1;transform:scale(1.2)}}
@keyframes f3d{0%{transform:rotateY(-16deg) rotateX(3deg) translateY(0)}100%{transform:rotateY(16deg) rotateX(-3deg) translateY(-10px)}}
@keyframes aura{0%,100%{transform:scale(.9);opacity:.4}50%{transform:scale(1.18);opacity:.85}}
@keyframes pf{0%{opacity:0;transform:translateY(20px)}30%{opacity:.95}100%{opacity:0;transform:translateY(-80px)}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.07)}}
@keyframes sheen{0%{background-position:200% 0}100%{background-position:-200% 0}}
@keyframes glow{0%,100%{filter:drop-shadow(0 0 10px rgba(245,196,81,.4))}50%{filter:drop-shadow(0 0 36px rgba(245,196,81,.95))}}
@keyframes ray{to{transform:rotate(360deg)}}
@keyframes bgsh{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes blob{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(40px,-30px) scale(1.15)}}
@keyframes pb{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes sweep{0%{transform:translateX(-200px) skewX(-20deg)}60%,100%{transform:translateX(1100px) skewX(-20deg)}}`;
const FONTS="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@600;700&display=swap";

const SECT=["#7C3AED","#8B2FE0","#9A2BD0","#A426B8","#C41F8A","#E23A5B","#F4622A","#F97316","#F0562F","#E03A5C","#C22A94","#9333EA"];
const DN="०१२३४५६७८९";const dev=n=>String(n).split("").map(c=>DN[+c]).join("");
function buildFull(content,assets,opts){
  opts=opts||{};const all=content.signs;const d=content.date;const IN=content.intro||{};
  const sub=opts.subset&&opts.subset.length?opts.subset.slice():[...Array(12).keys()];
  const intro=opts.intro!==undefined?opts.intro:sub[0]===0;
  const outro=opts.outro!==undefined?opts.outro:sub[sub.length-1]===11;
  const SL=4.4;const sch=[];let cur=intro?14.0:0.8;
  sub.forEach(si=>{const sg=all[si];let sents=(sg.sentences||[]).map(x=>typeof x==="string"?{text:x}:x).filter(x=>x&&x.text&&x.text.trim());if(!sents.length)sents=[{text:"आजको राशिफल उपलब्ध छैन।"}];
    const k=sents.length,c0=cur+6.6,E=c0+k*SL;sch.push({si,sg,S:cur,c0,E,sents,k,st:Math.max(0,Math.min(5,+sg.stars||0))});cur=E+0.8;});
  const last=sch[sch.length-1];const O=last.E+0.2;const T=Math.round((outro?O+4.8:last.E+1.0)*10)/10;
  const p=s=>(Math.max(0,Math.min(T,s))/T*100).toFixed(3)+"%";
  const kfs=[];
  const K=(name,pts)=>{pts=pts.slice().sort((a,b)=>a[0]-b[0]);if(pts[0][0]>0)pts.unshift([0,pts[0][1]]);pts.push([T,pts[pts.length-1][1]]);kfs.push(`@keyframes ${name}{`+pts.map(([s,c])=>`${p(s)}{${c}}`).join("")+"}");};
  const rv=(name,t0,dd=.6,frm="transform:translateY(24px)",to="transform:none")=>K(name,[[t0,"opacity:0;"+frm],[t0+dd,"opacity:1;"+to]]);
  const A=(nm,ex)=>`animation:${nm} ${T}s cubic-bezier(.22,.8,.3,1) infinite${ex||""}`;
  const HID="visibility:hidden;opacity:0",VIS="visibility:visible;opacity:1";
  const esc2=esc;const F="font-family:Poppins,'Noto Sans Devanagari',sans-serif;";
  const ev={whoosh:[],hits:[],pops:[],stars:[],cards:[],out:outro?O:null,T,intro:intro?14.0:0};
  const R=rng(11);const ri=(a,b)=>Math.floor(a+R()*(b-a+1));
  // wheel (stroke glyph) for dark + watermark
  const gl=G.map((pth,i)=>`<g transform="translate(${(400+318*Math.cos(i*.5236-1.5708)).toFixed(1)} ${(400+318*Math.sin(i*.5236-1.5708)).toFixed(1)}) scale(.62) translate(-50 -50)"><path d="${pth}" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>`).join("");
  const sp=[...Array(12)].map((_,i)=>`<line x1="${(400+250*Math.cos(i*.5236+.2618)).toFixed(0)}" y1="${(400+250*Math.sin(i*.5236+.2618)).toFixed(0)}" x2="${(400+385*Math.cos(i*.5236+.2618)).toFixed(0)}" y2="${(400+385*Math.sin(i*.5236+.2618)).toFixed(0)}" stroke="currentColor" stroke-width="2"/>`).join("");
  const wheel=`<svg width="800" height="800" viewBox="0 0 800 800" aria-hidden="true"><circle cx="400" cy="400" r="385" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="400" cy="400" r="250" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="400" cy="400" r="130" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="3 9"/>${sp}${gl}</svg>`;
  const tw=(n,mn,mx,seed)=>{const r=rng(seed);return [...Array(n)].map(()=>{const s=[3,4,6][Math.floor(r()*3)];return `<div style="position:absolute;left:${Math.floor(10+r()*1050)}px;top:${Math.floor(10+r()*1050)}px;width:${s}px;height:${s}px;border-radius:50%;background:#FFE9A8;animation:tw ${(2+r()*3).toFixed(1)}s ease-in-out ${(r()*3).toFixed(1)}s infinite"></div>`;}).join("");};
  const typed=(text,t0,step)=>clusters(text.trim()).map((c,j)=>c===" "?" ":`<span class="c" style="animation-delay:${(t0+j*step).toFixed(2)}s">${esc(c)}</span>`).join("");
  // ---------- colourful layer: welcome intro + every rashi intro (same wheel/background) ----------
  const S0=sch[0].S;const first=all[sub[0]];
  const lines=IN.lines&&IN.lines.length?IN.lines:["नेपडेट पात्रोले तयार पारेको आजको राशिफलमा स्वागत छ।","भिडियो अन्त्यसम्म हेर्नुहोला।"];
  let secs="";const pt=(r,a)=>[430+r*Math.sin(a*Math.PI/180),430-r*Math.cos(a*Math.PI/180)];
  for(let i=0;i<12;i++){const a0=i*30-15,a1=i*30+15;const [x0,y0]=pt(380,a0),[x1,y1]=pt(380,a1),[x2,y2]=pt(250,a1),[x3,y3]=pt(250,a0);
    secs+=`<path d="M${x0.toFixed(1)} ${y0.toFixed(1)}A380 380 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}L${x2.toFixed(1)} ${y2.toFixed(1)}A250 250 0 0 0 ${x3.toFixed(1)} ${y3.toFixed(1)}Z" fill="${SECT[i]}" stroke="#fff" stroke-width="3"/>`;}
  let dots="";for(let i=0;i<24;i++){const [x,y]=pt(402,i*15+7.5);dots+=`<path d="M0-9L2-2 9 0 2 2 0 9-2 2-9 0-2-2z" transform="translate(${x.toFixed(1)} ${y.toFixed(1)})" fill="#fff" opacity=".9"/>`;}
  const ring=`<svg width="860" height="860" viewBox="0 0 860 860" style="position:absolute;left:0;top:0"><circle cx="430" cy="430" r="426" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="2"/><circle cx="430" cy="430" r="412" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="3"/>${secs}<circle cx="430" cy="430" r="380" fill="none" stroke="#fff" stroke-opacity=".9" stroke-width="5"/><circle cx="430" cy="430" r="250" fill="none" stroke="#fff" stroke-width="5"/>${dots}</svg>`;
  const gi=[...Array(12)].map((_,i)=>{const a=i*30*Math.PI/180;return `<img src="${assets.imgs[i]}" alt="" style="position:absolute;left:${(430+315*Math.sin(a)-50).toFixed(1)}px;top:${(430-315*Math.cos(a)-50).toFixed(1)}px;width:100px;height:100px;filter:brightness(0) invert(1) drop-shadow(0 0 6px rgba(255,255,255,.6));opacity:.96;${A('wRi')}">`;}).join("");
  const corner=(i,l,t,w,rot)=>`<img src="${assets.imgs[i]}" alt="" style="position:absolute;left:${l}px;top:${t}px;width:${w}px;filter:brightness(0) invert(1);opacity:.13;transform:rotate(${rot}deg);animation:blob 9s ease-in-out ${i}s infinite">`;
  // wheel rotation (rashi comes to the top) + counter-rotation so icons stay upright
  const rotP=[],rotI=[];const addR=(t,dg)=>{rotP.push([t,`transform:rotate(${dg}deg)`]);rotI.push([t,`transform:rotate(${-dg}deg)`]);};
  const A0=360-sch[0].si*30;
  if(intro){addR(0,0);addR(2.2,0);addR(S0-1.0,60);addR(S0+0.5,A0);}else{addR(0,A0+40);addR(S0+0.7,A0);}
  const dkP=[],rgP=[],hlP=[[0,"opacity:0"]],bpP=[];
  dkP.push([0,intro?"clip-path:circle(78% at 50% 50%)":"clip-path:circle(0% at 50% 50%)"]);rgP.push([0,"opacity:0;transform:scale(0)"]);
  sch.forEach((o,n)=>{const S=o.S,An=360-o.si*30,open=!(n===0&&intro);
    if(open){dkP.push([S-0.8,"clip-path:circle(0% at 50% 50%)"],[S,"clip-path:circle(78% at 50% 50%)"]);rgP.push([S-0.8,"opacity:1;transform:scale(0)"],[S,"opacity:0;transform:scale(1)"]);if(n>0){addR(S-0.81,An+40);addR(S+0.7,An);}ev.whoosh.push(S-0.8);}
    else ev.whoosh.push(S-1.0);
    addR(S+3.6,An);
    dkP.push([S+3.6,"clip-path:circle(78% at 50% 50%)"],[S+4.4,"clip-path:circle(0% at 50% 50%)"]);
    rgP.push([S+3.59,"opacity:0;transform:scale(1)"],[S+3.6,"opacity:1;transform:scale(1)"],[S+4.4,"opacity:1;transform:scale(0)"],[S+4.41,"opacity:0;transform:scale(0)"]);
    hlP.push([S+0.5,"opacity:0"],[S+1.0,"opacity:1"],[S+3.5,"opacity:1"],[S+3.6,"opacity:0"]);
    const tin=open?S-0.7:S-0.3;
    K(`sc${n}`,[[tin-0.01,"visibility:hidden;opacity:0;transform:scale(.7)"],[tin,"visibility:visible;opacity:0;transform:scale(.7)"],[tin+0.8,"opacity:1;transform:scale(1)"],[S+3.5,"opacity:1;transform:scale(1)"],[S+3.6,"visibility:hidden;opacity:0;transform:scale(1)"]]);
    K(`bp${n}`,[[tin-0.01,"visibility:hidden;opacity:0;transform:translateY(20px)"],[tin+0.4,"visibility:visible;opacity:0;transform:translateY(20px)"],[tin+1.0,"opacity:1;transform:none"],[S+3.5,"opacity:1;transform:none"],[S+3.6,"visibility:hidden;opacity:0"]]);
    ev.hits.push(tin+0.2);ev.pops.push(S+4.0);
  });
  K("wR",rotP);K("wRi",rotI);K("dk",dkP);K("dkR",rgP);K("hl",hlP);
  if(intro){
    K("cwh",[[0.2,"opacity:0;transform:scale(.3)"],[2.2,"opacity:1;transform:scale(1)"]]);
    K("cc",[[0.9,"opacity:0;transform:scale(.4)"],[1.8,"opacity:1;transform:scale(1.06)"],[2.2,"opacity:1;transform:scale(1)"]]);
    const O1=S0-1.0,O2=S0-0.5;
    K("ct1",[[1.9,"opacity:0;transform:translateY(24px)"],[2.5,"opacity:1;transform:none"],[O1,"opacity:1;transform:none"],[O2,"opacity:0;transform:none"]]);
    K("ct2",[[2.4,"opacity:0;transform:translateY(24px)"],[3.0,"opacity:1;transform:none"],[O1,"opacity:1;transform:none"],[O2,"opacity:0;transform:none"]]);
    K("cdp",[[3.4,"opacity:0;transform:translateY(24px)"],[4.0,"opacity:1;transform:none"],[O1,"opacity:1;transform:none"],[O2,"opacity:0;transform:none"]]);
    K("cl1",[[4.0,"opacity:0;transform:translateY(16px)"],[4.3,"opacity:1;transform:none"],[10.2,"opacity:1;transform:none"],[10.7,"opacity:0;transform:none"]]);
    K("cl2",[[7.4,"opacity:0;transform:translateY(16px)"],[7.7,"opacity:1;transform:none"],[10.2,"opacity:1;transform:none"],[10.7,"opacity:0;transform:none"]]);
    K("cnx",[[10.8,"opacity:0;transform:scale(.8)"],[11.4,"opacity:1;transform:scale(1)"],[O1,"opacity:1;transform:scale(1)"],[O2,"opacity:0;transform:scale(1)"]]);
    ev.whoosh.push(0.2);ev.hits.push(1.9);
  } else K("cwh",[[0,"opacity:1;transform:none"]]);
  const sctr=sch.map((o,n)=>{const g=o.sg,nm=(g.name||""),nf=nm.length>6?60:nm.length>4?72:84;
    return `<div style="position:absolute;left:305px;top:205px;width:470px;height:470px;visibility:hidden;opacity:0;${A('sc'+n)}">
<div style="position:absolute;left:105px;top:20px;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(255,176,64,.55) 0%,rgba(255,176,64,0) 68%);animation:aura 4s ease-in-out infinite"></div>
<div style="position:absolute;left:135px;top:36px;width:200px;height:200px;perspective:800px"><img src="${assets.imgs[o.si]}" alt="" style="width:200px;height:200px;filter:drop-shadow(0 8px 12px rgba(120,40,10,.35));animation:f3d 5s ease-in-out infinite alternate"></div>
<div style="position:absolute;left:0;top:226px;width:470px;text-align:center;font-size:${nf}px;line-height:1.35;font-weight:700"><span style="color:#6B21A8">${esc(nm)}</span> <span style="color:#F97316">राशि</span></div>
<div style="position:absolute;left:0;top:${226+Math.round(nf*1.35)+2}px;width:470px;padding-left:8px;box-sizing:border-box;text-align:center;font-size:24px;letter-spacing:8px;font-weight:600;color:#8B5CF6">${esc((g.en||"").toUpperCase())}</div></div>
<div style="position:absolute;left:0;top:890px;width:1080px;text-align:center;visibility:hidden;opacity:0;${A('bp'+n)}"><span style="display:inline-block;padding:8px 30px;border-radius:40px;background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.7);color:#fff;font-size:30px;font-weight:700;text-shadow:0 2px 8px rgba(0,0,0,.25)">राशि <span class="dg">${dev(o.si+1)}</span> / <span class="dg">१२</span></span><div style="margin-top:10px;font-size:36px;font-weight:700;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.35)">आजको राशिफल</div></div>`;}).join("");
  const CL=`<div style="position:absolute;inset:0;overflow:hidden;background:linear-gradient(120deg,#FF6A3D,#E1306C,#8E2DE2,#2A9DF4,#FF6A3D);background-size:300% 300%;animation:bgsh 14s ease infinite,${A('dk').slice(10)}">
<div style="position:absolute;left:-120px;top:-100px;width:520px;height:520px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.35),transparent 70%);animation:blob 8s ease-in-out infinite"></div>
<div style="position:absolute;left:700px;top:560px;width:560px;height:560px;border-radius:50%;background:radial-gradient(circle,rgba(120,220,255,.4),transparent 70%);animation:blob 10s ease-in-out 1s infinite"></div>
${corner(0,-70,740,380,-12)}${corner(6,730,-40,360,10)}${corner(11,740,760,340,0)}${corner(3,-60,-40,330,0)}
${tw(30,0,0,71)}
<div style="position:absolute;left:-160px;top:-160px;width:1400px;height:1400px;background:repeating-conic-gradient(rgba(255,255,255,.12) 0 4deg,transparent 4deg 20deg);-webkit-mask-image:radial-gradient(circle,#000 10%,transparent 60%);mask-image:radial-gradient(circle,#000 10%,transparent 60%);animation:ray 50s linear infinite"></div>
<div style="position:absolute;left:110px;top:10px;width:860px;height:860px;${A('cwh')}"><div style="position:absolute;inset:0;filter:drop-shadow(0 14px 30px rgba(60,10,90,.45));${A('wR')}">${ring}${gi}</div></div>
<svg width="860" height="860" viewBox="0 0 860 860" style="position:absolute;left:110px;top:10px;opacity:0;${A('hl')}"><path d="M${pt(380,-15)[0].toFixed(1)} ${pt(380,-15)[1].toFixed(1)}A380 380 0 0 1 ${pt(380,15)[0].toFixed(1)} ${pt(380,15)[1].toFixed(1)}L${pt(250,15)[0].toFixed(1)} ${pt(250,15)[1].toFixed(1)}A250 250 0 0 0 ${pt(250,-15)[0].toFixed(1)} ${pt(250,-15)[1].toFixed(1)}Z" fill="#fff" fill-opacity=".22" stroke="#FFE08A" stroke-width="6" style="animation:pulse 1.6s ease-in-out infinite;transform-origin:430px 300px;filter:drop-shadow(0 0 14px #FFE08A)"/></svg>
<div style="position:absolute;left:305px;top:205px;width:470px;height:470px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff,#F6F1FF);box-shadow:inset 0 0 40px rgba(124,58,237,.18),0 0 40px rgba(255,255,255,.6);${intro?A('cc'):''}"></div>
${intro?`<div style="position:absolute;left:305px;top:290px;width:470px;text-align:center;font-size:92px;line-height:1.5;font-weight:700;color:#6B21A8;opacity:0;${A('ct1')}">आजको</div>
<div style="position:absolute;left:305px;top:390px;width:470px;text-align:center;font-size:96px;line-height:1.5;font-weight:700;color:#F97316;opacity:0;${A('ct2')}">राशिफल</div>
<div style="position:absolute;left:0;top:868px;width:1080px;text-align:center;opacity:0;${A('cdp')}"><span style="display:inline-block;padding:8px 30px;border-radius:40px;background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.7);color:#fff;font-size:32px;font-weight:700;text-shadow:0 2px 8px rgba(0,0,0,.25)">${esc(IN.prefix||"आज")} · <span class="dg">${esc(d.year)}</span> ${esc(d.month)} <span class="dg">${esc(d.day)}</span> गते ${esc(d.weekday)}</span></div>
<div style="position:absolute;left:40px;top:940px;width:1000px;text-align:center;font-size:33px;line-height:1.5;font-weight:600;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.35);opacity:0;${A('cl1')}">${typed(lines[0]||"",4.3,.05)}</div>
<div style="position:absolute;left:40px;top:998px;width:1000px;text-align:center;font-size:33px;line-height:1.5;font-weight:600;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.35);opacity:0;${A('cl2')}">${typed(lines[1]||"",7.7,.05)}</div>
<div style="position:absolute;left:0;top:960px;width:1080px;text-align:center;opacity:0;${A('cnx')}"><span style="display:inline-block;padding:10px 38px;border-radius:44px;background:linear-gradient(100deg,#FFD66B,#FFB347);color:#5B1A8C;font-size:40px;font-weight:700;box-shadow:0 8px 24px rgba(0,0,0,.25)">सुरुमा — ${esc(first.name)} राशि →</span></div>`:""}
${sctr}</div>
<div style="position:absolute;left:-302px;top:-302px;width:1684px;height:1684px;box-sizing:border-box;border-radius:50%;border:10px solid #fff;box-shadow:0 0 60px 10px rgba(255,255,255,.7);opacity:0;${A('dkR')}"></div>`;
  // ---------- main (white) layer ----------
  const P='M12 2l3 6.9 7.5.7-5.7 5 1.7 7.4L12 18l-6.5 4 1.7-7.4-5.7-5 7.5-.7z';
  const b0=sch[0].S+4.0;
  rv("h1",b0);rv("h2",b0+.3);rv("h3",b0+.5);rv("ft",b0+.2);rv("dts",b0+.4);
  const dateB=`<span class="dg">${esc(d.year)}</span> ${esc(d.month)} <span class="dg">${esc(d.day)}</span> | ${esc(d.weekday)}`;
  const orb='<svg width="300" height="300" viewBox="0 0 300 300" style="position:absolute;left:30px;top:-20px;animation:spin 9s linear infinite"><circle cx="150" cy="150" r="125" fill="none" stroke="#E8B93C" stroke-opacity=".5" stroke-dasharray="3 8"/><circle cx="275" cy="150" r="7" fill="#F5C451"/><circle cx="25" cy="150" r="6" fill="#D32F2F"/><circle cx="150" cy="25" r="5" fill="#3B82E0"/></svg><svg width="300" height="300" viewBox="0 0 300 300" style="position:absolute;left:30px;top:-20px;animation:spinr 14s linear infinite"><circle cx="150" cy="150" r="108" fill="none" stroke="#D32F2F" stroke-opacity=".35" stroke-dasharray="2 10"/><circle cx="150" cy="42" r="5" fill="#E8B93C"/></svg>';
  const parts=(c,sd)=>{const r=rng(sd);return [...Array(14)].map(()=>{const s=[4,5,6][Math.floor(r()*3)];return `<div style="position:absolute;left:${Math.floor(-60+r()*300)}px;top:${Math.floor(60+r()*180)}px;width:${s}px;height:${s}px;border-radius:50%;background:${c};box-shadow:0 0 8px #F5C451;animation:pf ${(3+r()*2).toFixed(1)}s ease-out ${(r()*4).toFixed(1)}s infinite"></div>`;}).join("");};
  const signsH=sch.map((o,n)=>{const S=o.S,g=o.sg,st=o.st,col=g.colorHex||"#F2C230";
    K(`sg${n}`,[[S+3.9,"visibility:hidden"],[S+4.0,"visibility:visible"],[o.E+0.7,"visibility:visible"],[o.E+0.8,"visibility:hidden"]]);
    K(`em${n}`,[[S+4.0,"opacity:0;transform:scale(.4)"],[S+4.5,"opacity:1;transform:scale(1.1)"],[S+4.8,"opacity:1;transform:scale(1)"]]);
    rv(`nm${n}`,S+4.4,.6,"transform:translateY(30px) scale(.85)");rv(`lt${n}`,S+4.8);rv(`c1${n}`,S+5.9);rv(`c2${n}`,S+6.15);
    const stT=[...Array(st)].map((_,i)=>S+5.2+.45*i);stT.forEach((t0,i)=>{K(`st${n}_${i}`,[[t0,"opacity:0;transform:scale(.3)"],[t0+.25,"opacity:1;transform:scale(1.45)"],[t0+.55,"opacity:1;transform:scale(1)"]]);ev.stars.push(t0);});
    const starsB=[0,1,2,3,4].map(i=>`<div style="position:relative;width:48px;height:42px"><svg width="42" height="42" viewBox="0 0 24 24" style="position:absolute;left:0;top:0"><path d="${P}" fill="#D1D5DB"/></svg>`+(i<st?`<svg width="42" height="42" viewBox="0 0 24 24" style="position:absolute;left:0;top:0;filter:drop-shadow(0 0 8px rgba(211,47,47,.7));${A(`st${n}_${i}`)}"><path d="${P}" fill="#D32F2F"/></svg>`:"")+`</div>`).join("");
    let cardsH="";
    o.sents.forEach((s,i)=>{const c0=o.c0+i*SL;ev.cards.push(c0);
      const pts=[[c0,"opacity:0;transform:translateY(34px) scale(.96)"],[c0+.45,"opacity:1;transform:none"]];if(i<o.k-1)pts.push([c0+SL-.5,"opacity:1;transform:none"],[c0+SL-.05,"opacity:0;transform:translateY(-26px) scale(.98)"]);else pts.push([o.E+0.3,"opacity:1;transform:none"],[o.E+0.7,"opacity:0;transform:none"]);K(`cd${n}_${i}`,pts);
      const ck=(s.cat&&CATS[s.cat])?s.cat:autoCat(s.text);const [lab,cc,ic]=CATS[ck];
      const dots=[...Array(o.k)].map((_,q)=>`<div style="width:${q===i?34:10}px;height:10px;border-radius:5px;background:${q===i?cc:"#D1D5DB"}"></div>`).join("");
      cardsH+=`<div style="position:absolute;left:80px;top:652px;width:920px;height:276px;box-sizing:border-box;padding:24px 36px;border-radius:30px;background:linear-gradient(180deg,#fff,#F5F8FF);border:2px solid ${cc}55;box-shadow:0 18px 40px rgba(31,58,125,.14);opacity:0;${A(`cd${n}_${i}`)}"><div style="position:absolute;left:0;top:30px;width:8px;height:70px;border-radius:0 6px 6px 0;background:${cc}"></div><div style="display:inline-flex;align-items:center;gap:10px;padding:8px 20px 8px 14px;border-radius:30px;background:${cc};color:#fff;font-size:24px;font-weight:600"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ic}</svg>${lab}</div><div style="margin-top:14px;font-size:38px;line-height:1.42;font-weight:500;color:#1F2937">${typed(s.text,c0+.5,.032)}</div><div style="position:absolute;right:30px;bottom:22px;display:flex;gap:6px">${dots}</div></div>`;});
    return `<div style="position:absolute;inset:0;visibility:hidden;${A('sg'+n)}">
<div style="position:absolute;left:360px;top:190px;width:360px;height:260px;opacity:0;${A('em'+n)}">
<div style="position:absolute;left:20px;top:10px;width:320px;height:240px;border-radius:50%;background:radial-gradient(circle,rgba(245,196,81,.85) 0%,rgba(245,196,81,0) 70%);animation:aura 4s ease-in-out infinite"></div>${orb}${parts("#E8B93C",n+3)}
<div style="position:absolute;left:65px;top:15px;width:230px;height:230px;perspective:900px"><img src="${assets.imgs[o.si]}" alt="" style="width:230px;height:230px;filter:drop-shadow(0 12px 16px rgba(130,50,10,.35));animation:f3d 5s ease-in-out infinite alternate"></div></div>
<div style="position:absolute;left:0;top:428px;width:1080px;text-align:center;font-size:74px;line-height:1.25;font-weight:700;color:#D32F2F;opacity:0;${A('nm'+n)}">${esc(g.name)}</div>
<div style="position:absolute;left:350px;top:524px;width:600px;display:flex;align-items:center;gap:20px"><div style="width:300px;font-size:19px;line-height:1.5;font-weight:700;color:#1F3A7D;opacity:0;${A('lt'+n)}">${esc(g.letters||"")}</div><div style="display:flex">${starsB}</div></div>
<div style="position:absolute;left:0;top:590px;width:1080px;display:flex;justify-content:center;gap:18px"><div style="display:flex;align-items:center;gap:10px;padding:6px 20px;border-radius:30px;background:#fff;border:2px solid ${esc(col)};font-size:21px;font-weight:600;color:#1F2937;opacity:0;${A('c1'+n)}"><span style="width:18px;height:18px;border-radius:50%;background:${esc(col)};box-shadow:0 0 10px ${esc(col)}"></span>शुभ रंग: ${esc(g.colorName||"")}</div><div style="padding:6px 20px;border-radius:30px;background:#fff;border:2px solid #E8B93C;font-size:21px;font-weight:600;color:#1F2937;opacity:0;${A('c2'+n)}">शुभ अंक: <b class="dg" style="color:#D32F2F">${esc(g.number||"")}</b></div></div>
${cardsH}</div>`;}).join("");
  // sign progress dots
  const dotsH=[...Array(12)].map((_,j)=>{const n=sch.findIndex(o=>o.si===j);if(n>=0){const o=sch[n];K(`dt${j}`,[[0,"background:#D1D5DB;width:10px"],[o.S+4.0,"background:#D1D5DB;width:10px"],[o.S+4.4,"background:#D32F2F;width:26px"],[o.E+0.7,"background:#D32F2F;width:26px"],[o.E+0.8,"background:#E5E7EB;width:10px"]]);}
    return `<div style="height:10px;width:10px;border-radius:5px;background:#D1D5DB;${n>=0?`animation:dt${j} ${T}s linear infinite`:""}"></div>`;}).join("");
  const tag=esc(content.tagline||"हरेक दिनको विश्वास");
  K("ov",[[O,"opacity:0"],[O+.8,"opacity:1"]]);K("ovl",[[O+.4,"opacity:0;transform:scale(.7)"],[O+1.3,"opacity:1;transform:scale(1)"]]);rv("ovt",O+1.5);rv("ovb",O+1.9);
  const MAIN=`<div style="position:absolute;inset:0;background:radial-gradient(circle at 90% 6%,rgba(245,196,81,.16),transparent 34%),radial-gradient(circle at 6% 96%,rgba(59,130,224,.10),transparent 36%),#fff;overflow:hidden">
<div style="position:absolute;left:140px;top:200px;width:800px;height:800px;color:#B08A3C;opacity:.13;animation:spin 90s linear infinite">${wheel}</div>
<div style="position:absolute;left:64px;top:26px;padding-top:20px;font-size:58px;line-height:1.2;font-weight:700;color:transparent;background:linear-gradient(100deg,#3B82E0 40%,#A9CBFF 50%,#3B82E0 60%);background-size:250% 100%;-webkit-background-clip:text;background-clip:text;opacity:0;${A('h1')},sheen 4s linear infinite">दैनिक<br>राशिफल</div>
<div style="position:absolute;left:64px;top:176px;font-size:25px;font-weight:700;color:#D32F2F;opacity:0;${A('h2')}">${dateB}</div>
<div style="position:absolute;left:64px;top:222px;display:flex;gap:7px;align-items:center;opacity:0;${A('dts')}">${dotsH}</div>
<img src="${assets.logo}" alt="NepDate" style="position:absolute;left:915px;top:46px;width:110px;height:100px;object-fit:contain;opacity:0;${A('h3')}">
${signsH}
<div style="position:absolute;left:40px;top:944px;width:1000px;height:114px;border-radius:28px;background:linear-gradient(100deg,#2F6FD6 0%,#1F3A7D 100%);box-shadow:0 14px 30px rgba(31,58,125,.35);overflow:hidden;opacity:0;${A('ft')}">
<div style="position:absolute;top:0;left:0;width:140px;height:114px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.28),transparent);animation:sweep 3.6s ease-in-out infinite"></div>
<div style="position:absolute;left:20px;top:15px;width:92px;height:84px;border-radius:20px;background:#fff;display:flex;align-items:center;justify-content:center"><img src="${assets.logo}" alt="NepDate" style="width:84px;height:76px;object-fit:contain"></div>
<div style="position:absolute;left:130px;top:12px;width:620px"><div style="font-size:19px;font-weight:600;color:#FFD66B;letter-spacing:1px">${tag}</div><div style="margin-top:2px;font-size:29px;line-height:1.35;font-weight:700;color:#fff">NepDate डाउनलोड गर्नुहोस्</div><div style="margin-top:2px;font-size:16px;font-weight:500;color:#CFE0FF">पञ्चाङ्ग · राशिफल · कुण्डली · शुभ साइत</div></div>
<img src="${assets.badge}" alt="Google Play" style="position:absolute;left:770px;top:26px;width:200px;height:62px;border-radius:10px;box-shadow:0 0 0 2px rgba(255,255,255,.35);animation:pulse 2.2s ease-in-out infinite"></div>
</div>`;
  const OUT=outro?`<div style="position:absolute;inset:0;background:#fff;opacity:0;display:flex;flex-direction:column;align-items:center;justify-content:center;${A('ov')}"><img src="${assets.logo}" alt="NepDate" style="width:340px;height:310px;object-fit:contain;opacity:0;${A('ovl')},glow 2.5s ease-in-out infinite"><div style="margin-top:14px;font-size:46px;font-weight:700;color:#3B82E0;opacity:0;${A('ovt')}">${tag}</div><img src="${assets.badge}" alt="Google Play" style="margin-top:34px;width:300px;height:93px;opacity:0;${A('ovb')}"></div>`:"";
  if(outro)ev.whoosh.push(O-0.1);
  const css=STAT+"\n"+kfs.join("\n");
  const loop=opts.loop?`animation:relo ${T}s linear infinite;`:"";
  const root=`<div style="position:relative;width:1080px;height:1080px;overflow:hidden;background:#07081F;${F}${loop}">${MAIN}${CL}${OUT}<div style="position:absolute;left:0;top:0;width:1080px;height:7px;background:linear-gradient(90deg,#FFD66B,#E1306C,#8E2DE2);transform-origin:0 0;transform:scaleX(0);animation:pb ${T}s linear infinite"></div></div>`;
  return {css,root,T,ev,sections:{intro:intro?0:null,signs:sch.map(o=>({si:o.si,S:o.S,c0:o.c0,E:o.E})),out:outro?O:null}};
}
function doc(r){return `<!doctype html><html lang="ne"><head><meta charset="utf-8"><link href="${FONTS}" rel="stylesheet"><style>${r.css}</style></head><body>${r.root}</body></html>`;}
g.RV={build:buildFull,doc,CATS,autoCat,FONTS};
})(typeof window!=="undefined"?window:globalThis);
