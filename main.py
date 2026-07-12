# main.py | ESP32 entry point for the spool logger
import machine
import utime
from collections import deque

from Data_Log.cable_calc import CableCalculator
from Motor_control.motor_control import MotorController

# Configuration
BAUD_RATE = 115200
LOG_INTERVAL_MS = 100
BUFFER_SIZE = 10
MOTOR_PWM_PIN = 4
MOTOR_ENCODER_PIN = 5
MOTOR_PPR = 20
SPOOL_DIAMETER_MM = 50.0
LINE_THICKNESS_MM = 1.0


class SpoolLogger:
    """Coordinate the serial interface, motor control, and length calculation."""

    def __init__(self):
        self.uart = machine.UART(0, BAUD_RATE)
        self.motor = MotorController(
            pwm_pin=MOTOR_PWM_PIN,
            encoder_pin=MOTOR_ENCODER_PIN,
            ppr=MOTOR_PPR,
        )
        self.calculator = CableCalculator(
            initial_radius_mm=SPOOL_DIAMETER_MM / 2.0,
            line_thickness_mm=LINE_THICKNESS_MM,
            ppr=MOTOR_PPR,
        )
        self.displacement_buffer = deque([], BUFFER_SIZE)
        self.last_log_time = 0

    def log_state(self):
        """Send the current pulse count and calculated length over serial."""
        pulse_count = self.motor.get_pulse_count()
        displacement = self.calculator.calculate_displacement(pulse_count)

        self.displacement_buffer.append(displacement)
        avg_displacement = sum(self.displacement_buffer) / len(self.displacement_buffer)

        msg = (
            f"Pulses: {pulse_count:5d} | Displacement: {displacement:7.2f}mm | "
            f"Avg: {avg_displacement:7.2f}mm\n"
        )
        self.uart.write(msg)

    def handle_command(self, cmd):
        """Process a single serial command."""
        if cmd == '+':
            self.motor.set_pwm(255)
        elif cmd == '-':
            self.motor.set_pwm(0)
        elif cmd == 'r':
            self.motor.reset_counter()
            self.uart.write("Counter reset.\n")

    def run(self):
        """Run the main control loop."""
        self.uart.write("=== Cable Spool Encoder System Initialized ===\n")
        self.uart.write(f"Initial radius: {self.calculator.initial_radius_mm:.2f}mm\n")
        self.uart.write(f"PPR: {self.motor.ppr}\n")
        self.uart.write("Ready. Waiting for motor commands...\n\n")

        try:
            while True:
                now = utime.ticks_ms()
                if now - self.last_log_time >= LOG_INTERVAL_MS:
                    self.log_state()
                    self.last_log_time = now

                if self.uart.any():
                    cmd = self.uart.read(1).decode()
                    self.handle_command(cmd)

                utime.sleep_ms(5)
        except KeyboardInterrupt:
            self.uart.write("\n=== System shutdown ===\n")
            self.motor.stop()


def main():
    """Create the application and start the control loop."""
    logger = SpoolLogger()
    logger.run()


if __name__ == '__main__':
    main()