---
type: meeting
date: 2026-10-15
topic: Tether mount load path and fastener specs
attendees: not recorded. No speaker labels. John recorded.
source: Granola, https://notes.granola.ai/d/552cdd4e-9b16-411c-8e15-983f2345f46b
decisions_logged: D-042
---

<!-- Granola summary, as-is. -->

# Tether Mount Load Path Issue

- Mounting holes under high load create a thread-digging problem
  - Screws handle compression fine, but lateral/top loads dig into screw threads
  - Tolerances shift as a result, misaligning the mount
- Need a datum reference geometry to anchor alignment, not rely on screws alone
  - Screws compress only; actual load transfer needs a separate path

# Interlocking Geometry Solution

- Extend the block outward and add a U-shaped notch on the mating part
  - Creates interlocking geometry between the plates and motor-end mounts
  - Force transfer handled by the interlock, not the bolts
- Geometry interfaces at the small motor connection points

# Parts and Ordering Status

- Fasteners: no critical gaps identified
- CAN connectors/wires: flagged by Hansi, confirmed as ordered
- April Tags: already $0, no order needed

# Next Steps

- **DM Hansi to confirm CAN connector status**

  Quickest path is a direct text or call to confirm what's arriving and when.
- **Finalize interlocking geometry on tether mount**

  Design the U-shaped notch and block extension so load transfers through geometry, not bolts.

---

Meeting transcript and chat: https://notes.granola.ai/d/552cdd4e-9b16-411c-8e15-983f2345f46b
