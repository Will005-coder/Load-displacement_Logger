"""Minimal MicroPython-compatible shim for time helpers."""

import time


def sleep_ms(ms):
    time.sleep(ms / 1000.0)


def ticks_ms():
    return time.time_ns() // 1_000_000


__all__ = ["sleep_ms", "ticks_ms"]
