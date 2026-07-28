"""Sentetik dosya: module_bad_calls.py
Kasitli hata: birden fazla UndefinedCall (tanimsiz fonksiyon cagrisi).
Bu, LLM'lerin en sik urettigi hallusinasyon turudur: var olmayan bir
yardimci fonksiyonu var sayip cagirmak.
"""


def compute_metrics(samples):
    cleaned = sanitize_samples(samples)  # <-- tanimsiz: hallucinated helper
    total = sum(cleaned)
    return total / normalize_count(len(cleaned))  # <-- tanimsiz: hallucinated helper


def render_report(metrics):
    formatted = pretty_print(metrics)  # <-- tanimsiz: hallucinated helper
    return formatted


def entry_point():
    data = [1, 2, 3, 4]
    metrics = compute_metrics(data)
    return render_report(metrics)
