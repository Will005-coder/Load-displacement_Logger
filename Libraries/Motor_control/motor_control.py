import machine


class MotorController:
    def __init__(self, pwm_pin, encoder_pin, ppr=20):
        """
        Initialize motor and encoder.

        Args:
            pwm_pin: GPIO pin for PWM (motor speed control)
            encoder_pin: GPIO pin for encoder (interrupt)
            ppr: Pulses per rotation
        """
        self.ppr = ppr
        self.pulse_count = 0
        self.pulse_lock = False

        self.pwm = machine.PWM(machine.Pin(pwm_pin))
        self.pwm.freq(1000)
        self.pwm.duty_u16(0)

        self.encoder_pin = machine.Pin(encoder_pin, machine.Pin.IN)
        self.encoder_pin.irq(
            handler=self._encoder_isr,
            trigger=machine.Pin.IRQ_RISING,
        )

    def _encoder_isr(self, pin):
        """Interrupt service routine for rising encoder pulses."""
        self.pulse_count += 1

    def get_pulse_count(self):
        """Get current pulse count."""
        return self.pulse_count

    def reset_counter(self):
        """Reset pulse count to zero."""
        self.pulse_count = 0

    def set_pwm(self, duty):
        """
        Set motor PWM duty cycle.

        Args:
            duty: 0-255 (0=off, 255=full speed)
        """
        duty_u16 = int((duty / 255.0) * 65535)
        self.pwm.duty_u16(duty_u16)

    def stop(self):
        """Stop motor immediately."""
        self.set_pwm(0)
