# main.py | ESP32 entry point for the spool logger
import os
import sys
from collections import deque
from Libraries.Data_Log.cable_calc import CableCalculator
from Libraries.Motor_control.motor_control import MotorController
from Libraries import utime as utime
from Libraries import machine as machine

ROOT_DIR = os.path.dirname(__file__)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

LIBRARIES_DIR = os.path.join(ROOT_DIR, "Libraries")
if LIBRARIES_DIR not in sys.path:
    sys.path.insert(0, LIBRARIES_DIR)

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
        self.csv_logging_enabled = False
        self.csv_file = None
        self.csv_log_path = "displacement_log.csv"

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

        if self.csv_logging_enabled:
            self._append_csv_row(displacement)

    def _append_csv_row(self, displacement):
        """Append one displacement sample to the CSV log file."""
        if self.csv_file is None:
            return

        timestamp_ms = utime.ticks_ms()
        self.csv_file.write(f"{timestamp_ms},{displacement:.6f}\n")
        if hasattr(self.csv_file, "flush"):
            self.csv_file.flush()

    def _start_csv_logging(self):
        """Create or open the displacement CSV file and write the header."""
        if self.csv_file is not None:
            self.uart.write("CSV logging already active.\n")
            return

        self.csv_file = open(self.csv_log_path, "a")
        if self.csv_file.tell() == 0:
            self.csv_file.write("timestamp_ms,displacement_mm\n")
            if hasattr(self.csv_file, "flush"):
                self.csv_file.flush()

        self.csv_logging_enabled = True
        self.uart.write(f"CSV logging started: {self.csv_log_path}\n")

    def _stop_csv_logging(self):
        """Close the displacement CSV file."""
        if self.csv_file is not None:
            if hasattr(self.csv_file, "flush"):
                self.csv_file.flush()
            self.csv_file.close()
            self.csv_file = None

        self.csv_logging_enabled = False
        self.uart.write("CSV logging stopped.\n")

    def handle_command(self, cmd):
        """Process a single serial command.
        Expected commands:
            '+': Start motor at full speed
            '-': Stop motor
            'r': Reset pulse counter
            '0'-'255': Set motor speed (PWM duty cycle)
        """
        cmd = cmd.strip()
        if cmd == '+':
            self.motor.set_pwm(255)
        elif cmd == '-':
            self.motor.set_pwm(0)
        elif cmd == 'c':
            if self.csv_logging_enabled:
                self._stop_csv_logging()
            else:
                self._start_csv_logging()
        elif cmd.isdigit():
            self.motor.set_pwm(int(cmd) * 0.3)  # Scale to 0-85 range
        elif cmd == 'r':
            self.motor.reset_counter()
            self.uart.write("Counter reset.\n")
        elif cmd:
            self.uart.write(f"Unknown command: {cmd}\n")

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
            if self.csv_logging_enabled:
                self._stop_csv_logging()
            self.motor.stop()


def main():
    """Create the application and start the control loop."""
    logger = SpoolLogger()
    logger.run()


if __name__ == '__main__':
    main()