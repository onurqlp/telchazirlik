#!/usr/bin/env python3
"""Attach central AYDA password gate to every HTML page of this exam repository.
Do not expose files on screen before the central password system validates access.
Idempotent: leave an already-wrapped page untouched. G5 WordPress homepage is external.
"""
from pathlib import Path
import re,json
GATE_STYLE='''<style id="ayda-exam-access-guard">
html:not(.ayda-exam-authorized) #aydaProtectedContent{display:none!important}
html.ayda-exam-authorized #aydaLoginBox{display:none!important}
#aydaLoginBox{min-height:100dvh;display:grid;place-items:center;padding:22px;background:linear-gradient(135deg,#0b1b31,#214d75);font:15px system-ui,-apple-system,sans-serif;z-index:99999;position:relative}
#aydaLoginBox .ayda-exam-login-card{width:min(440px,100%);background:white;color:#102541;border-radius:18px;padding:28px;box-shadow:0 18px 44px #0003}
#aydaLoginBox h1{font:900 24px/1.25 system-ui;color:#102541;margin:0 0 10px}
#aydaLoginBox p{font:14px/1.5 system-ui;color:#52657c}
#aydaLoginBox label{display:block;margin:17px 0 8px;font-weight:800;color:#102541}
#aydaLoginBox input{display:block;width:100%;box-sizing:border-box;padding:12px;min-height:49px;border:1px solid #a9b9c9;border-radius:10px;font:16px system-ui;background:white;color:#102541}
#aydaLoginBox button{display:block;width:100%;min-height:48px;border:0;border-radius:10px;margin:12px 0;background:#102541;color:white;font:bold 15px system-ui;cursor:pointer}
#aydaLoginBox a{color:#214d75}
</style>'''
LOGIN='''<section id="aydaLoginBox" aria-label="AYDA sınav öğrenci girişi"><div class="ayda-exam-login-card"><p style="font-weight:900;letter-spacing:.1em;color:#a98442">AYDA DİL AKADEMİSİ</p><h1>Sınav Hazırlık · Öğrenci Girişi</h1><p>Devam etmek için merkezi AYDA sınıf kodunu girin.</p><label for="aydaPasswordInput">Giriş kodu</label><input id="aydaPasswordInput" type="password" autocomplete="off" placeholder="AYDA giriş kodunuz"><button type="button" onclick="aydaCheckPassword()">Giriş Yap</button><p id="aydaLoginMessage" role="status" aria-live="polite"></p><p><a href="https://www.aydadil.com/sinavhazirlik/">← Sınav Hazırlık Ana Sayfası</a></p></div></section>'''
TAIL='''<script src="https://onurqlp.github.io/ayda-pass/access-control.js" onerror="document.getElementById('aydaLoginMessage').textContent='Şifre hizmeti yüklenemedi.'"></script><script id="ayda-exam-authorization-sync">(function(){const p=document.getElementById('aydaProtectedContent');if(!p)return;function sync(){document.documentElement.classList.toggle('ayda-exam-authorized',p.style.display==='block')}new MutationObserver(sync).observe(p,{attributes:true,attributeFilter:['style']});sync()})();</script>'''
changed=[];skip=[];incomplete=[]
for p in sorted(Path(".").rglob("*.html")):
 if ".git" in p.parts or ".github" in p.parts or "node_modules" in p.parts:continue
 s=p.read_text(encoding="utf-8",errors="replace")
 if 'id="ayda-exam-access-guard"' in s or "id='ayda-exam-access-guard'" in s or ('id="aydaLoginBox"' in s and 'id="aydaProtectedContent"' in s):
  skip.append(str(p));continue
 if not re.search(r"<body\b",s,re.I) or not re.search(r"</body\s*>",s,re.I):
  incomplete.append(str(p));continue
 if re.search(r"<head\b[^>]*>",s,re.I):
  s=re.sub(r"<head\b[^>]*>",lambda m:m.group(0)+GATE_STYLE,s,count=1,flags=re.I)
 else:
  s=re.sub(r"<html\b[^>]*>",lambda m:m.group(0)+GATE_STYLE,s,count=1,flags=re.I)
 s=re.sub(r"<body\b([^>]*)>",lambda m:"<body"+m.group(1)+">"+LOGIN+'<div id="aydaProtectedContent" style="display:none">',s,count=1,flags=re.I)
 s=re.sub(r"</body\s*>",lambda m:"</div>"+TAIL+m.group(0),s,count=1,flags=re.I)
 p.write_text(s,encoding="utf-8");changed.append(str(p))
result={"changed_count":len(changed),"skipped_already_protected":len(skip),"unhandled":incomplete,"changed_examples":changed[:20]}
Path("ayda-exam-guard-report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
if incomplete:raise SystemExit("Some HTML files had no recognizable body; manual review required")
