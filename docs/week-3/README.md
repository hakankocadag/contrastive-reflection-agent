# Week 3 — API Wrapper, Configuration and Reliability

[English](#english) | [Türkçe](#türkçe)

---

## English

### Overview

During Week 3, the Student Agent module was converted into a clean,
provider-independent API wrapper.

Centralized model configuration, timeout handling, retry behavior and
input validation were added to make the module more reliable and easier
to integrate with the other project components.

### Completed Tasks

- Added the provider-independent `LLMConfig` model.
- Centralized model parameters such as temperature and output-token limits.
- Added configurable request timeout support.
- Added configurable retry support for temporary connection failures.
- Created the `AsyncLLMClient` protocol.
- Separated the Student Agent from a specific LLM provider.
- Created the public `StudentAgentAPI` wrapper.
- Added validation for externally received prompt rules.
- Added JSON-compatible output support.
- Exposed the public module components through `student_agent/__init__.py`.
- Added automated timeout, retry and wrapper tests.

### Model Configuration

LLM-related parameters are managed through the `LLMConfig` model:

```python
from student_agent import LLMConfig

config = LLMConfig(
    model_name="mock-model",
    temperature=0.0,
    max_output_tokens=800,
    timeout_seconds=30.0,
    max_retries=2,
)
```

The configuration contains:

- `model_name`: Name of the selected language model
- `temperature`: Controls randomness in model responses
- `max_output_tokens`: Limits response length and possible API cost
- `timeout_seconds`: Maximum waiting time for one request
- `max_retries`: Number of retries after temporary failures

The configuration is immutable after creation to prevent accidental
runtime changes.

### Provider-Independent Client Interface

The `AsyncLLMClient` protocol defines the interface required from an LLM
provider:

```python
async def analyze(
    *,
    graph_data,
    system_prompt,
    config,
):
    ...
```

A future client implementation can use:

- OpenAI
- Azure OpenAI
- Another compatible LLM provider
- A mock client for testing

The Student Agent does not need to know which provider is being used.

### Timeout Handling

Every model request is executed with a configurable timeout.

```text
API request starts
        ↓
Response arrives before timeout
        ↓
Result is validated
```

If the provider does not respond within the configured period, the
request is stopped instead of waiting indefinitely.

### Retry Behavior

Temporary connection failures can be retried automatically.

Example with `max_retries=2`:

```text
Initial request
      ↓ failure
Retry 1
      ↓ failure
Retry 2
      ↓
Success or controlled error
```

The retry delay increases between attempts.

### Public API Wrapper

Other modules can use the Student Agent through the public wrapper:

```python
from student_agent import LLMConfig, StudentAgentAPI

api = StudentAgentAPI(
    client=llm_client,
    config=LLMConfig(
        temperature=0.0,
        max_output_tokens=800,
    ),
)

result = await api.analyze_graph(
    graph_data=graph_data,
    prompt_rules=[
        {
            "rule_id": "rule-001",
            "rule_text": "Ignore Python built-in function calls.",
            "version": 1,
        }
    ],
)
```

The wrapper performs the following operations:

```text
External graph dictionary
           ↓
Prompt-rule validation
           ↓
Student Agent analysis
           ↓
Structured-output validation
           ↓
JSON-compatible dictionary
```

Other project components do not need to manage internal prompt-building
or Pydantic details.

### Public Imports

The main components can be imported directly from the package:

```python
from student_agent import (
    AsyncLLMClient,
    LLMConfig,
    PromptRule,
    StudentAgentAPI,
    StudentAgentOutput,
)
```

### Testing

Run all automated tests with:

```bash
python -m pytest -v
```

Current result:

```text
6 passed
```

The tests currently verify:

- Latest prompt-rule version selection
- Stateless Student Agent behavior
- Retry behavior after a connection error
- Timeout handling
- JSON-compatible wrapper output
- Rejection of invalid prompt rules

### Current Limitations

- A real LLM provider has not been connected yet.
- API credentials are not managed by this module yet.
- Token usage and monetary cost are not measured from a real provider.
- The final `graph.json` structure must still be confirmed.
- Integration with the asynchronous orchestration engine is pending.
- Direct Teacher Agent integration is pending.

### Next Steps

- Implement the selected provider adapter.
- Add secure environment-variable configuration.
- Connect the final `graph.json` structure.
- Integrate the Student Agent with the orchestration engine.
- Connect Teacher Agent outputs.
- Record real latency, token-usage and cost metrics.

---

## Türkçe

### Genel Bakış

Üçüncü haftada Öğrenci Ajan modülü temiz ve sağlayıcıdan bağımsız bir API
wrapper hâline getirildi.

Modülün diğer proje bileşenleriyle daha kolay entegre edilebilmesi ve daha
güvenilir çalışması için merkezi model ayarları, zaman aşımı, tekrar deneme
ve giriş doğrulama mekanizmaları eklendi.

### Tamamlanan Görevler

- Sağlayıcıdan bağımsız `LLMConfig` modeli oluşturuldu.
- Temperature ve çıktı token sınırı gibi model ayarları merkezileştirildi.
- Yapılandırılabilir zaman aşımı desteği eklendi.
- Geçici bağlantı hataları için tekrar deneme desteği eklendi.
- `AsyncLLMClient` protokolü oluşturuldu.
- Öğrenci Ajan belirli bir LLM sağlayıcısından bağımsız hâle getirildi.
- Herkese açık `StudentAgentAPI` wrapper'ı oluşturuldu.
- Dış modüllerden gelen prompt kuralları için doğrulama eklendi.
- JSON uyumlu çıktı desteği eklendi.
- Ana bileşenler `student_agent/__init__.py` üzerinden dışarı açıldı.
- Timeout, retry ve wrapper için otomatik testler yazıldı.

### Model Yapılandırması

LLM ile ilgili ayarlar `LLMConfig` modeli üzerinden yönetilmektedir:

```python
from student_agent import LLMConfig

config = LLMConfig(
    model_name="mock-model",
    temperature=0.0,
    max_output_tokens=800,
    timeout_seconds=30.0,
    max_retries=2,
)
```

Yapılandırma şu alanları içerir:

- `model_name`: Kullanılacak dil modelinin adı
- `temperature`: Model cevaplarındaki rastgeleliği kontrol eder
- `max_output_tokens`: Cevap uzunluğunu ve olası API maliyetini sınırlar
- `timeout_seconds`: Bir API isteği için en fazla bekleme süresi
- `max_retries`: Geçici hatalardan sonra yapılacak tekrar deneme sayısı

Ayarların çalışma sırasında yanlışlıkla değiştirilmesini engellemek için
yapılandırma oluşturulduktan sonra değiştirilemez.

### Sağlayıcıdan Bağımsız İstemci Arayüzü

`AsyncLLMClient` protokolü, kullanılacak LLM istemcisinin uyması gereken
arayüzü tanımlar:

```python
async def analyze(
    *,
    graph_data,
    system_prompt,
    config,
):
    ...
```

Gelecekte şu istemcilerden biri kullanılabilir:

- OpenAI
- Azure OpenAI
- Başka bir uyumlu LLM sağlayıcısı
- Test amaçlı mock istemci

Öğrenci Ajan, hangi sağlayıcının kullanıldığını bilmek zorunda değildir.

### Zaman Aşımı Yönetimi

Her model isteği yapılandırılabilir bir zaman aşımı süresiyle çalıştırılır.

```text
API isteği başlar
       ↓
Cevap süre dolmadan gelir
       ↓
Sonuç doğrulanır
```

Sağlayıcı belirlenen süre içinde cevap vermezse sistem sonsuza kadar
beklemek yerine isteği durdurur.

### Tekrar Deneme Mekanizması

Geçici bağlantı hatalarında istek otomatik olarak yeniden denenebilir.

`max_retries=2` için örnek:

```text
İlk istek
   ↓ hata
Tekrar deneme 1
   ↓ hata
Tekrar deneme 2
   ↓
Başarı veya kontrollü hata
```

Tekrar denemeler arasındaki bekleme süresi kademeli olarak artar.

### Herkese Açık API Wrapper

Diğer proje modülleri Öğrenci Ajan'ı aşağıdaki wrapper üzerinden
kullanabilir:

```python
from student_agent import LLMConfig, StudentAgentAPI

api = StudentAgentAPI(
    client=llm_client,
    config=LLMConfig(
        temperature=0.0,
        max_output_tokens=800,
    ),
)

result = await api.analyze_graph(
    graph_data=graph_data,
    prompt_rules=[
        {
            "rule_id": "rule-001",
            "rule_text": "Ignore Python built-in function calls.",
            "version": 1,
        }
    ],
)
```

Wrapper aşağıdaki işlemleri gerçekleştirir:

```text
Dışarıdan gelen graph sözlüğü
             ↓
Prompt kurallarının doğrulanması
             ↓
Öğrenci Ajan analizi
             ↓
Structured output doğrulaması
             ↓
JSON uyumlu sözlük
```

Diğer ekip üyelerinin prompt oluşturma ve Pydantic ayrıntılarını yönetmesi
gerekmez.

### Dışarı Açılan Bileşenler

Ana bileşenler paket üzerinden doğrudan import edilebilir:

```python
from student_agent import (
    AsyncLLMClient,
    LLMConfig,
    PromptRule,
    StudentAgentAPI,
    StudentAgentOutput,
)
```

### Test

Tüm otomatik testleri çalıştırmak için:

```bash
python -m pytest -v
```

Mevcut sonuç:

```text
6 passed
```

Testler şu davranışları doğrulamaktadır:

- En güncel prompt kuralı sürümünün seçilmesi
- Öğrenci Ajan'ın stateless çalışması
- Bağlantı hatasından sonra tekrar deneme yapılması
- Zaman aşımı yönetimi
- Wrapper'ın JSON uyumlu çıktı üretmesi
- Geçersiz prompt kurallarının reddedilmesi

### Mevcut Sınırlamalar

- Gerçek bir LLM sağlayıcısı henüz bağlanmadı.
- API anahtarları bu modül tarafından henüz yönetilmiyor.
- Gerçek token kullanımı ve parasal maliyet henüz ölçülmüyor.
- Kesin `graph.json` yapısı hâlâ netleştirilmelidir.
- Asenkron ana motor entegrasyonu henüz yapılmadı.
- Öğretmen Ajan ile doğrudan bağlantı henüz kurulmadı.

### Sonraki Adımlar

- Seçilen LLM sağlayıcısı için adaptör geliştirmek.
- Ortam değişkenleri üzerinden güvenli ayar yönetimi eklemek.
- Kesin `graph.json` yapısını bağlamak.
- Öğrenci Ajan'ı asenkron ana motora entegre etmek.
- Öğretmen Ajan çıktılarını bağlamak.
- Gerçek gecikme, token kullanımı ve maliyet metriklerini kaydetmek.