---
status: draft
owner: John Peng
last_reviewed: 2026-10-16
---

# MVP review one-pager, 2026-10-16

Tether's MVP review one-pager, built locally to match the Terra Labs template ([Figma template frame](https://www.figma.com/design/i6NfHYKHX04PPjAx99nAzu/Terra-Labs-Fall-2026-Design?node-id=497-2)).

- Figma: the Tether frame was rebuilt to match this page on 2026-10-17, with editable text, image fills and a vector diagram.
- Page: [2026-10-16-john-mvp-one-pager/index.html](2026-10-16-john-mvp-one-pager/index.html)
- Print copy: [tether-mvp-one-pager.pdf](2026-10-16-john-mvp-one-pager/tether-mvp-one-pager.pdf)
- Images: John's sim ladder-climb frames (vision, ordered by anchor height), CAD of the full arm and one module (hardware), and a drawn communication diagram (software).

The text comes from `truth/`, the bench notes, and John's description on 2026-10-16 (below).

## New from John, 2026-10-16 (not yet in `truth/`)

- Each module runs on a **6S LiPo**.
- **Comms topology:** a master ESP32-C5 sits at the offboard computer. It sends joint positions over ESP-NOW to three slave ESP32-C5s, one on each robot module. Each slave drives its module's motors over CAN. **Conflict:** D-026 and the [bench note](2026-10-12-irisy-embedded-controls-bench.md) put the master on the robot as node ID 0 with one motor, reached by the laptop over Wi-Fi. The bench note also assumes XIAO ESP32-C6, not C5. The tethersmall testbed did use an offboard master (Mac → USB → master ESP32).
- **Localization change: mocap is likely out.** The mocap system can't be moved from where it is installed. Instead, encoders and gyroscopes go on every module/segment, and stereo cameras run SLAM for a rough position in the environment. **Conflict:** D-012 made mocap primary and ruled out SLAM as too noisy in dark conditions. The same environment is described as very dark.
- **Localization on the one-pager (chosen 2026-10-16):** IR cameras fixed around the demo set track small IR LEDs hidden on each module, which makes a set-mounted mocap rig. Encoders and gyros fill in between camera frames, and claw cameras handle grip alignment. Stereo SLAM was dropped because it needs a video stream offboard (the ESP32 link can't carry one) and dark, low-texture scenes make it drift. This is D-018 option 3 (build our own mocap). The set geometry (bars or steps) is still unknown.
- **Why mocap was picked first:** the set is very dark, so localization needs non-visible light (mocap IR). AprilTags on the robot were rejected as unreliable in the dark and aesthetically unacceptable.
- **Why all wireless (D-006):** joints need full, continuous 360° rotation, and wires or slip rings would limit that. It also keeps wires off the outside, so the robot looks clean and compact.
- **Why a battery in each module (D-004):** thick power wires would not route well through the joints, so power stays local to each module.
- **Cameras on both end effectors** align the claws to dock and grab bars. `truth/` has AprilTags on docking as the backup (D-012) and the video link as unresolved.
- **Stage 1 uses pre-planned paths.** RL policies, and possibly VLAs, come later for complex actions. This is consistent with D-014 ("no RL at this stage").
- **Demo Day:** Tether interacts with the demo set (bars), not necessarily a ladder.
- In the CAD, batteries (dark grey) sit inside the light-grey structural links.

| Section | Source |
|---|---|
| Vision | [project.md](../truth/project.md), D-001, D-014, D-020 |
| Hardware | [robot.md](../truth/robot.md), D-002 to D-008, D-020, D-021, D-026 |
| Software | D-012 to D-014, [robot.md](../truth/robot.md#tethersmall-testbed-2026-10-11), [embedded bench note](2026-10-12-irisy-embedded-controls-bench.md) |

## Check before the review

- **Climb frame order.** The frames are ordered 5 → 6 → 4 → 3 from the attachments, by how high the green claw anchors. Confirm.
- **Torque and payload are Cove's.** ≈50 Nm and ≈7 kg are Cove as built. Mass is left off for now.
- **Link numbers come from tethersmall.** 91–94 % delivery and the 13 ms median round trip were measured on the two-motor testbed, not on three Tether modules.