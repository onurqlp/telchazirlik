#!/usr/bin/env python3
"""Apply existing approved AYDA central classroom gate to every HTML exam page."""
import pathlib,re
root=pathlib.Path(__file__).resolve().parents[1]
ref=(root/"index.html").read_text(encoding="utf-8")
def part(a,b):
 start=ref.find(a)
 if start<0:raise RuntimeError("missing gate reference "+a)
 end=ref.find(b,start)
 if end<0:raise RuntimeError("unclosed gate")
 return ref[start:end+len(b)]
css=part('<style id="ayda-exam-access-guard">','</style>')
gate=part('<section id="aydaLoginBox"','</section>')
s=ref.find('<script src="https://onurqlp.github.io/ayda-pass/access-control.js"')
e=ref.find('</script>',ref.find('<script id="ayda-exam-authorization-sync">'))
if s<0 or e<0:raise RuntimeError("missing central access script")
tail=ref[s:e+9]
changed=[]
skipped=[]
for p in root.rglob("*.html"):
 if any(v in p.parts for v in (".git","node_modules",".github","g4-preview","g5-production")):continue
 content=p.read_text(encoding="utf-8")
 if 'id="ayda-exam-access-guard"' in content or 'id="ayda-exam-authorization-sync"' in content or ("access-control.js" in content and 'id="aydaLoginBox"' in content):
  skipped.append(str(p.relative_to(root)));continue
 if not re.search(r"<head\b",content,re.I) or not re.search(r"<body\b",content,re.I) or not re.search(r"</body\s*>",content,re.I):
  skipped.append(str(p.relative_to(root))+" [unsupported]");continue
 content=re.sub(r"(<head\b[^>]*>)",lambda m:m.group(1)+css,content,count=1,flags=re.I)
 content=re.sub(r"(<body\b[^>]*>)",lambda m:m.group(1)+gate+'<div id="aydaProtectedContent" style="display:none">',content,count=1,flags=re.I)
 content=re.sub(r"</body\s*>","</div>"+tail+"</body>",content,count=1,flags=re.I)
 p.write_text(content,encoding="utf-8")
 changed.append(str(p.relative_to(root)))
print("AYDA G5 protected",len(changed),"pages; preexisting/unsupported",len(skipped))
for p in changed[:20]:print("SECURED",p)
for p in skipped:
 if "[unsupported]" in p:print("UNSUPPORTED",p)
