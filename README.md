# Smart-greenhouse-monitor
IoT greenhouse climate monitoring and control system using Raspberry Pi Pico W and MicroPython

## Team Members
* **Artem Balaniuk** ([@253208-creator](https://github.com/253208-creator)) – [System architecture, `uasyncio`/timer task scheduling, main application logic, repository integration]
* **Reshat Uchak** ([@253240-hub](https://github.com/253240-hub)) – [BME280 I2C sensor integration, measurement filtering, threshold and hysteresis control logic]
* **Jan Brančík** ([@270767-jpg](https://github.com/270767-jpg)) – [SPI OLED UI, rotary encoder class, interrupt/debounce handling]
* **Danat Pustynnikov** ([@danat22](https://github.com/danat22)) – [Hardware schematic, MOSFET fan driver circuit, wiring, prototype assembly, and hardware testing]

## Component List
* Raspberry Pi Pico;
* BME280 Digital Environmental Sensor (measures pressure, humidity and temperature);
* I2C OLED Display;
* 5V fan with driver (MOSFET and few resistors);
* Digital Encoder


## Core Functionality
* **Environmental Monitoring:** Continuously measures ambient temperature (°C), relative humidity (%), and atmospheric pressure (hPa) using the BME280 sensor.
* **Real-Time Display:** Shows live sensor readings, the target threshold, operating mode (`AUTO` / `MANUAL`), and current fan state (`ON` / `OFF`) on the Nokia 5110 SPI LCD.
* **Interactive Control:** Lets the user adjust the target climate threshold and switch between `AUTO` and `MANUAL` modes using the digital rotary encoder and its push-button.
* **Automated Ventilation:** Switches the 5 V DC fan on and off via the MOSFET driver when temperature or humidity crosses the user-defined threshold, using hysteresis to prevent rapid switching.
* **Fault Handling:** Detects I2C sensor disconnections or invalid measurements and displays a clear warning on the screen without freezing the system.
* **Responsive Execution:** Processes encoder input, sensor readings, and display refreshes concurrently so user controls remain responsive at all times.
* **Wi-Fi Telemetry:** Publishes sensor readings and fan status over Wi-Fi/MQTT at regular intervals.

## Five-Week Plan

| Week | Focus | Tasks & Deliverables |
| :--- | :--- | :--- |
| **Week 1** | Proposal & Setup | Define project scope, split team roles, check hardware, and set up the repo with a block diagram and pinout. |
| **Week 2** | Component Tests | Test BME280, I2C display, encoder, and 5V fan driver separately; component classes and test scripts. |
| **Week 3** | Integration | Connect all modules in `main.py` using non-blocking tasks (`uasyncio`/timers) for live display and threshold fan control. |
| **Week 4** | Verification & Docs | Test error handling (disconnected sensor), measure refresh/polling intervals, add Sphinx docs (`docs/`), and draft the poster. |
| **Week 5** | Final Demo | Finish the A3+ poster and 1–2 min demo video, finalize the README, and present the working prototype. |

## Firmware & Used Libraries

### MicroPython Version
* **Firmware:** `MicroPython v1.29.0; Raspberry Pi Pico W with RP2040`
* **IDE:** VS Code (MicroPico)

### Built-in MicroPython Libraries
* `machine` (`I2C`, `Pin`, `Timer`, `PWM`) – I2C bus communication, GPIO interrupts, periodic hardware timer, and 200 Hz PWM fan control;
* `framebuf` – 1-bit pixel and text buffer rendering for the 128×64 OLED display;
* `time` – initialization delays (`sleep_ms`) and fan startup kickstart timing (`sleep`);

### Third-Party & Custom Project Modules (`code/`)
* `bme280.py` – third-party I2C driver for the Bosch BME280 temperature, humidity, and pressure sensor;
* `pack/led_display.py` – custom `OLED` driver class for the 128×64 I2C display;
* `pack/vent.py` – custom PWM fan control module (`set_fan_rpm`) with kickstart pulse logic
