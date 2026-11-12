# AZiL Video İndirici

**Windows 10/11 (64-bit) için kurulumsuz video indirici.** YouTube ve X bağlantıları, MP3 seçeneği, indirme yüzdesi ve telefon durumu için 9:16 MP4 dönüştürme.

## Resmî sürüm — v1.0.0

**[GitHub Releases — AZiL Video İndirici v1.0.0](https://github.com/scAzil/azil-video-indirici/releases/tag/v1.0.0)**

- **[Windows EXE'yi doğrudan indir](https://github.com/scAzil/azil-video-indirici/releases/download/v1.0.0/AZiL_Video_Indirici.exe)** — Windows 10/11 x64, yaklaşık 107 MB.
- **[Taşınabilir ZIP'i indir](https://github.com/scAzil/azil-video-indirici/releases/download/v1.0.0/AZiL_Video_Indirici_v1.0.0_Windows_x64.zip)** — aynı EXE'yi içerir, kurulum gerektirmez.
- [SHA-256 değerleri](https://github.com/scAzil/azil-video-indirici/releases/download/v1.0.0/SHA256SUMS.txt) ve [yayın kaynak/test kaydı](https://github.com/scAzil/azil-video-indirici/releases/download/v1.0.0/BUILD_PROVENANCE.txt).

**Python kurmak veya GUNCELLE.bat çalıştırmak gerekmez.** İndirilen EXE'yi açın veya ZIP'i bir klasöre çıkarıp içindeki EXE'yi çalıştırın. Dijital kod imzası henüz bulunmadığından Windows güvenlik uyarılarını değerlendirerek ilerleyin.

## Özellikler

- YouTube ve X bağlantılarını kuyruğa ekleme, video kalitesi seçimi ve MP3 indirme
- Sayısal yüzde, ilerleme çubuğu, indirme hızı ve kalan süre
- **Telefon Durumu (9:16 MP4):** Normal indirme bittikten sonra 1080×1920 H.264/AAC MP4 oluşturur; kaynak videoyu silmez
- **Dosyadan 9:16 MP4:** Bilgisayardaki bir videoyu yeniden indirmeden telefon paylaşımı için dönüştürür
- Türkçe karakterli başlıklarda UTF-8 dosya adı desteği ve dosya kimliğiyle kurtarma
- yt-dlp-ejs, Deno ve FFmpeg bileşenleri; hata kaydını kopyalama ve başarısız işleri yeniden deneme

Durum videoları 9:16 çerçeveyi doldurmak için ortadan kırpılabilir; kaynak görüntünün içine gömülü siyah kenarlar her zaman kaldırılamayabilir.

## Orijinal kaynak ve eski prototipler

- **[Orijinal v1 Python ZIP](AZiL_Video_Indirici_v1.zip):** `app.py`, `setup_app.py`, `BASLAT.bat`, `GUNCELLE.bat` ve kullanım notları. Bu eski yöntem için Windows, Python 3.10+ ve ilk kurulumda internet gerekir.
- **[Geliştirilmiş Python kaynak kodu](source-v1/app.py)** ve [Windows derleme iş akışı](.github/workflows/windows-build.yml).
- [Eski hafif prototip](downloads/AZiL_Video_Indirici_Calistir.zip) — resmî EXE ile aynı sürüm değildir.
- [Eski prototip derleme araçları](downloads/AZiL_Video_Indirici_Hazirlama.zip).

**Lisans ve kullanım:** [Üçüncü taraf bileşen notlarını](THIRD_PARTY_NOTICES.md) inceleyin. Yalnızca indirme ve paylaşma yetkiniz bulunan içerikleri ilgili platform koşullarına ve telif haklarına uygun biçimde kullanın.
