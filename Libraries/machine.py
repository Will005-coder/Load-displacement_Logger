"""Minimal MicroPython-compatible stub for desktop testing."""


class Pin:
    IN = 0
    IRQ_RISING = 1

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def irq(self, *args, **kwargs):
        return None


class PWM:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def freq(self, *args, **kwargs):
        return None

    def duty_u16(self, *args, **kwargs):
        return None


class UART:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def any(self):
        return 0

    def read(self, *args, **kwargs):
        return b""

    def write(self, data):
        return len(data)
