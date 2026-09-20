/* nv-lightbox v1 — click the main photo of a project page to view it full-screen; ← → / swipe through the gallery, Esc or click to close. */
(function(){
var main=document.getElementById("nv-main-img");if(!main)return;
function srcs(){var a=[];Array.prototype.forEach.call(document.querySelectorAll(".nv-film-btn img"),function(i){a.push(i.getAttribute("src"))});if(!a.length)a.push(main.getAttribute("src"));return a}
var box,img,cap,idx=0,list=[];
var CSS=".nv-lb{position:fixed;inset:0;z-index:10000;background:rgba(8,8,20,.94);display:flex;align-items:center;justify-content:center;cursor:zoom-out}.nv-lb img{max-width:96vw;max-height:88vh;object-fit:contain;box-shadow:0 20px 60px rgba(0,0,0,.6);cursor:default}"+
 ".nv-lb button{position:absolute;top:50%;transform:translateY(-50%);width:52px;height:52px;border:0;border-radius:50%;background:rgba(255,255,255,.14);color:#fff;font-size:26px;line-height:52px;cursor:pointer;transition:background .15s}.nv-lb button:hover{background:rgba(255,255,255,.3)}.nv-lb .nv-lb-prev{left:16px}.nv-lb .nv-lb-next{right:16px}"+
 ".nv-lb .nv-lb-close{top:14px;right:14px;transform:none;font-size:22px}.nv-lb .nv-lb-cap{position:absolute;bottom:16px;left:0;right:0;text-align:center;color:rgba(255,255,255,.75);font:600 12px/1.4 'Suisse Intl','Helvetica Neue',Arial,sans-serif;letter-spacing:.08em}"+
 "#nv-main-img{cursor:zoom-in}@media(max-width:600px){.nv-lb button{width:42px;height:42px;line-height:42px;font-size:20px}.nv-lb .nv-lb-prev{left:6px}.nv-lb .nv-lb-next{right:6px}}";
function show(i){idx=(i+list.length)%list.length;img.src=list[idx];cap.textContent=(idx+1)+" / "+list.length;
 var b=document.querySelectorAll(".nv-film-btn")[idx];if(b)b.click()}
function close(){if(!box)return;document.body.removeChild(box);box=null;document.body.style.overflow="";document.removeEventListener("keydown",keys)}
function keys(e){if(e.key==="Escape")close();else if(e.key==="ArrowRight")show(idx+1);else if(e.key==="ArrowLeft")show(idx-1)}
function open(){list=srcs();var cur=main.getAttribute("src");var i=list.indexOf(cur);if(i<0)i=0;
 if(!document.getElementById("nv-lb-css")){var st=document.createElement("style");st.id="nv-lb-css";st.textContent=CSS;document.head.appendChild(st)}
 box=document.createElement("div");box.className="nv-lb";box.setAttribute("role","dialog");box.setAttribute("aria-modal","true");
 img=document.createElement("img");img.alt=main.alt||"";box.appendChild(img);
 cap=document.createElement("div");cap.className="nv-lb-cap";box.appendChild(cap);
 var mk=function(cls,txt,fn,label){var b=document.createElement("button");b.type="button";b.className=cls;b.innerHTML=txt;b.setAttribute("aria-label",label);b.addEventListener("click",function(e){e.stopPropagation();fn()});box.appendChild(b)};
 if(list.length>1){mk("nv-lb-prev","&#8249;",function(){show(idx-1)},"Previous");mk("nv-lb-next","&#8250;",function(){show(idx+1)},"Next")}
 mk("nv-lb-close","&#10005;",close,"Close");
 box.addEventListener("click",function(e){if(e.target===box)close()});img.addEventListener("click",function(e){e.stopPropagation()});
 var x0=null;box.addEventListener("touchstart",function(e){x0=e.touches[0].clientX},{passive:true});box.addEventListener("touchend",function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0;x0=null;if(Math.abs(dx)>40)show(dx<0?idx+1:idx-1)});
 document.body.appendChild(box);document.body.style.overflow="hidden";document.addEventListener("keydown",keys);show(i)}
main.addEventListener("click",open);main.setAttribute("tabindex","0");main.setAttribute("role","button");main.addEventListener("keydown",function(e){if(e.key==="Enter"||e.key===" "){e.preventDefault();open()}});
})();
