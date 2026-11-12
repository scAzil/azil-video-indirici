"""AZiL Video İndirici — Windows, Python 3.10+."""
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urlsplit

# Frozen one-file executables unpack resources to sys._MEIPASS.
# User files and settings must not be stored inside the temporary bundle.
FROZEN = bool(getattr(sys, 'frozen', False))
BASE = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent
RESOURCES = Path(getattr(sys, '_MEIPASS', BASE))
STATE = Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'AZiLVideoIndirici'
QUALITIES = {'En iyi': None, '2160p / 4K': 2160, '1440p': 1440, '1080p': 1080, '720p': 720, '480p': 480}
FLAGS = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def validate_url(value):
    value = value.strip()
    try:
        p = urlsplit(value)
        host = (p.hostname or '').lower()
        allowed = ('youtube.com', 'youtu.be', 'x.com', 'twitter.com')
        if p.scheme not in ('https', 'http') or p.username or p.password or p.port not in (None, 80, 443):
            raise ValueError()
        if not any(host == d or host.endswith('.' + d) for d in allowed):
            raise ValueError()
        if not p.path or p.path == '/':
            raise ValueError()
    except ValueError:
        raise ValueError('YouTube veya X video bağlantısı girin.')
    return value


def command(url, folder, quality, audio, ffmpeg, deno):
    # A PyInstaller EXE cannot run 'python -m yt_dlp'. Re-enter this EXE
    # in a CLI-only worker mode, keeping its GUI separate from the downloader.
    runner = [sys.executable, '--azil-worker'] if FROZEN else [sys.executable, '-m', 'yt_dlp']
    args = runner + ['--ignore-config', '--no-playlist',
            '--no-colors', '--newline', '--windows-filenames', '--no-overwrites',
            '--socket-timeout', '25', '--retries', '3', '--fragment-retries', '3',
            '--ffmpeg-location', str(ffmpeg), '--js-runtimes', 'deno:' + str(deno),
            '--progress-template', 'download:AZIL_PROGRESS:%(progress._percent_str)s | %(progress._speed_str)s | kalan %(progress._eta_str)s',
            '--print', 'after_move:AZIL_FILE:%(filepath)s', '--no-simulate',
            '-P', str(folder), '-o', '%(title).150B [%(id)s].%(ext)s']
    if audio:
        args += ['-f', 'bestaudio/best', '-x', '--audio-format', 'mp3', '--audio-quality', '192K']
    else:
        height = QUALITIES[quality]
        limit = f'[height<={height}]' if height else ''
        args += ['-f', f'bv*{limit}+ba/b{limit}', '--merge-output-format', 'mkv']
    return args + ['--', url]


