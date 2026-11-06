---
type: meeting
date: 2026-10-18
topic: Docking mechanism, power architecture, bracket mounting, structural checks
attendees: not recorded. No speaker labels. John recorded.
source: Granola, https://notes.granola.ai/d/4a06d994-f812-4bd4-9be2-ed9fe4823557
decisions_logged: D-043, D-044
---

<!-- Granola summary, as-is. "Bomb" is Baum Family Makerspace, misheard by Granola. Later changes: the battery count
     here differs from D-036, and the pin layout here differs from the 10-26 meeting. See truth/open-questions.md. -->

# Docking Mechanism Design

- Pins-on-arm architecture confirmed: servo-driven pins on the arm side, passive holes on the structure side
  - Reversal from earlier plan (pins on structure side)
  - Simplifies comms: no handshake needed between arm and structure
  - Frees up docking port count, better for locomotion
- Claw is an optional add-on, not core to climbing
  - Worst case: remove claw, robot still climbs
  - Priority remains getting the climb working first
- Servo selection: low torque required (pins only, no structural load)
  - 270-degree servo confirmed; 120-degree rotation needed for 3-pin layout
  - Metal gear servo selected
  - Need to order one more set (currently have 1 set of 2; need 2 sets)
- Tapered pins to reduce friction and ease retraction
- Camera used to verify pin alignment and detect full extension

# Power Architecture and Slip Ring

- Slip ring scoped to end effector only (low power)
  - Not passing high power through the middle joint
  - End effector servo is low draw; slip ring spec confirmed workable
- Battery layout (3 batteries total):
  - 2 large main batteries ordered
  - 1 center/small battery not yet ordered: needs to be sourced
  - Small batteries not yet specced for runtime; estimated similar to or longer than main (less load)
- Main batteries runtime: ~2 hours
- Slip ring current requirement: 2.9 A

# Motor Mounting and Bracket Adapter

- Bracket orientation needs to flip to match motor mount geometry
  - Current 4-hole mount doesn’t align; need 6 additional holes drilled into existing bracket
  - Options: hand drill (low precision), CNC (preferred), or water jet
- CNC approach: clamp bracket, drill through-holes (no countersink needed)
  - Contact Alex at Biegler (3rd floor) or Bomb/Sharia for machining
  - If Alex is available, could be done same day or next day
  - Need a CAD file of the changes before going to the shop
- Adapter plate also discussed as alternative; deemed more complex than adding holes

# Structural Integrity and FEA

- Concern raised about off-axis bracket loading (moment arm on non-planar mount)
  - Vertical brackets previously tested: ~0.5 mm deflection, acceptable
  - Horizontal/off-axis bracket: ~60 MPa stress, yield ~600 MPa; safety factor large but geometry is sketchy
  - Links are the primary deforming elements, not the brackets
- Options: add internal brace, redesign bracket, or convert to triangular prism geometry
- FEA to be run on full arm at each joint to find first failure point
- Ask Sam or Jack about original safety factor from prior design

# Transceiver Testing

- Old C3 transceivers: previously working
- New transceivers (C6): not receiving (TX sends, RX silent)
  - Suspected duds based on Reddit reports about this vendor
  - Iris confirmed old ones worked; new ones unresolved
- Plan: order replacement OG-style transceivers (Prime 2-day)
- C5 transceivers: only 1 unit arrived; need more before full testing
- Wes using the power supply; current spikes causing restarts on some tests

# Team Coordination and Next Steps

- Software team not yet engaged; CAD never locked in
  - Plan: give software team the URDF export + design requirements
  - Assign them renders, demonstration prep, and constraint documentation (max reach per step, linkage limits)
  - Jack to export latest URDF
- Presentation Thursday: full team presenting to engineers; practice session tomorrow after 1:30 PM
- Battery enclosure: 3-sided CAD modeled (1.3 mm max deflection); 4th panel structural vs. removable still open
  - Fewer bolts on removable side (2 vs. 4); hinge option floated
- Outer shell / electronics housing: very low priority

# Next Steps

- **Order center/small batteries**

  2 large main batteries in hand; center battery and small arm batteries not yet ordered.
- **Order one more servo set**

  Currently have 1 set (2 servos); need a second set for symmetric arm design.
- **Order replacement C6 transceivers (OG vendor, Prime 2-day)**

  Current new-batch transceivers suspected duds; old ones confirmed working.
- **Machine 6 new through-holes in bracket**

  Go to Biegler 3rd floor, ask for Alex; bring CAD file of updated hole pattern.
- **Update CAD: flip U-bracket orientation and finalize motor/battery layout**

  Required before machining and before handing URDF to software team.
- **Export latest URDF and assign software team deliverables** (Jack)

  Give them design constraints, renders, and demonstration prep; lock CAD freeze date.
- **Spec out slip ring**

  Must handle 2.9 A; was promised to the team last Thursday.

---

Meeting transcript and chat: https://notes.granola.ai/d/4a06d994-f812-4bd4-9be2-ed9fe4823557
