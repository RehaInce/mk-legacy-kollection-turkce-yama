# Mortal Kombat: Legacy Kollection — Türkçe Yama

Mortal Kombat: Legacy Kollection (PC) için gayriresmî Türkçe çeviri. Türkçe, oyunun dil menüsüne **TÜRKÇE** adıyla ayrı bir seçenek olarak eklenir. İngilizce ve diğer diller değişmez.

**Çevrilenler:** menüler, ayarlar, karakter biyografileri ve sonları, müzedeki yapım hikâyesi ve tarihçe metinleri, hareket listeleri, başarımlar. Toplam 3093 metnin 2916'sı çevrildi. Kalanlar karakter, oyun ve platform adları gibi özel isimler.

**Sınırlamalar**
- Oyunun fontlarında `ğ ş ı İ` harfleri yok. Bu harfler `g s i I` olarak gösterilir. `ç ö ü` sorunsuz görünür.
- Derlemedeki orijinal oyunların metinleri ROM'ların içinde. Şimdilik yalnızca **arcade Mortal Kombat (1992)** çevrildi (aşağıya bak). Diğerleri İngilizce kalıyor.

## Kurulum

Gerekenler: Windows ve [Python 3.8+](https://www.python.org/downloads/).

1. Bu depoyu (ya da [Releases](../../releases) sayfasındaki zip'i) oyun klasöründe `Turkce_Yama` adlı bir klasöre çıkar. Klasörün `assets.pie` ile aynı yerde olması gerekir.
2. Oyunu aç ve ana menüye kadar gel. `1_Orijinal_Metni_Cikar.bat` dosyasını çalıştır (yönetici izni ister). Bu adım, oyunun dil dosyasını senin kopyandan çıkarır. Telif hakkı nedeniyle bu dosya depoda yer almıyor.
3. Oyunu kapat ve `2_Turkce_Yamayi_Uygula.bat` dosyasını çalıştır.
4. Oyunda **OPTIONS → GAME OPTIONS → LANGUAGE** yolundan **TÜRKÇE**'yi seç.

**Geri almak için:** `Orijinale_Geri_Don.bat`. Yamalayıcı, değiştirdiği byte'ların orijinallerini ilk çalıştırmada `assets.pie.tr-backup` dosyasına yedekler.

**Oyun güncellenirse:** Yamalar arşivin belirli bir sürümüne göre yazıldı. Güncellemeden sonra Türkçe kaybolursa yamayı yeniden uygulamadan önce bir issue aç.

## Arcade Mortal Kombat (1992) yaması

Oyunun içindeki 162 metnin tamamı çevrildi: biyografiler, karakter sonları, "BİTİR ONU !!", "RAUNT 1", "DÖVÜŞÇÜNÜ SEÇ", "KUSURSUZ ZAFER", tanıtım ekranları ve Reptile ipuçları. Oyunun üç fontuna `Ç Ğ İ Ö Ş Ü` harfleri piksel piksel çizilip eklendi.

1. Oyunu aç ve **arcade Mortal Kombat**'ı başlat. Başlık ekranı gelince `MK1_1_ROM_Cikar.bat` dosyasını çalıştır (yönetici izni ister). Bu adım ROM'ları senin kopyandan `mk1/` klasörüne çıkarır.
2. Oyunu kapat ve `MK1_2_Turkce_Yamayi_Uygula.bat` dosyasını çalıştır.

**Geri almak için:** `MK1_Orijinale_Geri_Don.bat`. Orijinal byte'lar `assets.pie.mkr4.maincpu.bak` ve `assets.pie.mk.gfxrom.bak` dosyalarına yedeklenir.

**Çeviriye katkı:** `mk1/mk1_tr.json` dosyasında `"0xADRES": "METİN"` biçiminde duruyor. `|` satır sonu demek. `%d`, `%p` ve `%,ld` aynen kalmalı. Pointer'ı olmayan metinler orijinalinden uzun olamaz, `build_mk1.py` bunu kontrol eder. Test için `mk1/test/` klasöründeki betikler [MAME 0.264](https://github.com/mamedev/mame/releases/tag/mame0264) ile oyunu görüntüsüz çalıştırır:
- `check.sh`: çökme testi
- `run.sh`: otomatik bir oyun oynayıp ekran görüntüleri alır
- `bisect_mk1.py`: oyunu çökerten metni bulur

## Game Boy Mortal Kombat yaması

Biyografiler, dövüş yazıları, menüler ve final metni çevrildi. Game Boy fontunda boş yer olmadığından Türkçe harfler, Türkçede kullanılmayan `Q X` ile yalnızca telif ekranında geçen `© ®` karakterlerinin yerine çizildi. Böylece `Ç Ö Ş Ü` var; `Ğ` ve `İ` ise `G` ve `I` olarak görünür.

1. Oyunda **Game Boy Mortal Kombat**'ı aç. Oyun başlayınca `GB_1_ROM_Cikar.bat` dosyasını çalıştır (yönetici izni ister).
2. Oyunu kapat ve `GB_2_Turkce_Yamayi_Uygula.bat` dosyasını çalıştır.

**Geri almak için:** `GB_Orijinale_Geri_Don.bat`.

**Çeviriye katkı:** `gb/gb_mk1_tr.json` dosyasında `"0xBLOK": ["satır", ...]` biçiminde duruyor. Her blok, orijinaliyle aynı sayıda satır içermeli. Satırlar en fazla 20 karakter olabilir ve blok orijinalinden uzun olamaz; `gb_build.py` bu kuralları kontrol eder. Fontta kesme işareti yok, ekler doğrudan isme yazılır (KANOYU). Test için: `gb/test/run.sh`.

## Game Gear Mortal Kombat yaması

Karakter sonları, Goro'nun hikâyesi, açılıştaki "kod" metinleri, dövüş yazıları, menüler ve rekor ekranı çevrildi. Fonttaki kullanılmayan küçük harflerin yerine `Ç Ğ İ Ö Ş Ü` çizildi, yani bütün Türkçe harfler var. Başlık ekranındaki "PRESS START" bir resim olduğundan İngilizce kaldı.

1. Oyunda **Game Gear Mortal Kombat**'ı aç. Oyun başlayınca `GG_1_ROM_Cikar.bat` dosyasını çalıştır (yönetici izni ister).
2. Oyunu kapat ve `GG_2_Turkce_Yamayi_Uygula.bat` dosyasını çalıştır.

**Geri almak için:** `GG_Orijinale_Geri_Don.bat`.

**Çeviriye katkı:** `gg/gg_mk1_tr.json` dosyasında iki biçim var. Liste (`["satır", ...]`) bir sayfadır: satırlar serbestçe bölünebilir, ama sayfa orijinalinden uzun olamaz. Tek metin (`"metin"`) yerinde kalır ve orijinalinden uzun olamaz. Satırlar en fazla 20 karakter. Test için: `gg/test/run.sh`.

## Nasıl çalışıyor

`assets.pie`, konuma bağlı bir akış şifresiyle (AES-CTR benzeri) şifrelenmiş bir ZIP arşivi. Metinler, sıkıştırılmamış `strings/locale.strings` dosyasında duruyor. Şifrenin anahtarına gerek yok: `şifreli ⊕ orijinal ⊕ yeni` işlemi aynı konumdaki keystream'i yeniden kullanıyor. Bunun için orijinal metnin bilinmesi gerekiyor, `extract_strings.py` de bu yüzden var.

| Dosya | Görevi |
|---|---|
| `lstr.py` | `locale.strings` biçimini okur ve yazar (hash tablosu, dil tabloları, metin havuzu) |
| `extract_strings.py` | Çözülmüş dosyayı çalışan oyunun belleğinden kopyalar (CRC ile doğrular) |
| `build_tr.py` | `tr/*.json` çevirilerini `es-mx` yuvasına yerleştirip `tr.strings` dosyasını üretir |
| `patch_pie.py` | `tr.strings` dosyasını arşive yazar, ZIP CRC alanlarını günceller, yedekler ve geri yükler |

## Katkıda bulunma

Hatalı çeviri, taşan yazı ya da eksik metin görürsen issue açabilir ya da doğrudan pull request gönderebilirsin.

- Çeviriler `tr/*.json` dosyalarında `"id": "Türkçe metin"` biçiminde duruyor. `id`, orijinal dosyadaki benzersiz İngilizce metinlerin sırasıdır. İngilizce karşılığını görmek için önce 2. adımı uygula, sonra şunu çalıştır:
  `python -c "import lstr,json;print(list(dict.fromkeys(lstr.load(open('locale.strings.orig','rb').read())[1]['en-us']))[ID])"`
- `tr/zz_short.json` dosyası en son yüklenir. Menüye sığmayan metinlerin kısa hâllerini buraya ekle.
- Doğru Türkçe yaz (`ğ ş ı İ` dahil). Font dönüşümünü derleme betiği kendisi yapıyor.
- `{menu_accept}`, `%s`, `%%` ve satır sonları aynen kalmalı. `build_tr.py` bunu kontrol eder ve bozulursa hata verir.
- Göndermeden önce `python build_tr.py` çalıştırıp oyunda kontrol et.

**Terim sözlüğü:** Outworld → Dış Dünya · Earthrealm → Dünya Diyarı · Netherrealm → Cehennem Diyarı · Elder Gods → Kadim Tanrılar · Kombatant → Dövüşçü · The Krypt → Mahzen. Karakter adları, oyun adları ve Fatality/Babality/Animality/Friendship gibi terimler çevrilmez.

## Yasal

Bu proje Digital Eclipse, Warner Bros. ya da NetherRealm Studios ile bağlantılı değildir. Depoda oyuna ait hiçbir dosya ya da metin bulunmaz. Yama yalnızca yasal olarak sahip olduğun kopyada çalışır. Kod ve çeviriler MIT lisansıyla sunulur.
