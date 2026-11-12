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

    def test_progress_parsing(self):
        self.assertAlmostEqual(app.parse_progress_percent('12.3% | 1.2MiB/s'), 12.3)
        self.assertAlmostEqual(app.parse_progress_percent('99,9%'), 99.9)
        self.assertEqual(app.parse_progress_percent('100.8%'), 100)
        self.assertIsNone(app.parse_progress_percent('waiting for download'))

    def test_quality_selector_preserves_vertical_video(self):
        args = app.command('https://www.youtube.com/shorts/test', '/tmp', '1080p', False,
                           'ffmpeg', 'deno', status_mode=True)
        selector = args[args.index('-f') + 1]
        self.assertIn('width<=1920', selector)
        self.assertIn('height<=1920', selector)
        ordinary = app.command('https://www.youtube.com/shorts/test', '/tmp', '1080p', False,
                               'ffmpeg', 'deno')
        self.assertIn('height<=1080', ordinary[ordinary.index('-f') + 1])

    def test_url_validation(self):
        self.assertEqual(app.validate_url(' https://youtube.com/shorts/abc '),
                         'https://youtube.com/shorts/abc')
        with self.assertRaises(ValueError):
            app.validate_url('https://youtube.com.evil.example/shorts/abc')


if __name__ == '__main__':
    unittest.main()
