"""Minimal MicroPython-compatible shim for time helpers."""

from time import sleep_ms, ticks_ms

__all__ = ["sleep_ms", "ticks_ms"]
