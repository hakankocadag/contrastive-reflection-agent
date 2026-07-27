# Contrastive Reflection Agent (Hakan Kocadağ - 1. Hafta)

Bu proje, büyük dil modellerinin (LLM) yazılım kod tabanlarını analiz ederken ürettikleri halüsinasyonları otonom bir şekilde giderebilen, çok ajanlı (multi-agent) bir test ve optimizasyon framework'ü inşa etmeyi amaçlamaktadır.

Bu branch (Hakan-Kocadağ), geliştirme ekibinin **1. Hafta** görevlerinden **Öğretmen Ajan API Entegrasyonu ve Zıt-Yansıma (Contrastive Reflection) Prompt Şablonlarının** geliştirilmesini içerir.

## 🚀 Yapılan Geliştirmeler (Hakan Kocadağ - 1. Hafta)

1. **Öğretmen Ajan API Entegrasyonu (`teacher_agent.py`)**
   - İleri seviye akıl yürütme yapacak Öğretmen Ajan için asenkron (asyncio) altyapı kurulmuştur.
   - `google-generativeai` kütüphanesi kullanılarak **Gemini API (gemini-2.5-flash)** entegrasyonu tamamlanmıştır.

2. **Dinamik Contrastive Reflection Şablonları (`templates/contrastive_reflection.j2` & `prompt_manager.py`)**
   - Jinja2 kütüphanesi kullanılarak, Öğrenci Ajan'ın çıktısı ile "Zıt Kanıtları" (Contrastive Evidence) birleştiren dinamik prompt şablonu tasarlanmıştır.

## ⚙️ Kurulum

Gerekli Python kütüphanelerini yüklemek için:

```bash
pip install -r requirements.txt
```

## 🔑 Ortam Değişkenleri (.env)

Projenin ana dizininde bir `.env` dosyası oluşturun ve içerisine kendi Gemini API anahtarınızı ekleyin:

```env
GEMINI_API_KEY=sizin_api_anahtariniz_buraya
GEMINI_MODEL_NAME=gemini-2.5-flash
```

## 🛠️ Kullanım ve Test

Proje şu anda, Ali ve Kenan'ın görevleri olan "gerçek AST ayrıştırmaları ve öğrenci ajanı bağlantıları" tamamlanana kadar **sahte (mock) verilerle** test edilebilir durumdadır.

Sadece Jinja2 prompt şablonunun veri doldurulmuş halini görmek için:
```bash
python prompt_manager.py
```

Öğretmen Ajan'ın Gemini API ile bağlantı kurup, öğrenci hatasını tespit ettiği "Contrastive Reflection" değerlendirmesini (gerçek LLM çıktısını) görmek için:
```bash
python teacher_agent.py
```