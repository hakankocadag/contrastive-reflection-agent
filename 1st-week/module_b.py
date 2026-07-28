"""Sentetik dosya: module_b.py
Kasitli hata: module_a ile CircularDependency (dongusel bagimlilik).
"""
import module_a  # <-- module_a da module_b'yi import ediyor: dongu burada kapanir


def parse_config(raw):
    entries = split_entries(raw)
    return entries


def split_entries(raw):
    return raw.split(",")


def debug_dump():
    return module_a.load_config("debug.ini")
