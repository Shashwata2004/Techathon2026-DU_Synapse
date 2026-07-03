# Hardware Wiring Guide

This is a representative one-room schematic for Wokwi. It shows how one room with 2 fans and 3 lights could be sensed by an ESP32. The software demo still uses simulated data from the FastAPI backend.

## Components

- 1 ESP32 development board
- 5 switches or slide switches for device ON/OFF state
- 3 LEDs for lights
- 2 DC motor symbols or LEDs labeled as fans
- 5 current-limiting resistors for LEDs
- Optional ACS712-style current sensor connected to an ADC pin

## Pin Mapping

| ESP32 Pin | Signal | Simulated Device |
| --- | --- | --- |
| GPIO 18 | Digital input | Fan 1 state switch |
| GPIO 19 | Digital input | Fan 2 state switch |
| GPIO 21 | Digital input | Light 1 state switch |
| GPIO 22 | Digital input | Light 2 state switch |
| GPIO 23 | Digital input | Light 3 state switch |
| GPIO 34 | Analog input | Optional current sensor output |
| 3.3V | Power rail | Switch pull-up side |
| GND | Ground rail | Common ground |

## Connection List

- Connect one side of each switch to 3.3V.
- Connect the other side of each switch to its assigned GPIO pin.
- Add a pulldown resistor to GND for each input, or configure software pulldowns where supported.
- Connect each LED through a current-limiting resistor to an output indicator path if you want a visual load state.
- Connect all grounds together.
- If using a current sensor, connect sensor analog output to GPIO 34 and sensor ground to ESP32 ground.

## Electrical Reasoning

The switches represent whether each fan or light circuit is ON. The ESP32 reads each switch as a digital HIGH/LOW signal and sends the state upstream in a real deployment. The optional current sensor represents measuring actual load current for power estimation.

## Safety Note

Real AC lights and fans must never be connected directly to an ESP32 or Arduino. A real installation needs relay modules or contactors, opto-isolation, fuses/breakers, correct wire gauges, current sensors rated for the load, and qualified electrical supervision.

Save the final Wokwi screenshot as `docs/diagrams/hardware-schematic.png`.
