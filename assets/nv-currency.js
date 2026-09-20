/* nv-currency v2 — USD ⇄ AED switch (dirham peg 3.6725). Segmented control in the header (desktop: next to РУС / the CTA;
   phone: next to the menu button), converts every price text live and remembers the choice. Waits for React hydration
   on the app pages so the pre-rendered markup is never touched before React has adopted it. Prices are converted per
   run of adjacent text nodes (React renders "$ " and the number as separate nodes); AED ≥ 100 000 is rounded to 1 000
   because the developer's list price is the round dirham figure the USD number was derived from. */
(function(){
var RATE=3.6725,KEY="nv-cur",cur=null;
try{cur=localStorage.getItem(KEY)}catch(e){}
cur=cur==="AED"?"AED":"USD";
var orig=new WeakMap(),mine=new WeakMap();  /* orig = the USD text the page/React wrote; mine = the last value this script wrote */
var RX=/\$\s?(\d[\d   ]*\d|\d)/g;
function fmt(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g," ")}
function aed(usd){var v=usd*RATE;return v>=1e5?Math.round(v/1000)*1000:Math.round(v)}
function set(node,v){if(node.nodeValue!==v)node.nodeValue=v;mine.set(node,v)}
function origOf(node){var t=node.nodeValue;if(mine.get(node)!==t)orig.set(node,t);return orig.get(node)}
function runOf(node){var a=node;while(a.previousSibling&&a.previousSibling.nodeType===3)a=a.previousSibling;var list=[];for(var n=a;n&&n.nodeType===3;n=n.nextSibling)list.push(n);return list}
function convRun(list){var joined="";for(var i=0;i<list.length;i++)joined+=origOf(list[i]);
 if(joined.indexOf("$")<0)return;
 var out=joined.replace(RX,function(m,d){var n=parseFloat(d.replace(/[   ]/g,""));return isNaN(n)?m:"AED "+fmt(aed(n))});
 if(out===joined)return;
 set(list[0],out);for(var j=1;j<list.length;j++)set(list[j],"")}
function revertRun(list){for(var i=0;i<list.length;i++){var n=list[i];if(!orig.has(n))continue;if(mine.get(n)===n.nodeValue)set(n,orig.get(n));else orig.set(n,n.nodeValue)}}
function walk(fn){var w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null);var n,starts=[];
 while(n=w.nextNode()){if(!(n.previousSibling&&n.previousSibling.nodeType===3))starts.push(n)}
 for(var i=0;i<starts.length;i++)fn(runOf(starts[i]))}
function hydrated(el){if(!el)return false;for(var k in el){if(k.indexOf("__reactFiber")===0)return true}return false}
function isApp(){return !document.querySelector(".nv-site-wrap")}
function ready(){return !isApp()||hydrated(document.querySelector("header"))}
function paint(){document.documentElement.setAttribute("data-nv-cur",cur);
 var segs=document.querySelectorAll(".nv-cur-btn button");for(var i=0;i<segs.length;i++){var s=segs[i],on=s.getAttribute("data-c")===cur;s.style.background=on?"#0037FF":"transparent";s.style.color=on?"#fff":"#141414";s.setAttribute("aria-pressed",on?"true":"false")}}
function apply(){if(!ready())return;walk(cur==="AED"?convRun:revertRun);paint()}
function setCur(c){if(c===cur)return;cur=c;try{localStorage.setItem(KEY,cur)}catch(e){}apply()}
var CSS=".nv-cur-btn{display:inline-flex;align-items:stretch;border:1px solid rgba(20,20,20,.22);background:#fff;white-space:nowrap;flex-shrink:0;min-height:36px}"+
 ".nv-cur-btn button{border:0;margin:0;background:transparent;color:#141414;font:700 10.5px/1 'Suisse Intl','Helvetica Neue',Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:0 .6rem;cursor:pointer;display:inline-flex;align-items:center;transition:background .15s,color .15s}"+
 ".nv-cur-btn button[aria-pressed=false]:hover{color:#0037FF}"+
 ".nv-cur-btn.nv-cur-m{display:none;margin-left:auto}"+
 "@media(max-width:1023.98px){.nv-cur-btn.nv-cur-m{display:inline-flex}}"+
 /* phones: the header cannot hold wordmark + switch + CTA/menu (measured 428 px at 375) → icon-only logo */
 "@media(max-width:479.98px){header a[href$='/'] .t-h3,.nv-site-wrap .nv-logo span{display:none}}"+
 "html[data-nv-cur=AED] .nv-eq{display:none}";
function make(extra){var b=document.createElement("div");b.className="nv-cur-btn"+(extra?" "+extra:"");b.setAttribute("role","group");b.setAttribute("aria-label","Валюта");
 ["USD","AED"].forEach(function(c){var s=document.createElement("button");s.type="button";s.setAttribute("data-c",c);s.textContent=c;s.title=c==="USD"?"Цены в долларах США":"Цены в дирхамах ОАЭ";s.addEventListener("click",function(){setCur(c)});b.appendChild(s)});return b}
function wanted(){return !!document.querySelector(".nv-site-wrap")||/^(?:\/en)?\/(dubai|abudhabi|armenia|georgia)\/(residential|commercial)\/?$/.test(location.pathname)}  /* only where prices are listed */
function mount(){
 if(!document.getElementById("nv-cur-css")){var st=document.createElement("style");st.id="nv-cur-css";st.textContent=CSS;document.head.appendChild(st)}
 if(!wanted()){var old=document.querySelectorAll(".nv-cur-btn");for(var i=0;i<old.length;i++)old[i].parentNode.removeChild(old[i]);return}
 var wrap=document.querySelector(".nv-site-wrap");
 if(wrap){if(wrap.querySelector(".nv-cur-btn"))return;var cta=wrap.querySelector(".nv-head-cta");
  if(!cta){wrap.appendChild(make(""));paint();return}
  var g=document.createElement("div");g.setAttribute("style","display:flex;align-items:center;gap:.6rem;flex-shrink:0");
  wrap.insertBefore(g,cta);g.appendChild(make(""));g.appendChild(cta);paint();return}
 var head=document.querySelector("header .mx-auto")||document.querySelector("header");
 if(!head||head.querySelector(".nv-cur-btn")||!hydrated(head))return;
 var lang=head.querySelector("span.text-signal,a.text-signal");var grp=lang?lang.parentElement:null;
 var burger=head.querySelector("button[aria-label]");
 if(grp)grp.insertBefore(make("nv-cur-d"),grp.firstChild);
 head.insertBefore(make("nv-cur-m"),burger&&burger.parentElement===head?burger:null);
 paint()}
var mo=new MutationObserver(function(ms){var added=false;
 for(var i=0;i<ms.length;i++){var m=ms[i];
  if(m.type==="characterData"){if(ready()&&m.target.parentNode)(cur==="AED"?convRun:revertRun)(runOf(m.target))}  /* React rewrote a price in place */
  else if(m.addedNodes&&m.addedNodes.length)added=true}
 if(added){mount();apply()}});
function start(){mount();apply();mo.observe(document.body,{childList:true,subtree:true,characterData:true});
 var tries=0,iv=setInterval(function(){mount();if(document.querySelector(".nv-cur-btn")){apply();clearInterval(iv)}else if(++tries>100)clearInterval(iv)},150)}
window.nvCurrency={get:function(){return cur},set:setCur,apply:apply};
if(document.body)start();else document.addEventListener("DOMContentLoaded",start);
})();
