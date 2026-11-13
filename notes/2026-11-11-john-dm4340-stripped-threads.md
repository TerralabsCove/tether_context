---
status: draft
owner: John Peng (hardware)
last_reviewed: 2026-11-11
---

# DM-J4340P-2EC: stripped mounting threads on the housing

Problem: the threads in the housing side (the part that doesn't spin) are stripped on the 4340s. Screws won't engage properly.

## What the manual says

Source: DM-J4340P-2EC user manual V1.0 (2025-01-10), "Motor Dimensions and Installation". This is the seller's drawing. Nothing here was measured.

| Face | Holes | Spins? |
|---|---|---|
| Rear (bottom) face | 4 × M2.5, 4 mm thread depth, on a ⌀38 circle | No |
| Front face, outer ring | 6 × M3, 5 mm deep, on a ⌀50 circle | No |
| Front face, output flange | 6 × M3, 6 mm deep, on a ⌀27 circle | Yes |

The manual gives no housing material, no screw torque and no screw length. It also says not to take the motor apart (Precautions, item 6).

The rear holes are the weakest on the motor: small, shallow and only four of them. The front outer ring has 6 × M3 at 5 mm, which is much stronger.

Cove failed the same way: "bottom threads stripped under load and the arm fell" ([robot.md](../truth/robot.md), 2026-04-26). D-042 says mount loads should go through interlocking geometry, not through the bolts ([decisions](../truth/decisions.md)).

## Check first (free)

1. **Screw length.** The holes are only about 4 mm deep. If a screw is too long it hits the bottom before it clamps, and more torque then strips the thread. Use: part thickness + 3 to 3.5 mm of thread at most.
2. **Hole depth and bottom.** Probe each hole with a pin and confirm it is blind. The rear face is where the driver board and connectors sit, so a hole that goes through changes the repair plan.
3. **Torque.** Use a small torque driver. M2.5 into aluminium usually takes well under 1 N·m (general practice, not from the manual).

## Repair options

| Option | How | Good | Bad |
|---|---|---|---|
| **A. Helicoil M2.5 (recommended)** | M2.5×0.45 helicoil kit: about 2.6 mm drill, STI tap, 1D (2.5 mm) insert. Use 1.5D (3.75 mm) only if probing shows the depth. | Same screw size, so no CAD change. Steel thread survives repeated assembly. | Drilling and tapping near the driver board. Chips are the main risk. |
| B. Retap to M3 | 2.5 mm drill, M3 bottoming tap | Cheap and fast | Only about 1.3 × D engagement in 4 mm, so not much stronger than the original. Mating parts need M3 clearance holes. |
| C. Epoxy or thread-repair compound | Fill and retap, or glue the screw in | No drilling | Temporary only. Don't use it on a load path. |

Chip control for A and B:
- Set a drill stop at the measured depth.
- Grease the drill and tap so the chips stick to them.
- Back out often and vacuum each hole.
- Don't blow air into the holes.
- Tape over the connectors and seams.

## Fix the cause

The threads will strip again if they still carry bending or side load. Two changes, together or alone:

- **Mount from the front outer ring (6 × M3 on ⌀50)** wherever the layout allows. This needs a CAD check of each 4340 mount.
- **Apply D-042 to the 4340 mounts.** Hold the motor in a pocket, cup or clamp around the ⌀57 body, so the rear screws only hold it in place in compression.

## Replace instead?

Replace a motor only if a hole is cracked, broken out to another hole, or open into the inside. Prices found 2026-11-11 for the 24 V version:

- aifitlab: $175, backordered
- Foxtech: $177–187
- OpenELAB: €214–226, ships from Long Beach
- Switch Science: sold out, no restock date

Check the voltage version before buying. Some listings sell only the motor without a driver. It's unknown whether Damiao sells the rear housing as a spare. Ask them before buying a whole motor.

## Update 2026-11-12: cause, and fast replacements

Cause, per John: M3 screws were driven into the M2.5 rear holes and nobody noticed. The holes are now partly cut to M3. That makes retapping to M3 (option B) the quickest repair: the screws and the mating parts are already M3. Use a bottoming tap and the chip control above.

Sellers checked in Chrome on 2026-11-12:

| Seller | Price | Stock | Ships from | Version |
|---|---|---|---|---|
| Robotics Center | $240 | In stock | San Francisco (90 Welsh St), pickup or delivery | Specs listed are V4 (12 / 40 Nm). Confirm before paying. |
| Foxtech | $177 (24 V) | Not shown | China. 3–5 days to ship, then DHL 6–8 days | V3 page |
| AIFITLAB | $175 | Unclear | China | V3 or V4 |
| OpenELAB | €221 | Pre-order, restock in 10–20 days | Not checked for this item | V3 or V4 |
| Amazon | none | | | |

**V3 vs V4.** Our motors match the V3 manual (9 Nm rated, 27 Nm peak, 8 A peak phase current). V4 is 12 / 40 Nm with 19.85 A peak phase current and 16-bit encoders. OpenELAB lists the size as 57 × 56.5 mm for both. The mounting-hole drawing for V4 was not checked. If a V4 goes in:
- Check its hole pattern against the V4 drawing.
- Set its TMAX to match what the code expects.
- Check the higher peak current against the fuses and power path.

## Update 2026-11-12: retapped to M4

Per John, the M3 threads were too damaged, so the rear holes were retapped to M4. Which motors, how many holes, and what final depth were not recorded.

What this means:
- **The thread is short.** The manual gives the holes 4 mm of thread depth. M4 in about 4 mm is roughly 1 × D of engagement, less if a taper or plug tap was used. That is short for steel screws in aluminium (housing material still unconfirmed).
- **Tightening is now the main risk.** Tighten well below the usual M4 torque chart value, and use a torque driver.
- **Screw length is critical.** Use part thickness + no more than 3.5 mm, so the screw can't bottom out.
- **Mating parts need M4 clearance holes,** 4.3–4.5 mm.
- **Spares and these motors now differ.** A new motor has M2.5 holes, and a retapped one has M4. Mark the retapped motors.

Checks before loading:
1. Look into each hole with a light and probe it. Check it didn't break into the inside, and look for cracks or bulging around it.
2. Clear the chips. Power up and check for normal feedback, no fault codes and normal idle current.
3. Do a torque test on one hole with a scrap screw before trusting it on the arm.

If M4 strips too, the next step is an M4 helicoil (about a 4.2 mm drill), which keeps M4 screws. M5 is not a good idea. The real fix is still D-042: the motor body sits in a pocket or clamp, so these screws only hold it in place.

## Open

- Which motors and which holes are stripped. The CAN IDs are worth recording.
- Housing material. Probably aluminium, not confirmed.
- What is behind the rear holes.
