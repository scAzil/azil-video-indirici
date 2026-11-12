"""Install only into the app folder; no administrator rights required."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
import venv
import zipfile

BASE = Path(__file__).resolve().parent


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'AZiL-Video-Indirici/1.0'})
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def main():
    if sys.version_info < (3, 10):
        raise RuntimeError('Python 3.10 veya yenisi gerekli. python.org sitesinden kurun.')
    import tkinter
    target = BASE / '.venv'
    python = target / 'Scripts' / 'python.exe'
    if not python.exists():
        print('Uygulamaya ozel Python ortami hazirlaniyor...', flush=True)
        venv.create(target, with_pip=True)
    subprocess.run([str(python), '-m', 'pip', 'install', '--upgrade', 'yt-dlp[default]', 'imageio-ffmpeg'], check=True)
    print('YouTube icin Deno hazirlaniyor...', flush=True)
    release = json.loads(fetch('https://api.github.com/repos/denoland/deno/releases/latest'))
    name = 'deno-x86_64-pc-windows-msvc.zip'
    asset = next(a for a in release['assets'] if a['name'] == name)
    data = fetch(asset['browser_download_url'])
    digest = asset.get('digest') or ''
    if not digest.startswith('sha256:'):
        checksum = next(a for a in release['assets'] if a['name'] == name + '.sha256sum')
        digest = 'sha256:' + fetch(checksum['browser_download_url']).decode().split()[0]
    if hashlib.sha256(data).hexdigest().lower() != digest.split(':', 1)[1].lower():
        raise RuntimeError('Deno dosyasi dogrulanamadi; kurulum durduruldu.')
    tools = BASE / 'tools'
    tools.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        binary = archive.read('deno.exe')
    temporary = tools / 'deno.exe.tmp'
    temporary.write_bytes(binary)
    temporary.replace(tools / 'deno.exe')
    subprocess.run([str(python), '-m', 'yt_dlp', '--version'], check=True)
    subprocess.run([str(python), '-c', 'import imageio_ffmpeg, subprocess; subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-version"], check=True)'], check=True)
    subprocess.run([str(tools / 'deno.exe'), '--version'], check=True)
    (BASE / '.ready').write_text('1.0', encoding='utf-8')
    print('Kurulum tamamlandi.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('\nKurulum tamamlanamadi: ' + str(exc), flush=True)
        sys.exit(1)
