"""Scan source and Git-tracked project files; report locations only, never matches."""
from pathlib import Path
import re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
PATTERNS=[('service-key',re.compile(r'\bsk-[A-Za-z0-9_-]{24,}')),('bearer-value',re.compile(r'Bearer\s+[A-Za-z0-9_.-]{25,}')),('private-key',re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),('jwt',re.compile(r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}')),('assigned-secret',re.compile(r'''(?i)(?:api_key|access_token|refresh_token|password)\s*[=:]\s*["'][^"'\s]{20,}["']'''))]
files=set(p for p in ROOT.rglob('*') if p.is_file() and not any(x in p.relative_to(ROOT).parts for x in ['.venv','__pycache__','data','.git']))
try:
 result=subprocess.run(['git','ls-files','-z','--',str(ROOT)],cwd=ROOT,capture_output=True,check=True)
 gitroot=Path(subprocess.run(['git','rev-parse','--show-toplevel'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip())
 files.update(gitroot/x for x in result.stdout.decode().split('\0') if x)
except (subprocess.SubprocessError,FileNotFoundError):pass
findings=[];count=0
for p in sorted(files):
 if p.suffix.lower() not in {'.py','.js','.css','.html','.md','.txt','.sh','.json','.example','.toml','.yml','.yaml'}:continue
 if not p.is_relative_to(ROOT) or not p.exists():continue
 text=p.read_text(errors='replace');count+=1
 # Embedded legacy image bytes are assets, not credential text.
 text=re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+','[embedded image]',text)
 for name,pattern in PATTERNS:
  for m in pattern.finditer(text):findings.append((str(p.relative_to(ROOT)),text.count('\n',0,m.start())+1,name))
print(f'Scanned {count} source files; {len(findings)} potential secrets.')
for path,line,kind in findings:print(f'{path}:{line} [{kind}]')
print('Pattern scan only; does not inspect credential stores, ignored user data, or Git history.')
sys.exit(bool(findings))
