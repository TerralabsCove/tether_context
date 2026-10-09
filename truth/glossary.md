---
status: active
owner: anyone
last_reviewed: 2026-10-08
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
| Xiao | Seeed XIAO, a small microcontroller board. Which variant we have is not recorded. |
| ESP-NOW | Espressif's low-latency wireless protocol between ESPs. |
| NRF ESB | Nordic's Enhanced ShockBurst wireless protocol. |
| BMS | Battery management system. Dropped for Tether (D-008). |
| Damiao | The actuator brand used on Cove. |
| TerraGM | Terra Labs general meeting. |
| Granola | The app that records and summarizes our meetings. |
