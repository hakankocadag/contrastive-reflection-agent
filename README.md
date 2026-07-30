# Contrastive Reflection Agent (Hakan Kocadağ - 1, 2 ve 3. Hafta Görevleri)

Bu proje, büyük dil modellerinin (LLM) yazılım kod tabanlarını analiz ederken ürettikleri halüsinasyonları otonom bir şekilde giderebilen, çok ajanlı (multi-agent) bir test ve optimizasyon framework'ü inşa etmeyi amaçlamaktadır.

Bu branch (Hakan-Kocadağ), geliştirme ekibinin **Hakan Kocadağ**'a atanan ilk 3 haftalık görevlerinin tamamlanmış halini içermektedir.

## Yapılan Geliştirmeler

### 1. Hafta (Temellerin Atılması)
1. **Öğretmen Ajan API Entegrasyonu (`teacher_agent.py`)**
   - İleri seviye akıl yürütme yapacak Öğretmen Ajan için asenkron (asyncio) altyapı kurulmuştur.
   - `google-generativeai` kütüphanesi kullanılarak **Gemini API (gemini-2.5-flash)** entegrasyonu tamamlanmıştır.
2. **Dinamik Contrastive Reflection Şablonları (`templates/contrastive_reflection.j2` & `prompt_manager.py`)**
   - Jinja2 kütüphanesi kullanılarak, Öğrenci Ajan'ın çıktısı ile "Zıt Kanıtları" (Contrastive Evidence) birleştiren dinamik prompt şablonu tasarlanmıştır.

### 2. Hafta (Otonom Denetim ve Zekanın Bütünleşmesi)
1. **Veritabanı Okuması ve Simülasyonu (`mock_database.py`)**
   - Veritabanından gelen kontrastif kanıtları okumak üzere izole bir veritabanı simülasyonu oluşturuldu. Öğretmen Ajan, kayıtları bu modülden asenkron olarak çekmektedir.
2. **Prompt Güncellemesinin (Kural) Ayrıştırılması**
   - Öğretmen Ajan'ın serbest LLM metninden, yeni hataları engelleyecek **spesifik ve hedefli prompt güncellemesi** (kural) Regex ile ayrıştırıldı (parse edildi) ve veritabanına geri bildirim olarak kaydedildi.

### 3. Hafta (Doğrulama ve Metrik Raporlama)
1. **Metrik Hesaplayıcı ve İstatistik Raporlama (`metrics_reporter.py`)**
   - Framework'ün halüsinasyon giderme (başarı) metrikleri %30'luk simüle edilmiş bir "Eval Seti" (100 dosya) üzerinden ölçümlendi.
   - Öğretmen ajandan gelen kuralların sisteme kazandırdığı başarı (Rule Quality Score) hesaplandı ve konsola döküldü.
   - Sonuçlar `final_statistics_report.txt` dosyasına otomatik raporlanacak şekilde kurgulandı.

## Kurulum

Gerekli Python kütüphanelerini yüklemek için:

```bash
pip install -r requirements.txt
```

## Ortam Değişkenleri (.env)

Projenin ana dizininde bir `.env` dosyası oluşturun ve içerisine kendi Gemini API anahtarınızı ekleyin:

```env
GEMINI_API_KEY=sizin_api_anahtariniz_buraya
GEMINI_MODEL_NAME=gemini-2.5-flash
```

## Kullanım ve Test

Proje şu anda, takımın geri kalanının görevleri tamamlanana kadar **sahte (mock) verilerle** izole bir biçimde test edilebilir durumdadır.

1. **Jinja2 Prompt Şablon Testi:**
```bash
python prompt_manager.py
```

2. **Öğretmen Ajan ve Zıt Yansıma Otonom Döngüsü (2. Hafta Modülü):**
Bu komut, veritabanında bekleyen dosyaları çeker, Gemini'den kuralı ayrıştırır ve statüyü günceller.
```bash
python teacher_agent.py
```

3. **Final İstatistikleri ve Başarı Metriklerinin Raporlanması (3. Hafta Modülü):**
Bu komut, 100 test dosyası üzerinde başarı oranını hesaplar ve RQS (Kural Kalitesi) raporunu çıkarır.
```bash
python metrics_reporter.py
```
