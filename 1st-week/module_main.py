"""Sentetik dosya: module_main.py
Temiz dosya (kasitli hata yok). module_c'yi dogru sekilde kullanir,
dongusel bagimlilik veya tanimsiz cagri icermez.
"""
import module_c


def summarize(values):
    return module_c.average(values)


def main():
    values = [10, 20, 30]
    result = summarize(values)
    return result
