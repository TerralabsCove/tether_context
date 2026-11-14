# Index

Every current doc, one line each. Start here.

## Source of truth

- [truth/project.md](truth/project.md): what Tether is, goals, roadmap, where things stand
- [truth/robot.md](truth/robot.md): Cove as built and Tether's design, with verified vs assumed tags
- [truth/decisions.md](truth/decisions.md): every decision, why, and where it was made (D-001 to D-046; D-030 reserved)
- [truth/open-questions.md](truth/open-questions.md): unresolved questions and risks to watch
- [truth/team.md](truth/team.md): who does what, meeting schedule
- [truth/glossary.md](truth/glossary.md): terms and acronyms

## Plans

- [plans/mocap-integration.md](plans/mocap-integration.md): motion-capture integration plan (draft, partly superseded by the 10-08 meeting)

## Meetings

- [2026-10-05 team scheduling](meetings/2026-10-05-team-scheduling.md): meeting schedule, breadboard-only electrical, no BMS, Trent as embedded lead
- [2026-10-06 mech layout](meetings/2026-10-06-mech-layout.md): offset layout, 360° middle joint, batteries, claws, 5 wireless modules
- [2026-10-08 mocap localization](meetings/2026-10-08-mocap-localization.md) (date unconfirmed): mocap as primary localization, offboard compute, no RL for now
- [2026-10-12 leads, Tether items](meetings/2026-10-12-leads-tether.md): ESP and policy on hardware, MVP scope
- [2026-10-15 mount design](meetings/2026-10-15-mount-design.md): interlocking geometry instead of bolts carrying load
- [2026-10-18 docking and power](meetings/2026-10-18-docking-power.md): pins on the arm, slip ring at the end effector only
- [2026-10-19 showcase and MVP](meetings/2026-10-19-showcase-mvp.md): Fall Showcase, MVP requirements, nothing upside down
- [2026-10-25 team sync](meetings/2026-10-25-team-sync.md): missing C5s, sim plan, climb motion, 5 GHz
- [2026-10-26 MVP feedback](meetings/2026-10-26-mvp-feedback.md): task sheets, 5 weeks left, slip ring as main blocker
- [2026-11-01 designer demo](meetings/2026-11-01-designer-demo.md): Area D placement, curious-robot demo concept, look and feel
- [2026-11-01 all-hands](meetings/2026-11-01-all-hands.md): mech and electrical status, module power path, assembly dates
- [2026-11-02 leads status](meetings/2026-11-02-leads-status.md): software staffing, LiDAR and analog FPV out, task sheet format
- [2026-11-05 planning](meetings/2026-11-05-tether-planning.md): 2 weeks behind, panel contingency, backup gripper, one fisheye camera per end, no stereo

## Assets

- [2026-09-27 kickoff deck](assets/2026-09-27-tether-kickoff.pptx): Cove history, Tether idea, sim results, roadmap

## Archive

- [2026-10-22 latency slides v1](archive/2026-10-22-john-latency-slides-v1/) and [v2](archive/2026-10-22-john-latency-slides-v2/): earlier drafts of the latency slide graphics

## In other repos

- [tether](https://github.com/TerralabsCove/tether): COVE2 sim. See `PROJECT_SUMMARY.md`, `docs/VALIDATION_PLAN.md`, `docs/EDITOR_ARCHITECTURE.md`.
- [cove-controls](https://github.com/TerralabsCove/cove-controls): Cove controls code and URDF
- [tether_controls](https://github.com/TerralabsCove/tether_controls): Tether firmware and bench tools; Tether arm URDF in `description/`, step-reach sim in `sim/step_reach_sim/`
- [tethersmall](https://github.com/TerralabsCove/tethersmall): two-motor ESP-NOW + Damiao testbed; RL policy over ESP-NOW. See `docs/ESPNOW_BRINGUP.md` and the [2026-10-11 note](notes/2026-10-11-john-tethersmall-rl-over-espnow.md).
- [tether_camera](https://github.com/TerralabsCove/tether_camera): end camera code (reCamera): on-camera AprilTag program `tagstream`, tests and results. See its `README.md` and the [2026-11-13 summary note](notes/2026-11-13-john-recamera-tag-tracking.md).
