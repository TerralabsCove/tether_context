---
status: draft
owner: John Peng
last_reviewed: 2026-11-06
---

# Digest of the Notion Tether page (2026-11-06)

Written by John's AI agent from [Tether and Terra Everything](https://app.notion.com/p/407b37231fea8062a1b0f09d333779b4), read 2026-11-06 at 09:09 UTC. That page is kept by John's assistant from Discord, Granola, GitHub and the sheets. Treat this digest as unverified. Decisions and open questions went to [truth/](../truth/decisions.md). This note holds the status detail that doesn't belong there.

BOM figures were read directly from the [Tether BOM](https://docs.google.com/spreadsheets/d/16mWqcQNEYmytco0OLClecacfsPCy_qwmkcIXcmFBWYw/edit) on 2026-11-06. Where the sheet and the Notion page differ, this note uses the sheet and says so.

Left out on purpose: club logistics, Castle bookings and address, dues and merch, and the Discord scan log.

## Mech

- **Panels:** water-jet at Baum. The Notion page has them promised for Nov 4, then Nov 5 night. Latest plan is in the [11-05 meeting](../meetings/2026-11-05-tether-planning.md).
- **End mounts:** CNC at Castle. Hand tap twisted on the 2nd tap (Nov 5). Jack is switching to CNC tapping and waits on the Makera bits TTH-088/089, ordered Nov 4, no arrival date.
- **U bracket:** dropped off at Castle Nov 5. Other parts are still being made.
- **Slip ring joint:** Jack's [redesign doc](https://docs.google.com/document/d/1dFEFnA6Pvco84UzzAF4Dn2Wpjk93UWag5d_dCiHui30/edit?usp=sharing) (Oct 29). Old design's end-bolt axial force from bending exceeded failure. New design: lowest hand-calc SF 2.05 at 5 mm minimum bolt engagement, SF 2.15 for axial load from bending, SF 7.5 for aluminum in bending. FEA peaks at 280 MPa at the bolt holes, which Jack attributes to mesh artifacts. **[assumed]** Nothing here is measured. See [question 18](../truth/open-questions.md).
- **Pins:** deformation FEA under 0.17 mm. **[assumed]**
- **Slip ring part:** on site at Castle since Nov 5. Still needs measuring, because shaft length depends on it.

## End effector

- Oct 26 leads breakout: about 90° of rotation is enough (4 pegs, 90° apart), so ±180° with a cable chain is an option instead of a slip ring. Not decided.
- Final 3D print was due for test Nov 3 and custom parts were due to be ordered Nov 4. The Notion page shows no result for either. See D-040.

## Electrical and comms

- C5s are flashed, labeled and mapped, with MACs in GitHub (Oct 27). 2 C5s went missing Oct 25. Whether they were found is unconfirmed.
- CAN transceiver headers were redone lower profile (Nov 2). Left board works. Right two are only continuity-checked, so test them with motors powered before use.
- Iris's power harness (Nov 5): final bracket has checked screw lengths. Two edge harnesses are planned, not soldered yet. It still needs a split on the big-motor branch for the buck to the ESPs.
- Middle battery wire exits on the side with the motor's connector (Iris, Nov 2).
- Soft-start modules (TTH-075, Autoro AS60 ×3) were ordered per the 11-01 meeting. Delivery isn't confirmed on the Notion page.

## Software

- John worked out max step and reach himself (Oct 30), so the designer sync no longer waits on the URDF sim.
- John posted a corrected `arm.urdf` for the URDF sim on Oct 30.
- Localization verification was due the week of Nov 1. No result on the Notion page. The first reCamera test is in the [11-06 follow-ups note](2026-11-06-john-claw-camera-followups.md).
- GitHub issues #15–#43 are still assigned to Trent and need reassigning.

## Timeline on the Notion page

These dates predate the 11-05 meeting, which puts the project about 2 weeks behind.

| When | Milestone |
|---|---|
| Sun 11/8 | One full module done, mech and electrical |
| ~Tue 11/10 | Goal: full arm minus end effectors and slip rings (tentative) |
| ~11/14–15 | End effector custom parts assembled, slip ring work done, wireless ESP control tests start |
| 11/16–11/22 | Demo and climb structure done (GitHub #65) |
| 11/25–11/29 | Thanksgiving. Projects should be done 1–2 days before |
| Week of 11/30 | Demo Day. Exact date is an [open conflict](../truth/open-questions.md#conflicts-between-sources) |

## BOM (sheet, 2026-11-06)

| Budget | Committed | Remaining | Ready to buy |
|---|---|---|---|
| $1,500.00 | $1,290.44 | $209.56 | $90.10 |

- **Cameras are Draft, not ordered:** TTH-092 (2 × GC2053 sensor board, $49.72) and TTH-093 (1 × reCamera 2002w 64GB, $109.90), both Mouser. Up to 30 % tariff may apply. No M12 fisheye lens is on the BOM.
- **Jack's order #3 is Ready, not ordered:** TTH-094 to TTH-097, $90.10. The Notion page says Ordered with $1,380.54 committed. The sheet has since changed them to Ready.
- **New servos:** TTH-090, 2 packs of FEETECH STS3215 30 kg 12 V serial bus servos (4 servos, $88.42), bought by Ming Nov 4. Not explained on the Notion page. Tether's buck plan is 5 V and the end-effector servos are ANNIMOS. See [question 20](../truth/open-questions.md).
- **LiDAR:** TTH-084, 2 × Unitree L1, $854, still Draft even though LiDAR was dropped (D-034). More than the remaining budget.

## Demo direction

From the [11-01 designer meeting](../meetings/2026-11-01-designer-demo.md) and the Notion page. Leading idea, not final:

- Area D, among the first things visitors see. Caroline and one other designer work on Tether's platform.
- Curious, lively arm moving objects between two piles in a loop, so there is no visible reset.
- Hill or spiral structure on an aluminum extrusion frame, with docks mounted to the frame and then covered.
- Green paint and fake moss on static links. The spinning end effector is harder to decorate.
- The Notion page and the Granola summary disagree on carrying: the page says Tether can't carry something and climb at once, the summary says it can if the object fits within dock depth. A keyword search of the transcript didn't settle it.
- Lively motion is probably possible but hard, and no one owns it yet.