class App:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.jobs = {}
        self.busy = False
        self.cancel_event = threading.Event()
        self.proc = None
        self.lock = threading.Lock()
        self.closing = False
        STATE.mkdir(parents=True, exist_ok=True)
        self.settings = STATE / 'settings.json'
        try:
            saved = json.loads(self.settings.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            saved = {}
        self.folder = tk.StringVar(value=saved.get('folder', str(Path.home() / 'Downloads' / 'AZiL')))
        self.quality = tk.StringVar(value='1080p')
        self.audio = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='Hazır • Bağlantıyı yapıştırın ve kuyruğa ekleyin.')
        root.title('AZiL • Video İndirici 1.0')
        root.geometry('980x740')
        root.minsize(790, 610)
        root.configure(bg='#101823')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=('Segoe UI', 10), background='#172231', foreground='#edf2fa')
        style.configure('TButton', padding=9, background='#263b50')
        style.map('TButton', background=[('active', '#36546e')])
        style.configure('TEntry', fieldbackground='#263b50', foreground='white')
        style.configure('TCombobox', fieldbackground='#263b50', foreground='white')
        style.map('TCombobox', fieldbackground=[('readonly', '#263b50')], foreground=[('readonly', 'white')])
        style.configure('Treeview', background='#101823', fieldbackground='#101823', foreground='#edf2fa', rowheight=30)
        style.configure('Treeview.Heading', background='#263b50', padding=7)
        outer = ttk.Frame(root, padding=22)
        outer.pack(fill='both', expand=True, padx=12, pady=12)
        ttk.Label(outer, text='AZiL  /  Video İndirici', font=('Segoe UI', 23, 'bold')).pack(anchor='w')
        ttk.Label(outer, text='Bağlantıdan dosyaya. Reklamsız, bilgisayarınızda.', foreground='#6edbc8').pack(anchor='w', pady=(2, 18))
        ttk.Label(outer, text='YouTube veya X bağlantıları • Her satıra bir bağlantı').pack(anchor='w')
        self.urls = tk.Text(outer, height=3, bg='#101823', fg='white', insertbackground='white', font=('Segoe UI', 11), relief='flat', padx=10, pady=8)
        self.urls.pack(fill='x', pady=7)
        bar = ttk.Frame(outer)
        bar.pack(fill='x')
        ttk.Button(bar, text='Panodan yapıştır', command=self.paste).pack(side='left')
        ttk.Button(bar, text='Kuyruğa ekle', command=self.add).pack(side='left', padx=8)
        ttk.Checkbutton(bar, text='Yalnızca ses (MP3)', variable=self.audio).pack(side='right')
        ttk.Combobox(bar, textvariable=self.quality, values=list(QUALITIES), state='readonly', width=14).pack(side='right', padx=8)
        pathbar = ttk.Frame(outer)
        pathbar.pack(fill='x', pady=14)
        ttk.Label(pathbar, text='Kayıt klasörü:').pack(side='left')
        ttk.Entry(pathbar, textvariable=self.folder).pack(side='left', fill='x', expand=True, padx=8)
        ttk.Button(pathbar, text='Seç', command=self.choose).pack(side='left')
        ttk.Button(pathbar, text='Klasörü aç', command=self.open_folder).pack(side='left', padx=(8, 0))
        table = ttk.Frame(outer)
        table.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(table, columns=('url', 'mode', 'status'), show='headings', selectmode='extended', height=7)
        for key, label, width in [('url', 'Bağlantı / Dosya', 430), ('mode', 'Seçim', 110), ('status', 'Durum', 170)]:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, minwidth=70)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll = ttk.Scrollbar(table, command=self.tree.yview)
        scroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.bind('<Double-1>', self.open_file)
        buttons = ttk.Frame(outer)
        buttons.pack(fill='x', pady=12)
        self.start_button = ttk.Button(buttons, text='İndirmeyi başlat', command=self.start)
        self.start_button.pack(side='left')
        ttk.Button(buttons, text='Durdur', command=self.stop).pack(side='left', padx=8)
        ttk.Button(buttons, text='Seçileni kaldır', command=self.remove).pack(side='left')
        ttk.Button(buttons, text='Hatalıları yeniden sıraya al', command=self.retry).pack(side='right')
        self.progress = ttk.Progressbar(outer, maximum=100)
        self.progress.pack(fill='x')
        ttk.Label(outer, textvariable=self.status, wraplength=850).pack(anchor='w', pady=8)
        self.log = tk.Text(outer, height=5, bg='#101823', fg='#aac0d6', font=('Consolas', 9), relief='flat', state='disabled')
        self.log.pack(fill='x')
        ttk.Label(outer, text='Kalite seçimi üst sınırdır. Video MKV veya kaynağın biçiminde; ses MP3 olarak kaydedilir.', foreground='#aac0d6', font=('Segoe UI', 9)).pack(anchor='w', pady=(8, 0))
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.poll)

    def paste(self):
        try:
            text = self.root.clipboard_get()
            self.urls.insert('end', ('\n' if self.urls.get('1.0', 'end').strip() else '') + text)
        except tk.TclError:
            self.status.set('Panoda metin bulunamadı.')

    def choose(self):
        value = filedialog.askdirectory()
        if value:
            self.folder.set(value)

    def add(self):
        lines = [v.strip() for v in self.urls.get('1.0', 'end').splitlines() if v.strip()]
        if not lines:
            return
        try:
            links = [validate_url(v) for v in lines]
        except ValueError as exc:
            messagebox.showerror('Bağlantı', str(exc))
            return
        for url in links:
            mode = 'MP3' if self.audio.get() else self.quality.get()
            iid = self.tree.insert('', 'end', values=(url, mode, 'Bekliyor'))
            self.jobs[iid] = dict(url=url, quality=self.quality.get(), audio=self.audio.get(), state='Bekliyor', file=None)
        self.urls.delete('1.0', 'end')
        self.status.set(f'{len(links)} bağlantı eklendi. Ayarlar ekleme anında kaydedildi.')

    def open_folder(self):
        try:
            folder = Path(self.folder.get()).expanduser()
            folder.mkdir(parents=True, exist_ok=True)
            os.startfile(str(folder.resolve()))
        except OSError as exc:
            messagebox.showerror('Klasör', str(exc))

    def open_file(self, event=None):
        for iid in self.tree.selection()[:1]:
            path = self.jobs[iid].get('file')
            if path and Path(path).is_file():
                try:
                    os.startfile(path)
                except OSError as exc:
                    messagebox.showerror('Dosya açılamadı', str(exc))

    def remove(self):
        for iid in self.tree.selection():
            if self.jobs[iid]['state'] != 'İndiriliyor':
                self.jobs.pop(iid)
                self.tree.delete(iid)

    def retry(self):
        for iid, job in self.jobs.items():
            if job['state'] in ('Hata', 'Durduruldu'):
                job['state'] = 'Bekliyor'
                self.tree.set(iid, 'status', 'Bekliyor')

    def start(self):
        if self.busy:
            return
        try:
            import imageio_ffmpeg
            self.ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            # In a one-file EXE Deno is bundled into its extracted resources.
            # In the original Python/BAT distribution it lives beside app.py.
            self.deno = RESOURCES / 'tools' / 'deno.exe'
            if not self.deno.is_file():
                if FROZEN:
                    raise RuntimeError('Deno EXE paketinde bulunamadı; yeni sürümü indirin.')
                raise RuntimeError('Deno eksik. GUNCELLE.bat dosyasını çalıştırın.')
            folder = Path(self.folder.get()).expanduser().resolve()
            folder.mkdir(parents=True, exist_ok=True)
            self.settings.write_text(json.dumps({'folder': str(folder)}, ensure_ascii=False), encoding='utf-8')
        except Exception as exc:
            messagebox.showerror('Hazırlık', str(exc))
            return
        self.active_folder = folder
        self.cancel_event.clear()
        self.busy = True
        self.start_button.state(['disabled'])
        self.next_job()

    def next_job(self):
        if not self.cancel_event.is_set():
            for iid, job in self.jobs.items():
                if job['state'] == 'Bekliyor':
                    job['state'] = 'İndiriliyor'
                    self.tree.set(iid, 'status', 'İndiriliyor')
                    self.progress['value'] = 0
                    self.status.set('Bağlantı çözümleniyor…')
                    threading.Thread(target=self.worker, args=(iid, dict(job)), daemon=True).start()
                    return
        self.busy = False
        self.start_button.state(['!disabled'])
        self.status.set('Durduruldu. Bekleyenler için yeniden başlatabilirsiniz.' if self.cancel_event.is_set() else 'Kuyruk tamamlandı. Sonuçları durum sütunundan kontrol edin.')
        if self.closing:
            self.root.destroy()

    def worker(self, iid, job):
        code = 1
        try:
            args = command(job['url'], self.active_folder, job['quality'], job['audio'], self.ffmpeg, self.deno)
            with self.lock:
                if self.cancel_event.is_set():
                    self.events.put(('done', iid, 'Durduruldu'))
                    return
                self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=FLAGS)
                proc = self.proc
            for line in proc.stdout:
                self.events.put(('line', iid, line.rstrip()))
            proc.stdout.close()
            code = proc.wait()
        except Exception as exc:
            self.events.put(('line', iid, 'Hata: ' + str(exc)))
        finally:
            with self.lock:
                self.proc = None
        self.events.put(('done', iid, 'Durduruldu' if self.cancel_event.is_set() else ('Tamamlandı' if code == 0 else 'Hata')))

    def stop(self):
        if not self.busy:
            return
        self.cancel_event.set()
        self.status.set('İndirme durduruluyor…')
        def kill():
            with self.lock:
                proc = self.proc
                if proc and proc.poll() is None:
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=FLAGS)
                    else:
                        proc.terminate()
        threading.Thread(target=kill, daemon=True).start()

    def poll(self):
        try:
            for _ in range(150):
                kind, iid, value = self.events.get_nowait()
                if iid not in self.jobs:
                    continue
                if kind == 'done':
                    self.jobs[iid]['state'] = value
                    self.tree.set(iid, 'status', value)
                    if value == 'Tamamlandı':
                        self.progress['value'] = 100
                    self.root.after(50, self.next_job)
                elif value.startswith('AZIL_FILE:'):
                    path = value[len('AZIL_FILE:'):]
                    self.jobs[iid]['file'] = path
                    self.tree.set(iid, 'url', Path(path).name)
                elif value.startswith('AZIL_PROGRESS:'):
                    progress = value[len('AZIL_PROGRESS:'):].strip()
                    match = re.search(r'(\d+(?:\.\d+)?)%', progress)
                    if match:
                        self.progress['value'] = float(match.group(1))
                    self.status.set(progress)
                else:
                    self.log.configure(state='normal')
                    self.log.insert('end', value + '\n')
                    if int(self.log.index('end-1c').split('.')[0]) > 250:
                        self.log.delete('1.0', '50.0')
                    self.log.see('end')
                    self.log.configure(state='disabled')
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def close(self):
        if self.busy:
            if not messagebox.askyesno('Çıkış', 'Etkin indirmeyi durdurup çıkılsın mı?'):
                return
            self.closing = True
            self.stop()
        else:
            self.root.destroy()


