'use strict';
// The renderer accepts only normalized enums/numbers. No model markup is interpreted.
window.AvatarStudio=(()=>{
 const NS='http://www.w3.org/2000/svg';
 const svg=(name,attrs={},children=[])=>{const e=document.createElementNS(NS,name);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,String(v));children.forEach(x=>e.append(x));return e};
 const pick=(x,a,d)=>a.includes(x)?x:d,clamp=(x,l,h)=>Math.max(l,Math.min(h,Number(x)||1)),color=(x,d)=>/^#[0-9a-f]{6}$/i.test(x)?x:d;
 function render(raw={}){
  const a={face:pick(raw.face,['round','oval','square','long'],'oval'),width:clamp(raw.width,.85,1.15),chin:clamp(raw.chin,.85,1.15),eyes:pick(raw.eyes,['almond','round','narrow'],'almond'),brows:pick(raw.brows,['straight','arched','soft'],'straight'),nose:pick(raw.nose,['small','straight','rounded'],'straight'),mouth:pick(raw.mouth,['soft','wide','small'],'soft'),hair:pick(raw.hair,['short','side','bob','long','wave','crop','bun','curtain'],'side'),skin:color(raw.skin,'#e6b18b'),hair_color:color(raw.hair_color,'#242631'),color:color(raw.color,'#343e62'),outfit:pick(raw.outfit,['blazer','shirt','knit'],'blazer'),glasses:raw.glasses===true};
  const root=svg('svg',{viewBox:'0 0 500 550',role:'img','aria-label':'原創虛構 2D 業務顧問'}),body=svg('g',{class:'avatar-body'});root.append(body);
  const path=(d,fill,attrs={})=>svg('path',{d,fill,...attrs});const ellipse=(cx,cy,rx,ry,fill,attrs={})=>svg('ellipse',{cx,cy,rx,ry,fill,...attrs});
  if(['long','wave','bob'].includes(a.hair))body.append(path('M160 116 Q150 58 250 57 Q351 61 345 137 L367 325 Q313 364 145 321 Z',a.hair_color));
  body.append(path('M213 248 L213 296 Q182 304 157 323 L135 550 L365 550 L342 323 Q309 305 286 296 L286 248',a.skin));
  const outfit=svg('g');outfit.append(path('M204 292 L250 331 L296 292 Q334 302 361 329 L396 550 L103 550 L136 329 Q163 306 204 292',a.color));
  if(a.outfit==='blazer')outfit.append(path('M210 296 L250 331 L290 296 L277 441 L250 524 L224 438 Z','#f7f5ef'),path('M204 292 L223 386 L205 376 L239 511 L190 370 L171 351 Z','#ffffff1c'),path('M296 292 L277 386 L295 376 L261 511 L310 370 L330 351 Z','#00000015'));
  if(a.outfit==='shirt')outfit.append(path('M204 292 L250 321 L296 292 L280 350 L250 330 L220 350 Z','#ffffff40'),path('M250 332 L250 550','none',{stroke:'#ffffff40','stroke-width':2}));
  if(a.outfit==='knit')outfit.append(path('M204 295 Q250 353 296 295','none',{stroke:'#00000025','stroke-width':8}));
  body.append(outfit);
  for(const [cls,d,hand]of [['left','M148 324 Q116 327 103 380 L83 479 Q91 501 114 491 L153 390','M84 478 Q76 514 94 530 Q111 531 119 494'],['right','M352 324 Q384 327 397 380 L417 479 Q409 501 386 491 L347 390','M416 478 Q424 514 406 530 Q389 531 381 494']])body.append(svg('g',{class:'arm '+cls},[path(d,a.color),path(hand,a.skin)]));
  const head=svg('g',{class:'avatar-head'}),face=svg('g',{transform:`translate(250 185) scale(${a.width} ${a.face==='long'?1.12:1}) translate(-250 -185)`});head.append(face);body.append(head);
  face.append(ellipse(173,185,15,24,a.skin),ellipse(327,185,15,24,a.skin));
  let d={oval:'M177 135 Q178 82 250 80 Q323 83 324 137 L319 212 Q302 269 250 281 Q200 268 181 212 Z',round:'M174 139 Q168 83 250 81 Q332 83 326 143 L328 201 Q323 268 250 278 Q180 269 173 209 Z',square:'M177 132 Q174 81 250 81 Q326 83 323 134 L323 220 L297 263 Q249 280 205 262 L178 224 Z',long:'M185 133 Q176 85 250 81 Q324 85 315 135 L310 219 Q283 271 250 282 Q215 272 189 220 Z'}[a.face];
  d=d.replace(/\b(281|282|278)\b/g,n=>String(250+(Number(n)-250)*a.chin));
  face.append(path(d,a.skin),path('M183 174 Q185 225 211 245 Q243 270 282 259 Q263 281 250 281 Q200 268 181 212 Z','#00000008'));
  const eyeY=181,eyeRy={almond:6,round:9,narrow:4}[a.eyes];const eyes=svg('g',{class:'eye-layer'});
  for(const x of [214,286])eyes.append(ellipse(x,eyeY,15,eyeRy,'#fff9ef'),ellipse(x+1,eyeY,5.5,eyeRy,'#342d2e'),ellipse(x+2,eyeY-2,1.5,1.6,'white'),path(`M${x-16} ${eyeY} Q${x} ${eyeY-eyeRy-6} ${x+16} ${eyeY}`,'none',{stroke:a.hair_color,'stroke-width':2.5,'stroke-linecap':'round'}));
  face.append(eyes);const brows=svg('g',{class:'eyebrow-layer'});
  for(const x of [214,286])brows.append(path(`M${x-18} 162 Q${x} ${a.brows==='arched'?150:a.brows==='soft'?156:160} ${x+17} 160`,'none',{stroke:a.hair_color,'stroke-width':a.brows==='soft'?3:4,'stroke-linecap':'round'}));face.append(brows);
  face.append(path(a.nose==='small'?'M250 189 L245 213 Q250 217 256 213':a.nose==='rounded'?'M249 187 Q235 217 246 218 Q258 222 262 211':'M252 185 L244 215 L256 216','none',{stroke:'#a9765b','stroke-width':2,'stroke-linecap':'round'}));
  const mw={soft:18,wide:24,small:14}[a.mouth];face.append(ellipse(250,238,mw,9,'#753f41',{class:'mouth-open'}),path(`M${250-mw} 236 Q250 241 ${250+mw} 236`,'none',{stroke:'#9d5c58','stroke-width':2.5,'stroke-linecap':'round'}),path(`M${247-mw} 234 Q250 253 ${253+mw} 234`,'none',{stroke:'#9d5c58','stroke-width':2.5,class:'smile-line'}));
  if(a.glasses)face.append(svg('g',{fill:'none',stroke:'#555160','stroke-width':3},[svg('rect',{x:191,y:170,width:47,height:29,rx:10}),svg('rect',{x:262,y:170,width:47,height:29,rx:10}),path('M238 180 Q250 175 262 180 M190 177 L174 172 M310 177 L326 172','none')]));
  const hair={short:'M171 170 Q153 110 183 79 Q225 51 284 72 Q338 72 330 162 L311 133 L297 105 Q244 139 182 132 Z',side:'M171 178 Q143 120 186 80 Q224 47 280 68 Q344 68 330 173 L316 140 L305 109 Q268 144 180 147 Z',bob:'M164 233 Q145 100 196 74 Q250 44 306 80 Q353 113 337 243 L315 216 L316 125 Q255 143 184 120 L186 226 Z',long:'M165 203 Q146 85 207 68 Q280 39 325 96 L335 216 L317 173 L299 106 Q250 144 184 139 Z',wave:'M165 203 Q133 164 159 130 Q148 89 186 77 Q203 45 244 65 Q300 46 319 79 Q353 97 337 136 Q359 170 332 221 L317 176 L298 119 Q251 149 182 127 Z',crop:'M174 145 L173 112 Q187 68 250 66 Q308 69 326 111 L326 146 L311 122 L189 120 Z',bun:'M172 172 Q147 100 204 74 Q247 51 300 81 Q343 110 327 169 L309 127 Q254 152 186 125 Z',curtain:'M170 180 Q141 105 204 72 Q253 50 302 76 Q349 106 330 185 L315 148 Q278 153 249 101 Q221 151 181 151 Z'}[a.hair];
  if(a.hair==='bun')face.insertBefore(ellipse(250,64,47,33,a.hair_color),face.firstChild);
  face.append(path(hair,a.hair_color));return root;
 }
 function mount(target,persona){target.replaceChildren();let src=null;if(persona.image_id&&/^[a-f0-9]{32}\.png$/.test(persona.image_id))src='/media/avatar/'+persona.image_id;else if(persona.avatar_asset&&/^avatars\/[a-z0-9-]+\.(png|jpe?g|webp)$/.test(persona.avatar_asset))src='/assets/'+persona.avatar_asset;if(src){let img=document.createElement('img');img.src=src;img.alt=(persona.name||'AI 業務顧問')+'角色主視覺（靜態圖片）';target.append(img)}else target.append(render(persona.avatar))}
 return {render,mount};
})();
