"""Minimal MicroPython-compatible shim for desktop testing."""

import time


def sleep_ms(ms):
    time.sleep(ms / 1000.0)


def ticks_ms():
    return time.time_ns() // 1_000_000
