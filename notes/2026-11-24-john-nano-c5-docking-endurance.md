---
status: draft
owner: John Peng
last_reviewed: 2026-11-24
---

# STS3215 docking and endurance on an Arduino Nano, then the C5 (2026-11-24)

Written by John's AI agent on 2026-11-24, from a bench session with John. Not authoritative. Follows
[the morning's C5 bench note](2026-11-24-john-sts3215-c5-bench.md). Code and logs:
[tether_controls PR #6](https://github.com/TerralabsCove/tether_controls/pull/6), under
`bench/boards/arduino-nano/sts3215_led_test/` and `bench/boards/xiao-esp32-c5/sts3215_led_test/`.

John used an Arduino Nano for these tests so a mistake would not cost another C5. Servo ID 2 drives the
docking end effector through a belt.

## Results

- **The Nano drives both STS3215s from D2**, bit-banged at 1 Mbit/s. Both answered on the first scan. **[verified]**
- **The Nano's RX/TX pins do not work for the servo bus.** With servo data on TX jumpered to RX, the Nano could
  talk to the servos, but once the servos were powered the PC could no longer send commands to the Nano. The
  Nano's USB chip drives RX through a 1 kΩ resistor and could not pull the servo line low. **[verified]** (cause
  **[assumed]**)
- **Endurance: every run was clean.** No blocked moves, no comm errors, servos at 31 °C or less. See the table.
  **[verified]**
- **The Nano ran 10 minutes on the 5 V buck with no PC** and did not reset. **[verified]** (EEPROM record)
- **Docking works at 50 steps/s with a load trip of 160.** The first dock at 150 steps/s (trip 240) made the belt
  skip at a load of about 204. **[verified]** (belt skip seen by John)
- **After the first dock, ID 2 retracts only to about 91°.** Before it, ID 2 moved freely down to 11.4°. The cause
  is not known. **[verified]** (position), cause open
- **The C5 runs the same tests and stays cool.** The ring stayed dark on the C5 with the second loom. **[verified]**

## Endurance runs

Each cycle: ID 1 +50°, back, −50°, back; then ID 2's motion; torque capped at 30 %, stall guard on, ring
rainbow on. Logs are in tether_controls PR #6 except the buck run, whose stats come from the Nano's EEPROM.

| Board, power, loom | ID 2 motion | Time | Cycles | Servo max temp ID 1 / ID 2 | Pack | Board |
|---|---|---|---|---|---|---|
| Nano, USB, loom 1 | ±25° | 5 min | 12 | 27 / 29 °C | 12.1 V | 4.69-4.71 V |
| Nano, USB, loom 1 | sweep 13.2° ↔ 145.9° | 5 min | 8 | 28 / 30 °C | 12.0-12.1 V | 4.71-4.75 V |
| Nano, 5 V buck, no PC, loom 1 | sweep 13.2° ↔ 145.9° | 10 min | 16 | 29 / 30 °C | ≥ 11.9 V | 5.02-5.14 V |
| Nano, USB, loom 2 | sweep 13.2° ↔ 145.9° | 5 min | 8 | 27 / 29 °C | 12.4-12.6 V | 4.73-4.75 V |
| C5, USB, loom 2 | dock 145.9° ↔ undock 94.9°, 50 steps/s | 5 min | 8 | 29 / 31 °C | 12.1-12.3 V | chip temp flat |

The Nano's supply readings use its internal bandgap, so they are rough (about ±10 %).

## ID 2 range and docking

Before the dock was used, from about 122°, ID 2 reached −108° in steps, down to 11.4° with a flat load (104-116 of
1000). On the + side it stopped at about 151° on two days.

| Test | Result |
|---|---|
| Dock 1, 150 steps/s, trip 240 | Stopped at 144.7°, peak load 204. John saw the belt skip. |
| Undock 1 | Free to about 94°, then the load rose and the guard stopped it at 88.9°. |
| Docks 2-5, 50 steps/s, trip 160 | 144.8°, then 145.2° three times. Peak load 108-140. No skip. John confirmed it locked in. |
| Undocks 2-5, same settings | Stopped at 90.7-91.0° every time (load trip). John confirmed it was out of the port after undocks 2 and 3. |
| Push +10° from docked, 30 steps/s, 20 % cap, trip 100 | Moved 0.4°, then tripped on load. |
| Push 1° at a time, 20 % cap, trip 150 | Crept to 147.5°, then stalled at the cap. Load never passed 100. |
| C5, 8 dock/undock cycles | Every dock reached its 145.9° target (within 0.7°), peak load 108-116. |

The dock end stayed at 145° while the retract end moved from 11° to 91°, so a belt offset alone does not explain
it: an offset would move both ends. The firmware's retract end is now 1080 (94.9°).

## C5 bring-up with the second loom

- Pins: servo data D2 (GPIO25), ring DIN D3 (GPIO7). Neither is a C5 boot-strapping pin (GPIO2, 3, 26, 27, 28),
  per the pioarduino framework headers. **[verified]**
- The C5 was flashed on USB alone first: 23-25 °C. It stayed at 24-25 °C through the 5-minute run. **[verified]**
- The ring stayed dark although it had 5 V (John's multimeter). The data line check (`pinhigh 7`, D3 held at
  3.3 V) was in progress. A 5 V WS2812B wants about 3.5 V for a high, so 3.3 V data is marginal. **[assumed]**

## Power order

From the dead C5 and John's question about plugging in a live 5 V line:

1. USB or buck on the C5's 5V pad, never both.
2. For buck power, wire everything with the pack unplugged, buck 5 V to the 5V pad included. Plug the pack in last,
   so the buck's output ramps up instead of a live 5 V line being plugged into the C5.
3. Unplug the pack first before changing wiring or going back to USB.

## Open

- Why ID 2 now stops retracting at about 91° when it reached 11° before the first dock.
- Why the ring is dark on the C5 with loom 2: the DIN wire, or 3.3 V data into a 5 V ring. A level shifter
  (for example 74AHCT125) would settle the second.
- Belt tension, so a dock at speed cannot skip teeth.
- A 10-minute untethered run on the C5 (`arm 600`).
- Which joint ID 1 drives, and [open question 20](../truth/open-questions.md) on what the STS3215s are for.
