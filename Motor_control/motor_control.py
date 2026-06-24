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
        self.pulse_lock = False  # Simple lock to prevent count corruption
        
        # Motor PWM setup (1kHz frequency)
        self.pwm = machine.PWM(machine.Pin(pwm_pin))
        self.pwm.freq(1000)
        self.pwm.duty_u16(0)  # Start stopped
        
        # Encoder pin interrupt
        self.encoder_pin = machine.Pin(encoder_pin, machine.Pin.IN)
        self.encoder_pin.irq(
            handler=self._encoder_isr,
            trigger=machine.Pin.IRQ_RISING  # Count on rising edge
        )
    
    def _encoder_isr(self, pin):
        """
        Interrupt service routine for encoder pulses.
        
        Called on every rising edge. Must be < 100µs.
        Uses a simple lock instead of threading (no RTOS overhead on ESP32).
        """
        # Atomic increment without full lock (micropython constraint)
        # ISR runs with interrupts disabled, so this is safe
        self.pulse_count += 1
    
    def get_pulse_count(self):
        """Get current pulse count (thread-safe read)."""
        # Reading an int is atomic in micropython
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
        # Convert 8-bit to 16-bit duty cycle
        duty_u16 = int((duty / 255.0) * 65535)
        self.pwm.duty_u16(duty_u16)
    
    def stop(self):
        """Stop motor immediately."""
        self.set_pwm(0)