"""Small, offline checks for GUI-independent AZiL downloader functions."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

APP_PATH = Path(__file__).resolve().parents[1] / 'source-v1' / 'app.py'
spec = importlib.util.spec_from_file_location('azil_app', APP_PATH)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class VideoDownloaderTests(unittest.TestCase):
    def test_phone_status_dimensions_and_codecs(self):
        args = app.status_ffmpeg_args('ffmpeg.exe', 'original.mkv', 'status.mp4')
        vf = args[args.index('-vf') + 1]
        self.assertIn('1080:1920', vf)
        self.assertIn('force_original_aspect_ratio=increase', vf)
        self.assertIn('crop=1080:1920', vf)
        self.assertNotIn('pad=', vf)
        self.assertIn('libx264', args)
        self.assertIn('yuv420p', args)
        self.assertIn('aac', args)
        self.assertIn('+faststart', args)

    def test_status_output_preserves_original_and_avoids_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'short.mkv'
            source.write_bytes(b'original')
            first = app.status_output_path(source)
            self.assertEqual(first.name, 'short - Durum 9x16.mp4')
            first.write_bytes(b'other')
            second = app.status_output_path(source)
            self.assertEqual(second.name, 'short - Durum 9x16 (2).mp4')
            self.assertEqual(source.read_bytes(), b'original')
            self.assertEqual(first.read_bytes(), b'other')

    def test_turkish_filename_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            real = Path(folder) / 'satın aldığım koltuğa başkası oturdu [BdSgGtHHFNw].mkv'
            real.write_bytes(b'video')
            mojibake = str(Path(folder) / 'sat�n ald���m koltu�a ba�kas� oturdu [BdSgGtHHFNw].mkv')
            resolved = app.recover_downloaded_file(
                mojibake, folder, 'https://www.youtube.com/shorts/BdSgGtHHFNw')
            self.assertEqual(resolved, real)
            self.assertEqual(app.recover_downloaded_file(str(real), folder), real)
            self.assertIsNone(app.recover_downloaded_file(None, folder, 'https://youtu.be/fail12345'))
            self.assertEqual(app.utf8_subprocess_env()['PYTHONIOENCODING'], 'utf-8:replace')

    def test_ejs_and_utf8_flags(self):
        args = app.command('https://www.youtube.com/shorts/BdSgGtHHFNw',
                           '/tmp', '1080p', False, 'ffmpeg', 'deno', status_mode=True)
        self.assertEqual(args[args.index('--remote-components') + 1], 'ejs:github')
        self.assertEqual(args[args.index('--encoding') + 1], 'utf-8')

    def test_progress_parsing(self):
        self.assertAlmostEqual(app.parse_progress_percent('12.3% | 1.2MiB/s'), 12.3)
        self.assertAlmostEqual(app.parse_progress_percent('99,9%'), 99.9)
        self.assertEqual(app.parse_progress_percent('100.8%'), 100)
        self.assertIsNone(app.parse_progress_percent('waiting for download'))

    def test_phone_mode_uses_same_proven_download_as_normal(self):
        url = 'https://www.youtube.com/shorts/test'
        for quality in ('1080p', '720p', 'En iyi'):
            args = app.command(url, '/tmp', quality, False, 'ffmpeg', 'deno',
                               status_mode=True)
            ordinary = app.command(url, '/tmp', quality, False, 'ffmpeg', 'deno')
            self.assertEqual(args, ordinary)
            self.assertIn('-f', args)
        args = app.command(url, '/tmp', '1080p', False, 'ffmpeg', 'deno')
        self.assertIn('height<=1080', args[args.index('-f') + 1])

    def test_url_validation(self):
        self.assertEqual(app.validate_url(' https://youtube.com/shorts/abc '),
                         'https://youtube.com/shorts/abc')
        with self.assertRaises(ValueError):
            app.validate_url('https://youtube.com.evil.example/shorts/abc')


if __name__ == '__main__':
    unittest.main()
