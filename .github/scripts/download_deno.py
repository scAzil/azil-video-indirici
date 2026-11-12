"""Fetch Deno for the standalone Windows build, verifying GitHub's SHA-256."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import urllib.request
import zipfile

API = 'https://api.github.com/repos/denoland/deno/releases/latest'
NAME = 'deno-x86_64-pc-windows-msvc.zip'


def fetch(url, token=False):
    headers = {'User-Agent': 'AZiL-Video-Indirici-CI/1.0'}
    if token and os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


release = json.loads(fetch(API, token=True))
asset = next(a for a in release['assets'] if a['name'] == NAME)
archive = fetch(asset['browser_download_url'])
digest = asset.get('digest') or ''
if digest.startswith('sha256:'):
    expected = digest.split(':', 1)[1].strip().lower()
else:
    checksum = next(a for a in release['assets'] if a['name'] == NAME + '.sha256sum')
    expected = fetch(checksum['browser_download_url']).decode('utf-8').split()[0].lower()
actual = hashlib.sha256(archive).hexdigest().lower()
if actual != expected:
    raise RuntimeError('Deno SHA-256 verification FAILED')
with zipfile.ZipFile(io.BytesIO(archive)) as z:
    names = [n for n in z.namelist() if n.replace('\\', '/').split('/')[-1].lower() == 'deno.exe']
    if len(names) != 1:
        raise RuntimeError('Expected exactly one Deno binary in verified archive')
    data = z.read(names[0])
out = Path('vendor/deno.exe')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(data)
subprocess.run([str(out.resolve()), '--version'], check=True, timeout=20)
print('Verified Deno release:', release['tag_name'], 'sha256:', actual)
