# Load-displacement_Logger

This project logs cable displacement for a cable-driven loading setup using an ESP32 and a motor/encoder interface.

## Dependencies
- Esptool 
- MicroPython (flashed on the esp)
- PyMakr (the bridge)


## Current project structure

- main.py
  - Main ESP32 entry point.
  - Initializes the UART, motor controller, calculator, and runs the main control loop.

- Libraries/
  - Local reusable modules for the ESP32 project.
  - Data_Log/
    - cable_calc.py: calculates the spooled line length from encoder pulses using the spiral-based geometry model.
  - Motor_control/
    - motor_control.py: handles PWM output and encoder pulse counting.
  - machine.py: lightweight MicroPython compatibility shim for desktop testing.
  - utime.py: lightweight MicroPython compatibility shim for desktop testing.

- Data_Log/
  - Legacy folder retained for compatibility with older imports.
  - Prefer using the version under Libraries/Data_Log.

- Motor_control/
  - Legacy folder retained for compatibility with older imports.
  - Prefer using the version under Libraries/Motor_control.

- pymakr.conf
  - PyMakr configuration for uploading the project to an ESP32.
  - Ignores local-only folders such as .venv and .vscode.

- .venv/
  - Local Python virtual environment used for desktop testing and validation.

## How the code is organized

- main.py is the startup script.
- hardware control is kept in Libraries/Motor_control.
- geometry and length calculations are kept in Libraries/Data_Log.
- the desktop shims in Libraries allow the project to be imported and tested locally without a MicroPython board.

## Notes for ESP32/PyMakr usage

- Upload the project root with PyMakr.
- Ensure main.py is present at the root so the ESP32 runs it on boot.
- Keep the Libraries folder intact so the imports resolve correctly on the device.

