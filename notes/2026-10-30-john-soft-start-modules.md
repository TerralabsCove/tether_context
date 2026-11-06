---
status: draft
owner: john
last_reviewed: 2026-10-30
---

# Soft-start / anti-spark options for module power

Problem: each module's LiPo connects straight to its motors (D-008, no BMS). Plugging in charges the motor drivers' bus capacitors all at once. That inrush sparks the connector and can damage the drivers.

Assumed: 6S LiPo (~25.2 V full), to match the 24 V trunk in [robot.md](../truth/robot.md). Per-module peak current is not measured. Size for 3 motors at peak and check it against Damiao datasheets before buying.

Prices and ratings are from an Amazon search on 2026-10-30. They are seller claims, not verified.

## Three kinds of part

1. **Anti-spark connector (XT90-S).** A resistor in the plug precharges the caps for a moment before the main pins touch. Passive, cheap, no switch. You still have to plug in to power on.
2. **Soft-start filter board.** A MOSFET ramps the voltage up on connect. No on/off control.
3. **Electronic anti-spark switch.** A MOSFET switch with soft start plus a button or AUX input. Gives a real "start switch". This is closest to what we asked for.

## Shortlist

| Part | Type | Rating | Volts | Price | Reviews |
|---|---|---|---|---|---|
| Autoro AS60-30 (XT60) | switch module | 30 A | 3–8S | $15.99 | 5.0 (5) |
| Autoro AS60 (XT60) | switch module | 60 A | 3–8S | $19.99 | 4.1 (4) |
| Autoro AS100 + S16 switch | switch | 100 A | 2–20S, 84 V | $38.99 | 5.0 (6) |
| Anti Spark Switch XT60, AUX on/off | switch | not listed in search | not listed | $19.99 | 4.5 (2) |
| Anti Spark Switch Aluminum PCB V2.0 | switch (e-skate style) | 200 A | not listed | $32.99 | 4.8 (8) |
| Anti-Spark Switch Smart Enhanced | switch (e-skate style) | not listed | not listed | $39.99 | 3.9 (33) |
| DarwinFPV soft-start XT60 filter | filter, no switch | not listed | 3–8S | $9.99 | none |
| Amass XT90-S, 5 pairs | connector | 90 A class | — | $12.98 | 4.8 (1K) |

## Avoid

- Plain XT60/XT90 toggle or rocker switches. Mechanical contacts will arc on the same inrush. No soft start.
- "Smoke stoppers" (ShortSaver etc.). These are short-circuit testers for bench bring-up, not run-time switches.

## Follow-up 2026-10-30: we still need an on/off switch

Team leaned toward the Autoro AS60 (60 A). Its listing shows it is **inline only, no switch input**. It soft-starts when the battery is plugged in, and only if the load is connected first. The listing contradicts itself: the bullets say 60 A, the spec table says 30 A and 33 V.

Options that give a real power switch:

| Option | How it switches | Rating (seller) | Connectors | Size / weight | Price |
|---|---|---|---|---|---|
| A. Jonronfey "Anti Spark Switch XT60, AUX on/off" | Rocker drives MOSFETs on the negative line. Rocker carries signal only. 2.54 mm header for a remote switch. Slow turn-on. Reverse-polarity LED. | 60 A, 9–30 V | XT60 native | 68 × 46 × 30 mm | $19.99 |
| B. Autoro AS100 | S16 metal latching button with LED, 250 mm lead. Signal only. | 100 A cont / 300 A peak, 6–84 V | XT90, 10 AWG | 55 × 40 × 11 mm, 66.8 g + 17.4 g button | $38.99 |
| C. AS60 plus mechanical switch ahead of it (battery → switch → AS60 → motors) | Switch carries full motor current | depends on switch | XT60 | extra part | $20 + switch |

Notes:
- A: 6S full charge is 25.2 V, so the 30 V limit leaves only ~5 V of margin. One reviewer reports a 40 V / 180 A MOSFET and two 40 A fuses in parallel. Only 2 reviews.
- A: the pin header could be wired to an e-stop or an ESP GPIO later. Not tested.
- A, review search (2026-10-30): no independent reviews found (Reddit, forums, blogs). The only 2 reviews are Amazon Vine (free product). Amazon part number JF-2643.
- A, MOSFET: the reviewer's "G011N04" marking most likely matches Huayi HYG011N04 (40 V, 165 A, ~1.1 mΩ). [assumed] Check by opening the case when it arrives.
- A, wiring risk: it switches the **negative** line. If the ESP's DC-DC is fed from the battery side, motor ground floats when the switch is off, and CAN can backfeed through the transceiver. Put everything (motors and DC-DC) downstream of the switch.
- A, regen: motor braking can raise bus voltage above 25.2 V. Not measured.
- C: works for turn-on, but the switch arcs when opened under load, and small XT60 rockers are AC-rated. Not recommended.

## Follow-up 2026-10-30: does 6S suit the DM-J4340P-2EC?

Source: DM-J4340P-2EC user manual V1.0 (2025-01-10), Key Parameters and Control & Protection tables. Seller manual, not measured.

- Rated voltage 24 V (a 48 V version also exists). 6S is 25.2 V full, 22.2 V nominal, ~19.8 V at 3.3 V/cell. That fits the 24 V version.
- Overvoltage trip is user-set; the manual recommends ≤ 32 V for the 24 V version. That gives ~7 V of headroom over a full pack for regen.
- Undervoltage: the supply must be ≥ 15 V. The trip value is register `0x00` `UV_Value`, range 10 V and up. 15 V on 6S is 2.5 V/cell, which over-discharges a LiPo.
- So D-008's "motors protect the battery" only holds if `UV_Value` is raised to about 19.8–21 V (3.3–3.5 V/cell) and stored to flash on every motor. Default value not read yet.
- The undervoltage trip only exits enabled mode. The driver and the ESP's DC-DC still draw current, so a pack left plugged in keeps draining.
- Check which version we own (24 V or 48 V). A 48 V unit on 6S would run at roughly half speed.

## Next steps

- Get peak current per module (3 Damiao motors) to choose 30 A vs 60 A vs 100 A.
- Check weight and size against the module layout.
- Cheapest safe option: XT90-S on every battery lead. Add an electronic switch if we want a button to power on.
