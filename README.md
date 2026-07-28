# Contrastive Reflection Agent

A multi-agent test automation framework designed to detect and reduce
hallucinations produced by large language models during software
architecture analysis.

Yazılım mimarisi analizi sırasında büyük dil modellerinin ürettiği
halüsinasyonları tespit etmek ve azaltmak amacıyla geliştirilen çok ajanlı
bir test otomasyonu framework'üdür.

## Project Modules

- Ground Truth Generator
- Student Agent
- Guardian
- Teacher Agent
- Asynchronous Orchestration Engine

## Student Agent

The Student Agent analyzes graph data, detects function calls, reports
architectural errors, and returns validated structured output.

Öğrenci Ajan, graph verisini analiz eder, fonksiyon çağrılarını ve mimari
hataları tespit eder ve sonuçları doğrulanmış yapısal bir formatta döndürür.

## Documentation

### Week 1 — Student Agent Foundation

During Week 1, the initial Student Agent structure, Pydantic schemas,
system prompt, asynchronous interface, mock graph data, and automated
tests were created.

Birinci haftada Öğrenci Ajan'ın temel yapısı, Pydantic şemaları, system
promptu, asenkron arayüzü, örnek graph verisi ve otomatik testleri
oluşturuldu.

[View Week 1 Documentation — English & Türkçe](docs/week-1/README.md)

## Testing

Run the tests with:

```bash
python -m pytest -v
