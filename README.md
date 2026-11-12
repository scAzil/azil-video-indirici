# AZiL Video İndirici

Windows için video indirme uygulaması. Program, kaynak ZIP üzerinden Python ortamında çalıştırılabilir.

## İndirme

- **[AZiL Video İndirici v1 — orijinal kaynak paketi](AZiL_Video_Indirici_v1.zip)** (`AZiL_Video_Indirici_v1.zip`): `app.py`, `setup_app.py`, `BASLAT.bat`, `GUNCELLE.bat` ve kullanım notları.
- [Alternatif hafif prototip](downloads/AZiL_Video_Indirici_Calistir.zip): Ayrı hazırlanmış Python uygulama paketi; orijinal v1 ile birebir aynı değildir.
- [Prototip EXE hazırlama paketi](downloads/AZiL_Video_Indirici_Hazirlama.zip): Prototip için derleme betikleri.

**Gereksinim:** Windows, Python 3.10+ ve ilk kurulumda internet erişimi. Orijinal paketi tamamen açın, içindeki kullanım notlarını okuyup `BASLAT.bat` ile başlayın.

## Geliştirilmekte olan Windows EXE — 9:16 telefon durumu ve yüzde göstergesi

Windows EXE aday sürümü GitHub **Actions** sayfasında `Build Windows x64 (candidate)` iş akışının başarılı çalışmasının altındaki **Artifacts** bölümünde bulunur. Resmî GitHub Release yayımlanana kadar bunlar test adaylarıdır.

- **İndirme yüzdesi:** İlerleme çubuğu, sayısal yüzde, kuyrukta her işin yüzdesi, hız ve kalan süre. yt-dlp ses/video parçalarını ayrı indirebildiği için yüzde her parçanın ilerlemesidir.
- **Telefon Durumu (9:16 MP4):** Video seçeneği yanında kutucuğu işaretle; YouTube Shorts veya başka bir desteklenen videoyu indirir, ardından **1080 × 1920, MP4, H.264, AAC, 30 fps** biçiminde ikinci bir dosya oluşturur. Çıktı adının sonuna `- Durum 9x16.mp4` eklenir.
- **Aynı, denenmiş indirme yöntemi:** Telefon Durumu modu da normal moddaki aynı yt-dlp kalite seçimini kullanır. Farklı filtreler yüzünden indirme hatası yaşanmasın diye yalnızca indirme tamamlandıktan sonra MP4 dönüşümü yapılır.
- **Dosyadan 9:16 MP4:** Bilgisayarda zaten bulunan MP4/MKV/WebM gibi videolar, yeniden indirilmeden `Dosyadan 9:16 MP4` düğmesinden kuyruğa alınır. `İndirmeyi başlat` işlemi yerel dönüşümü çalıştırır.
- **Hata raporu:** `Son hata ayrıntısını kopyala` düğmesi başarısız indirme veya dönüşümün son çıktı satırlarını panoya kopyalar. Paylaşmadan önce adres veya kişisel bilgi içerip içermediğini kontrol edin.
- **Kaynak video korunur:** İndirilen özgün dosya asla dönüşüm sırasında silinmez. Yalnızca başarısız dönüşümün yarım kalan çıktısı temizlenir.
- **Kuyruk kontrolü:** Aynı URL ikinci kez eklenmez. Başarısız işler yeniden sıraya alınabilir.
- **Kırpma davranışı:** Tam 9:16 çerçeveyi doldurmak için merkezden kırpar; 9:16 olmayan görüntülerin üst/alt veya sağ/sol bölümleri kesilebilir. Videonun kendi içine işlenmiş siyah kenarlar otomatik algılanmaz.
- **Kullanım:** Programı ayrı bir klasöre çıkar, EXE'yi çalıştır, kaydetme klasörünü belirle, bağlantıyı yapıştır, isteğe bağlı `Telefon Durumu (9:16 MP4)` kutucuğunu aç, `Kuyruğa ekle` ve `İndirmeyi başlat` düğmelerini kullan.

**Yayın durumu:** Windows için GitHub Actions test adayları mevcuttur ancak resmî GitHub Release hâlâ yoktur. Otomatik derleme testleri gerçek hizmetlerden yapılan indirme ve telefon uygulamasında görüntüleme testinin yerini tutmaz.

Yalnızca indirmeye yetkili olduğunuz içerikleri ilgili platformun kullanım koşulları ve hak sahiplerinin izinlerine uygun biçimde indirin.
