# Smart-greenhouse-monitor
IoT greenhouse climate monitoring and control system using **Raspberry Pi Pico W** and **MicroPython**.

## Team Members
- **Artem Balaniuk** ([@253208-creator](https://github.com/253208-creator)) – System architecture, timer task scheduling, main application logic (`PROJECT.py`), and repository integration
- **Reshat Uchak** ([@253240-hub](https://github.com/253240-hub)) – BME280 I2C sensor integration, measurement reading, and proportional smoothstep fan control logic
- **Jan Brančík** ([@270767-jpg](https://github.com/270767-jpg)) – I2C OLED UI (`leddisplay.py`), status LED driver (`rgb_led.py`), and rotary encoder interrupt handling
- **Danat Pustynnikov** ([@danat22](https://github.com/danat22)) – Hardware schematic, NPN transistor fan driver circuit (`NTE 199`), breadboard wiring, prototype assembly, and component testing

## Component List
- **Microcontroller:** Raspberry Pi Pico W (RP2040) with expansion shield;
- **Environmental Sensor:** Bosch BME280 Digital Environmental Sensor (measures atmospheric pressure, relative humidity, and temperature via **I2C**);
- **Display:** 128×64 **I2C OLED Display** (SH1106 controller, address `0x3C`);
- **Ventilation Driver:** 5V DC brushless fan driven by an **NTE 199 NPN transistor** and a $1\text{ k}\Omega$ base resistor;
- **Status Indicator:** 4-pin common-cathode **RGB LED** module (green = ventilating, red = idle);
- **User Input:** Incremental Digital Rotary Encoder (`CLK`, `DT`).

## System Block Diagram

```text
+-----------------------+       I2C0 (GP4, GP5)      +---------------------------+
|    BME280 Sensor      | -------------------------> |                           |
| (Temp, Hum, Pressure) |                            |                           |
+-----------------------+                            |                           |
                                                     |   Raspberry Pi Pico W     |
+-----------------------+      GPIO IRQ (GP17, 18)   |   (MicroPython v1.29.0)   |
|    Rotary Encoder     | -------------------------> |                           |
|   (Adjusts Tset)      |                            |  - Periodic Timer (500ms) |
+-----------------------+                            |  - Smoothstep PWM control |
                                                     |                           |
+-----------------------+       I2C0 (GP4, GP5)      |                           |
|  SH1106 OLED Display  | <------------------------- |                           |
|     (128x64 px)       |                            +-----+---------------+-----+
+-----------------------+                                  |               |
                                              PWM (GP19)   |               | GPIO (GP12, 13, 14)
                                                           v               v
                                                 +----------------+ +--------------+
                                                 | NPN Transistor | |   RGB LED    |
                                                 |   (NTE 199)    | | (Green/Red)  |
                                                 +-------+--------+ +--------------+
                                                         |
                                                         v
                                                 +----------------+
                                                 |  5V DC Fan     |
                                                 +----------------+
```

## Circuit Schematic & Pinout

| Component | Component Pin | Pico W Pin | Bus / Signal | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **BME280** | `VIN` / `GND` / `SCL` / `SDA` | `3V3` / `GND` / `GP5` / `GP4` | `I2C0` (400 kHz) | Environmental sensor (`0x76`) |
| **I2C OLED (SH1106)** | `VCC` / `GND` / `SCK` / `SDA` | `3V3` / `GND` / `GP5` / `GP4` | `I2C0` (400 kHz) | Shared I2C0 bus (`0x3C`) |
| **Rotary Encoder** | `+` / `GND` / `CLK` / `DT` | `3V3` / `GND` / `GP17` / `GP18` | Digital Input (`PULL_UP`) | Hardware `IRQ` for `Tset` adjustment |
| **5V Fan Driver** | Base (via $1\text{ k}\Omega$ resistor) | `GP19` | `PWM` (200 Hz) | Collector to Fan `-`, Emitter to `GND`, Fan `+` to `5V / VBUS` |
| **RGB LED** | `-` / `R` / `G` / `B` | `GND` / `GP14` / `GP13` / `GP12` | Digital Output | Green (`GP13`) when ventilating, Red (`GP14`) when idle |

### Fan & NPN Transistor (`NTE 199`) Wiring
```text
5V (VBUS) --------> [+] 5V DC Fan [-] --------> Collector (C) [NTE 199]
                                                               |
GP19 (PWM) -------> [ 1 kΩ Resistor ] --------> Base (B)      [NTE 199]
                                                               |
GND <------------------------------------------ Emitter (E)   [NTE 199]
```

## Core Functionality & Timing
- **Environmental Monitoring (`500 ms` Timer):** A hardware `Timer(-1)` triggers `timer_handler()` every **500 ms** (`2 Hz`) to read ambient temperature (°C), relative humidity (%), and atmospheric pressure (hPa) from the BME280 sensor without blocking execution.
- **Real-Time I2C Display:** Shows live sensor readings (`T`, `H`, `P`) alongside the user-defined target temperature (`Tset`) on the 128×64 I2C OLED display.
- **Interactive Control (`GPIO IRQ`):** Hardware interrupts on `GP17` (`CLK`) and `GP18` (`DT`) (`IRQ_RISING | IRQ_FALLING`) immediately increment or decrement `Tset` by $1\text{ }^\circ\text{C}$ on every encoder detent.
- **Smoothstep PWM Ventilation & Kickstart (`200 Hz`):** Computes fan duty cycle smoothly from temperature error $e = T - T_{\text{set}}$ using $x = \text{clamp}(e / 5.0, 0, 1)$, $\text{rpm} = x^2(3 - 2x)$. When starting from standstill (`rpm == 0`) to low duty cycles (`rpm < 0.7`), `set_fan_rpm()` applies a **100 % kickstart pulse for `300 ms`**.
- **Optical Status Indication:** Whenever `rpm > 0.0`, the RGB LED switches from red (`GP14`) to green (`GP13`) to indicate active cooling.
- **Fault Handling:** Verifies I2C device presence at startup (`0x3C` / `0x3D` fallback) and raises descriptive diagnostic messages if wiring is disconnected.

## Five-Week Plan

| Week | Focus | Tasks & Deliverables |
| :--- | :--- | :--- |
| **Week 1** | Proposal & Setup | Define project scope, split team roles, check hardware, and set up the repo with a block diagram and pinout. |
| **Week 2** | Component Tests | Test BME280, I2C display, encoder, and 5V fan driver separately; component classes and test scripts (`tests/`). |
| **Week 3** | Integration | Connect all modules in `PROJECT.py` / `main.py` using non-blocking timer/IRQ handlers for live display and fan/LED control. |
| **Week 4** | Verification & Docs | Verify error handling, measure refresh/polling intervals, add Sphinx docs (`docs/`), and draft the poster. |
| **Week 5** | Final Demo | Finish the A3+ poster and 1–2 min demo video, finalize the README, and present the working prototype. |

## Firmware & Used Libraries

### MicroPython Version
- **Firmware:** `MicroPython v1.29.0; Raspberry Pi Pico W with RP2040`
- **IDE:** VS Code (MicroPico)

### Built-in MicroPython Libraries
- `machine` (`I2C`, `Pin`, `Timer`, `PWM`) – I2C bus communication, GPIO interrupts, 500 ms periodic hardware timer, and 200 Hz PWM fan control;
- `framebuf` – 1-bit pixel and text buffer rendering (`MONO_VLSB`) for the 128×64 I2C OLED display;
- `time` – initialization delays (`sleep_ms`) and fan startup kickstart timing (`sleep`).

### Third-Party & Custom Project Modules (`project/`)
- `bme280.py` – third-party I2C driver for the Bosch BME280 temperature, humidity, and pressure sensor;
- `pack/leddisplay.py` – custom `OLED` driver class for the 128×64 I2C SH1106 display;
- `pack/vent.py` – custom PWM fan control module (`set_fan_rpm`) with 300 ms kickstart pulse logic;
- `pack/rgb_led.py` – custom `RGBLed` status indicator driver (green during ventilation, red when idle);
- `PROJECT.py` – main application entry point integrating sensors, encoder IRQ, timer loop, and actuators.

## Component Tests (Week 2 Verification)

Individual hardware verification tests performed prior to system integration (located in `tests/`):

| Component | Test Procedure | Verified Outcome |
| :--- | :--- | :--- |
| **I2C Bus & BME280** | Executed `i2c.scan()` and continuous `sensor.read_values()` output | Confirmed `0x76` (BME280) and `0x3C` (OLED) addresses and stable T/H/P readings |
| **I2C OLED (SH1106)** | Rendered test strings via `framebuf` with column offset `0x02` | Clean 128×64 text rendering without horizontal pixel shift |
| **Rotary Encoder** | Rotated clockwise/counter-clockwise with `IRQ` callback active | Accurate $\pm 1\text{ }^\circ\text{C}$ updates to `Tset` without missed steps |
| **5V Fan + NTE 199** | Tested `set_fan_rpm()` at `0%`, `35%` (with `300 ms` kickstart), and `100%` | Reliable startup at low PWM duty cycles and full stop at `0%` |
| **RGB LED** | Toggled ventilation active flag (`True` / `False`) | Green LED illuminated when ventilating (`True`); Red LED when idle (`False`) |
