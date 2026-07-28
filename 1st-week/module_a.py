"""Sentetik dosya: module_a.py
Kasitli hata: module_b ile CircularDependency (dongusel bagimlilik).
"""
import module_b  # <-- module_b da module_a'yi import ediyor: dongu burada baslar


def normalize(value):
    return value.strip().lower()


def load_config(path):
    raw = normalize(path)
    return module_b.parse_config(raw)


def main():
    config = load_config("settings.ini")
    return config
