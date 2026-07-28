"""Sentetik dosya: module_c.py
Temiz dosya (kasitli hata yok). Bekci'nin 'yanlis pozitif' uretmedigini
dogrulamak icin negatif kontrol (negative control) olarak kullanilir.
"""


def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def average(values):
    total = 0
    for v in values:
        total = add(total, v)
    return total / len(values)
