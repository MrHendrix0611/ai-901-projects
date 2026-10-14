"""Verificação básica offline; complemente com gitleaks/trufflehog antes de publicar."""
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
SKIP_DIRS={'node_modules','.venv','venv','.git','__pycache__'}
SKIP_SUFFIXES={'.png','.jpg','.jpeg','.gif','.ico','.pdf','.zip','.woff','.ttf','.pyc'}
checks=[
  ("Chave nomeada com valor não vazio", re.compile(r'(?im)^[ \t]*(?:AZURE_ML_KEY|AZURE_OPENAI_KEY|AZURE_DOCUMENT_INTELLIGENCE_KEY)[ \t]*=[ \t]*[^\s#]+')),
  ("Chave Azure escrita em código", re.compile(r'(?i)(?:(?:const|let|var)[ \t]+)?(?:apiKey|api_key|\bkey)[ \t]*[:=]\s*["\'](?!(?:SUA_|YOUR_|EXAMPLE|placeholder))[A-Za-z0-9+/=_-]{40,}["\']')),
  ("Token GitHub", re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}')),
  ("Chave privada", re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
]
problems=[]
for p in ROOT.rglob('*'):
  if not p.is_file() or any(x in SKIP_DIRS for x in p.parts) or p.suffix.lower() in SKIP_SUFFIXES:
    continue
  if p.name=='.env' or p.name.startswith('.env.') and p.name!='.env.example':
    problems.append(f'{p.relative_to(ROOT)}: arquivo de configuração privado')
    continue
  try:s=p.read_text('utf-8')
  except (UnicodeDecodeError,OSError):continue
  for label,pattern in checks:
    for match in pattern.finditer(s):
      # Arquivos .env.example só devem conter valor vazio; no README, placeholders documentados são aceitos.
      if p.name in {'README.md','SECURITY.md'}:
        continue
      problems.append(f'{p.relative_to(ROOT)}: {label} (linha {s.count(chr(10),0,match.start())+1})')
if problems:
  print('Possíveis informações sensíveis:')
  for issue in problems:print(' -',issue)
  sys.exit(1)
print('OK: nenhuma credencial detectada pelas regras locais. Faça revisão manual e gitleaks antes do push.')