def self_test(report):
    """Headless CI check that bundled runtime components exist and run."""
    result = {'frozen': FROZEN, 'runtime_dir': str(RESOURCES)}
    try:
        import yt_dlp
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        deno = RESOURCES / 'tools' / 'deno.exe'
        if not Path(ffmpeg).is_file():
            raise RuntimeError('FFmpeg not found: ' + str(ffmpeg))
        if not deno.is_file():
            raise RuntimeError('Deno not found: ' + str(deno))
        for name, program in (('deno', str(deno)), ('ffmpeg', str(ffmpeg))):
            checked = subprocess.run([program, '-version' if name == 'ffmpeg' else '--version'],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, timeout=20, creationflags=FLAGS)
            result[name] = checked.returncode
            if checked.returncode != 0:
                raise RuntimeError(name + ' failed: ' + checked.stdout[-1000:])
        result['yt_dlp'] = yt_dlp.version.__version__
        result['ok'] = True
        code = 0
    except Exception as exc:
        result['ok'] = False
        result['error'] = str(exc)
        code = 1
    Path(report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return code


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--azil-worker':
        # Run yt-dlp CLI in this EXE, without opening a second GUI window.
        from yt_dlp import main
        sys.argv = ['yt-dlp'] + sys.argv[2:]
        main()
    elif len(sys.argv) == 3 and sys.argv[1] == '--azil-self-test':
        sys.exit(self_test(sys.argv[2]))
    else:
        root = tk.Tk()
        App(root)
        root.mainloop()
