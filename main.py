# main.py — System initialization and control loop
import machine
import utime
import motor_control
import cable_calc
from collections import deque

# Configuration
BAUD_RATE = 115200
LOG_INTERVAL_MS = 100  # Report every 100ms
BUFFER_SIZE = 10  # Moving average

# Serial setup
uart = machine.UART(0, BAUD_RATE)

# Initialize motor and encoder
motor = motor_control.MotorController(
    pwm_pin=4,
    encoder_pin=5,
    ppr=20  # Pulses per rotation (adjust to your encoder)
)

# Initialize cable calculator
calculator = cable_calc.CableCalculator(
    spool_diameter_mm=50.0,  # Adjust to your spool
    ppr=20
)

# Logging buffer
displacement_buffer = deque([], BUFFER_SIZE)
last_log_time = 0

def log_state():
    """Log system state to serial."""
    pulse_count = motor.get_pulse_count()
    displacement = calculator.calculate_displacement(pulse_count)
    
    # Moving average for smoothing
    displacement_buffer.append(displacement)
    avg_displacement = sum(displacement_buffer) / len(displacement_buffer)
    
    msg = f"Pulses: {pulse_count:5d} | Displacement: {displacement:7.2f}mm | Avg: {avg_displacement:7.2f}mm\n"
    uart.write(msg)

def main():
    """Main control loop."""
    global last_log_time
    
    uart.write("=== Cable Spool Encoder System Initialized ===\n")
    uart.write(f"Spool diameter: {calculator.spool_diameter_mm}mm\n")
    uart.write(f"PPR: {motor.ppr}\n")
    uart.write("Ready. Waiting for motor commands...\n\n")
    
    try:
        while True:
            # Non-blocking: check if it's time to log
            now = utime.ticks_ms()
            if now - last_log_time >= LOG_INTERVAL_MS:
                log_state()
                last_log_time = now
            
            # Example: check serial for commands
            if uart.any():
                cmd = uart.read(1).decode()
                if cmd == '+':
                    motor.set_pwm(255)  # Full speed forward
                elif cmd == '-':
                    motor.set_pwm(0)    # Stop
                elif cmd == 'r':
                    motor.reset_counter()  # Reset pulse counter
                    uart.write("Counter reset.\n")
            
            utime.sleep_ms(5)  # Small sleep to yield to interrupts
    
    except KeyboardInterrupt:
        uart.write("\n=== System shutdown ===\n")
        motor.stop()

if __name__ == '__main__':
    main()