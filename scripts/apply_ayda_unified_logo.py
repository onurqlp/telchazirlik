#!/usr/bin/env python3
"""Unify AYDA logo in exam preparation HTML files without touching educational exercises."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
logo="https://www.aydadil.com/wp-content/uploads/2026/10/ayda-home-v89-baa791945bb954a30b.png"
css="""<style id="ayda-unified-logo-css">.ayda-shared-logo{display:inline-flex!important;align-items:center!important;gap:9px!important;text-decoration:none!important;color:#102541!important;max-width:100%}.ayda-shared-logo img{width:134px!important;max-width:min(134px,48vw)!important;height:auto!important;object-fit:contain!important;display:block!important;background:transparent!important;border:0!important;box-shadow:none!important}.ayda-shared-logo-bar{padding:9px 14px;background:#fff;border-bottom:1px solid #e4eaf0;display:flex;align-items:center;min-height:66px}@media(max-width:600px){.ayda-shared-logo img{width:112px!important}}</style>"""
js="""<script id="ayda-unified-logo-js">(function(){let logo='__LOGO__';let target=document.querySelector('header .brand,header .logo,header .top-brand,header .brand-mark,.topbar .brand,.site-header .brand,.navbar .brand,.brand-badge');if(target){if(target.tagName==='A'){target.classList.add('ayda-shared-logo');target.href='https://www.aydadil.com/';target.innerHTML='<img width="134" height="49" alt="AYDA Dil Akademisi" src="'+logo+'">'}else if(target.closest('a')){let a=target.closest('a');a.classList.add('ayda-shared-logo');a.href='https://www.aydadil.com/';a.innerHTML='<img width="134" height="49" alt="AYDA Dil Akademisi" src="'+logo+'">'}else{target.innerHTML='<img width="134" height="49" alt="AYDA Dil Akademisi" src="'+logo+'">';target.classList.add('ayda-shared-logo')}}else{let top=document.querySelector('header,main,.page,body');if(!top)return;let bar=document.createElement('div');bar.className='ayda-shared-logo-bar';bar.innerHTML='<a class="ayda-shared-logo" href="https://www.aydadil.com/" aria-label="AYDA Ana Sayfa"><img width="134" height="49" alt="AYDA Dil Akademisi" src="'+logo+'"></a>';top.prepend(bar)}})();</script>""".replace('__LOGO__',logo)
count=0
for f in root.rglob("*.html"):
 if any(x in f.parts for x in (".git","node_modules",".github","dist","build")):continue
 s=f.read_text(encoding="utf-8")
 if "ayda-unified-logo-css" in s:continue
 if not re.search(r"<body\b",s,re.I) or not re.search(r"</body\s*>",s,re.I):continue
 if re.search(r"</head\s*>",s,re.I):
  s=re.sub(r"</head\s*>",css+"</head>",s,count=1,flags=re.I)
 else:continue
 s=re.sub(r"</body\s*>",js+"</body>",s,count=1,flags=re.I)
 f.write_text(s,encoding="utf-8");count+=1
print("Unified canonical AYDA logo on",count,"HTML exam pages")
