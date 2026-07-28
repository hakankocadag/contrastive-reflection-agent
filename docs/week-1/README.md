# Week 1 — Student Agent Foundation

[English](#english) | [Türkçe](#türkçe)

---

## English

### Overview

During Week 1, the foundation of the Student Agent module was developed.

The Student Agent is responsible for analyzing graph data, detecting function calls, reporting architectural errors, and returning the results in a validated structured format.

### Completed Tasks

- Created the initial Student Agent module structure.
- Defined Pydantic output schemas.
- Created the initial system prompt.
- Added support for additional prompt rules.
- Implemented an asynchronous agent interface.
- Added a fake LLM client for API-independent testing.
- Created a temporary mock `graph.json` fixture.
- Added automated tests with pytest.
- Verified structured output validation.

### Project Structure

```text
student_agent/
├── __init__.py
├── agent.py
├── prompts.py
└── schemas.py

tests/
├── fixtures/
│   └── mock_graph.json
├── __init__.py
└── test_student_agent.py
```

### Data Models

The Student Agent uses three Pydantic models:

- `FunctionCall`
- `ArchitectureError`
- `StudentAgentOutput`

The final output follows this structure:

```text
StudentAgentOutput
├── detected_calls
└── reported_errors
```

### Main Interface

The agent can be called asynchronously:

```python
result = await agent.analyze(
    graph_data=graph_data,
    additional_rules=additional_rules,
)
```

### Testing

Run the automated tests with:

```bash
python -m pytest -v
```

Current test result:

```text
1 passed
```

### Current Limitations

- A real LLM provider has not been integrated yet.
- The current graph data is temporary mock data.
- The final `graph.json` structure must be confirmed with the Ground Truth module.
- Teacher Agent prompt updates are not connected yet.
- API cost and model parameters have not been optimized yet.

### Next Steps

- Confirm the final `graph.json` structure.
- Integrate the selected LLM provider.
- Connect Teacher Agent prompt updates.
- Improve validation and error handling.
- Optimize API usage and model parameters.

---

## Türkçe

### Genel Bakış

Birinci haftada Öğrenci Ajan modülünün temel yapısı geliştirildi.

Öğrenci Ajan; graph verisini analiz etmek, fonksiyon çağrılarını tespit etmek, mimari hataları raporlamak ve sonuçları doğrulanmış yapısal bir formatta döndürmekten sorumludur.

### Tamamlanan Görevler

- Öğrenci Ajan modülünün başlangıç klasör yapısı oluşturuldu.
- Pydantic çıktı şemaları tanımlandı.
- İlk system prompt hazırlandı.
- Ek prompt kurallarını destekleyen yapı oluşturuldu.
- Asenkron ajan arayüzü geliştirildi.
- Gerçek API olmadan test yapabilmek için sahte LLM istemcisi oluşturuldu.
- Geçici bir `graph.json` test verisi eklendi.
- Pytest ile otomatik test yazıldı.
- Structured output doğrulaması test edildi.

### Proje Yapısı

```text
student_agent/
├── __init__.py
├── agent.py
├── prompts.py
└── schemas.py

tests/
├── fixtures/
│   └── mock_graph.json
├── __init__.py
└── test_student_agent.py
```

### Veri Modelleri

Öğrenci Ajan üç Pydantic modeli kullanmaktadır:

- `FunctionCall`
- `ArchitectureError`
- `StudentAgentOutput`

Sonuç aşağıdaki yapıda döndürülmektedir:

```text
StudentAgentOutput
├── detected_calls
└── reported_errors
```

### Temel Kullanım

Ajan asenkron olarak çağrılabilir:

```python
result = await agent.analyze(
    graph_data=graph_data,
    additional_rules=additional_rules,
)
```

### Test

Testleri çalıştırmak için:

```bash
python -m pytest -v
```

Mevcut test sonucu:

```text
1 passed
```

### Mevcut Sınırlamalar

- Gerçek bir LLM sağlayıcısı henüz bağlanmadı.
- Kullanılan graph verisi geçici test verisidir.
- Kesin `graph.json` yapısı Ground Truth modülüyle netleştirilmelidir.
- Öğretmen Ajan’dan gelecek prompt güncellemeleri henüz bağlanmadı.
- API maliyeti ve model parametreleri henüz optimize edilmedi.

### Sonraki Adımlar

- Kesin `graph.json` yapısını netleştirmek.
- Seçilen LLM sağlayıcısını entegre etmek.
- Öğretmen Ajan prompt güncellemelerini bağlamak.
- Doğrulama ve hata yönetimini geliştirmek.
- API kullanımını ve model parametrelerini optimize etmek.