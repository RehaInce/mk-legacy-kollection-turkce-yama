# Mortal Kombat: Legacy Kollection — Türkçe Yama

Mortal Kombat: Legacy Kollection (PC) için gayriresmî Türkçe çeviri. Türkçe, oyunun dil menüsüne **TÜRKÇE** adıyla ayrı bir seçenek olarak eklenir. İngilizce ve diğer diller değişmez.

**Çevrilenler:** menüler, ayarlar, karakter biyografileri ve sonları, müzedeki yapım hikâyesi ve tarihçe metinleri, hareket listeleri, başarımlar. Toplam 3093 metnin 2916'sı çevrildi. Kalanlar karakter, oyun ve platform adları gibi özel isimler.

**Sınırlamalar**
- Oyunun fontlarında `ğ ş ı İ` harfleri yok. Bu harfler `g s i I` olarak gösterilir. `ç ö ü` sorunsuz görünür.
- Derlemedeki orijinal oyunlar (MK1, MK2, Trilogy vb.) ROM'ların içinde olduğu için İngilizce kalır.

## Kurulum

Gerekenler: Windows ve [Python 3.8+](https://www.python.org/downloads/).

1. Bu depoyu (ya da [Releases](../../releases) sayfasındaki zip'i) oyun klasöründe `Turkce_Yama` adlı bir klasöre çıkar. Klasörün `assets.pie` ile aynı yerde olması gerekir.
2. Oyunu aç ve ana menüye kadar gel. `1_Orijinal_Metni_Cikar.bat` dosyasını çalıştır (yönetici izni ister). Bu adım, oyunun dil dosyasını senin kopyandan çıkarır. Telif hakkı nedeniyle bu dosya depoda yer almıyor.
3. Oyunu kapat ve `2_Turkce_Yamayi_Uygula.bat` dosyasını çalıştır.
4. Oyunda **OPTIONS → GAME OPTIONS → LANGUAGE** yolundan **TÜRKÇE**'yi seç.

**Geri almak için:** `Orijinale_Geri_Don.bat`. Yamalayıcı, değiştirdiği byte'ların orijinallerini ilk çalıştırmada `assets.pie.tr-backup` dosyasına yedekler.

**Oyun güncellenirse:** Yamalar arşivin belirli bir sürümüne göre yazıldı. Güncellemeden sonra Türkçe kaybolursa yamayı yeniden uygulamadan önce bir issue aç.

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
