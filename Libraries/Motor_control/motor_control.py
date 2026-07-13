try:
    import machine
except ImportError:
    from Libraries import machine


class MotorController:
    def __init__(self, pwm_pin, encoder_cha_pin, encoder_chb_pin, ppr=20):
        """
        Initialize motor and quadrature encoder.

        Args:
            pwm_pin: GPIO pin for PWM (motor speed control)
            encoder_cha_pin: GPIO pin for encoder Channel A
            encoder_chb_pin: GPIO pin for encoder Channel B
            ppr: Pulses per rotation
        """
        self.ppr = ppr
        self.pulse_count = 0
        self.pulse_lock = False

        self.pwm = machine.PWM(machine.Pin(pwm_pin))
        self.pwm.freq(1000)
        self.pwm.duty_u16(0)

        self.encoder_cha = machine.Pin(encoder_cha_pin, machine.Pin.IN)
        self.encoder_chb = machine.Pin(encoder_chb_pin, machine.Pin.IN)
        self.encoder_cha.irq(
            handler=self._encoder_isr,
            trigger=machine.Pin.IRQ_RISING,
        )

    def _encoder_isr(self, pin):
        """Interrupt service routine for quadrature encoder pulses."""
        # Read both channels to determine direction
        cha = self.encoder_cha.value()
        chb = self.encoder_chb.value()
        # If CHA and CHB are same state, we're moving forward
        if cha == chb:
            self.pulse_count += 1
        else:
            self.pulse_count -= 1

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
