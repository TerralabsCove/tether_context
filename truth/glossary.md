---
status: active
owner: anyone
last_reviewed: 2026-11-28
---

# Glossary

| Term | Meaning |
|---|---|
| Cove | The 7-DOF arm built in spring 2026. Fixed base, electromagnet on one end. |
| Tether | The fall 2026 project: Cove turned into a two-gripper inchworm robot. |
| COVE2 | The name for Tether in code and in the sim. |
| COVE2 Robot Studio | The browser-based sim and design tool in the tether repo. |
| Inchworm gait | One end anchors, the other swings and grabs, then they swap. |
| End A / End B | The two ends of the arm. Either can be the anchor. |
| Anchor | The end currently holding on and acting as the base. |
| Module | One physical section of Tether with its own battery, ESP, and motors. 3 planned (D-020). |
| Offset layout | The chosen joint layout: straighter than full diagonal, with an offset (D-002). |
| Inchworm / Cable 360 / Existing | The three wire-routing variants compared in sim. |
| Winding budget | How many turns a joint can rotate before its cables run out of slack. |
| Slip ring | A rotary electrical connector that allows unlimited rotation. |
| G0–G5 | Validation gates, from model freeze to integrated locomotion. |
| URDF | Robot description file used by the sim. |
| FK / IK | Forward and inverse kinematics. |
| Mocap | Motion capture: external cameras tracking markers on the robot. |
| IYA / Avalon | Group whose mocap system we hope to borrow. Contact via Ming. |
| WISP | Another team that may use mocap. |
| ESP | ESP32-family microcontroller. One per module. |
| Xiao | Seeed XIAO, a small microcontroller board. tethersmall uses XIAO ESP32-C3 (needs its U.FL antenna) and XIAO ESP32-C6 (on-board antenna). Tether's modules and master use XIAO ESP32-C5 (D-029), which has a U.FL connector and no on-board antenna. Exception: the center module is a XIAO ESP32-S3 since 2026-11-27 (2.4 GHz only). |
| ESP-NOW | Espressif's low-latency wireless protocol between ESPs. |
| NRF ESB | Nordic's Enhanced ShockBurst wireless protocol. |
| BMS | Battery management system. Dropped for Tether (D-008). |
| Damiao | The actuator brand used on Cove. |
| tethersmall | Two-motor testbed from Cove parts, used to test an RL policy and the module firmware over ESP-NOW. [Repo](https://github.com/TerralabsCove/tethersmall), archived as of 2026-11-28. Its code, including the arm's module and gateway firmware, is now the `tethersmall/` folder of [tether-firmware](https://github.com/TerralabsCove/tether-firmware). |
| Master / slave (ESP-NOW) | In tethersmall: the master ESP32 sits on the computer's USB and relays frames; each slave ESP32 drives one module's motors over CAN. |
| MIT mode | Damiao control mode: the motor runs its own PD loop toward a position target with gains sent in each command. |
| TerraGM | Terra Labs general meeting. |
| Granola | The app that records and summarizes our meetings. |
| Baum | Baum Family Makerspace, where the panels are water-jetted. Granola often writes it as "Bomb". |
| Castle | Ming's house, used as a workshop. Book through the Terrance bot. |
| reCamera | Seeed Studio's small Linux camera with its own processor. Tether uses the 2002W (D-038). |
| AprilTag | A printed square marker a camera can locate in 3D. tag36h11 is the family used in testing. |
| Terrance | The Discord bot that logs parts and Castle bookings. |
| Pizza slices | End effector parts, named for their shape. 4 make one end effector. Machined by Ming. |
| Shell | The outer cover for the arm. JC designs it. 3D printed. |
| Docking board / port | The dock Tether locks into. 7 ports on 6 floor plates in the demo setup. The boards are printed in PETG. |
| Watt Hall B1 | Level B1 of Watt Hall. The demo site and the practice site (D-051). "Watt B1" on the whiteboard. Granola writes it as "wall hole", "Wahoo" or "WPH". |
| Interactive boxes | Boxes Tether can stack. Each has a docking port, so Tether grabs it like a dock. Magnets on the boxes make them stick to each other. A possible part of the demo. |
| Roski | USC Roski School of Art and Design. The team plans to ask a Roski student for access to Watt Hall B1. |
| Mushrooms | Set pieces in the demo setup (a mushroom with a flat top, 10-19 meeting). The fallback place to practice moving between docks. |
| Glade | The experience-design team building the set Tether runs on. |
| MakerZone, Robo, Makers | Where the team 3D prints and gets filament, as named in the 11-21 meeting. |
