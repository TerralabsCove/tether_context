---
status: draft
owner: Hansi Lee
last_reviewed: 2026-10-30
---

# Small motor 0x05 on board 11's CAN bus: wiring checks (2026-10-30)

Written by Hansi's AI agent from the test session. Not authoritative. Follows the
[C5 range test](2026-10-28-hansi-c5-range-test.md). Raw output: [checks.log](2026-10-30-hansi-0x05-hold-wiring/checks.log).

## Setup [as built]

- 0x05, a DM4340 (TMAX 28), shares a CAN bus with 0x02 (TMAX 200) on board 11, the base slave (COM21). The wires to
  0x05 are spliced onto 0x02's CAN pair with new solder joints.
- Firmware: tethersmall `c58dce8`. At boot the node scans CAN ids 0x01–0x7E, drives the motor with the largest TMAX
  as the joint, and holds any other motor still where it booted (`HOLD_SMALL`, see tethersmall
  `docs/SMALL_MOTOR_LOCK.md`). For 0x05 that is kp 40, kd 1.5, torque cap 9 Nm.
- Gateway not connected, so 0x02 only polls with damping. No arm motion.

## Fault and fix

- First check: 0x05 did not answer in two full boot scans. 0x02 answered on the same bus, so board 11, its
  transceiver and the shared wiring worked. [verified]
- Hansi's only change afterwards: twisting the CANH/CANL pair on the new wires from 0x02 to 0x05. [as built,
  reported by Hansi]
- After that change, 0x05 answered and was held. [verified]
- Cause [assumed]: twisting alone mainly improves noise immunity and is unlikely to turn a motor that never answers into
  one that always answers. Handling the wires more likely seated a pin or completed a joint that was open. This is
  the second time 0x05 went silent from its wiring; the first was a bad loom.

## Checks after the fix [verified]

**Wiggle test.** The node prints 0x05's hold status at 2 Hz. Each spot on 0x05's branch was flexed, tugged and
pressed for 45 s. A CAN dropout would show status 0xF0 (no reply for 50 ms), a power blip 0xF2, bus errors a rising
`tx_err` on 0x02's line.

| spot | hold lines | not HOLDING / status ≠ 0x00 | 0x05 angle (rad) | bus `tx_err` |
|---|---|---|---|---|
| 1. splice joints onto 0x02's pair | 90 | 0 | −1.736 throughout | 0 → 0 |
| 2. twisted run | 90 | 0 | −1.736 throughout | 0 → 0 |
| 3. 0x05 CAN connector, wire end | 90 | 0 | −1.736 throughout | 0 → 0 |
| 4. 0x05 CAN connector, mated | 90 | 0 | −1.736 throughout | 0 → 0 |
| 5. 0x05 power lead and connector | 90 | 0 | −1.736 throughout | 0 → 0 |

**Ten hard resets.** 0x02 and 0x05 were both found on all 10 boots, each on the first probe. 0x02 was chosen as the
joint motor and 0x05 held at status 0x00 every time.

## Limits

- The 2 Hz status line can miss a dropout shorter than about 0.5 s. `tx_err` staying at 0 makes one unlikely.
- Not tested with the arm moving: vibration, cable flex across the joints and motor current noise. Watch 0x05's hold
  line on the first hardware run.
