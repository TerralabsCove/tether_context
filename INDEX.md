# Index

Every current doc, one line each. Start here.

## Source of truth

- [truth/project.md](truth/project.md): what Tether is, goals, roadmap, where things stand
- [truth/robot.md](truth/robot.md): Cove as built and Tether's design, with verified vs assumed tags
- [truth/decisions.md](truth/decisions.md): every decision, why, and where it was made (D-001 to D-023)
- [truth/open-questions.md](truth/open-questions.md): unresolved questions and risks to watch
- [truth/team.md](truth/team.md): who does what, meeting schedule
- [truth/glossary.md](truth/glossary.md): terms and acronyms

## Plans

- [plans/mocap-integration.md](plans/mocap-integration.md): motion-capture integration plan (draft, partly superseded by the 10-08 meeting)

## Meetings

- [2026-10-05 team scheduling](meetings/2026-10-05-team-scheduling.md): meeting schedule, breadboard-only electrical, no BMS, Trent as embedded lead
- [2026-10-06 mech layout](meetings/2026-10-06-mech-layout.md): offset layout, 360° middle joint, batteries, claws, 5 wireless modules
- [2026-10-08 mocap localization](meetings/2026-10-08-mocap-localization.md) (date unconfirmed): mocap as primary localization, offboard compute, no RL for now

## Assets

- [2026-09-27 kickoff deck](assets/2026-09-27-tether-kickoff.pptx): Cove history, Tether idea, sim results, roadmap

## In other repos

- [tether](https://github.com/TerralabsCove/tether): COVE2 sim. See `PROJECT_SUMMARY.md`, `docs/VALIDATION_PLAN.md`, `docs/EDITOR_ARCHITECTURE.md`.
- [cove-controls](https://github.com/TerralabsCove/cove-controls): Cove controls code and URDF
- [tethersmall](https://github.com/TerralabsCove/tethersmall): two-motor ESP-NOW + Damiao testbed; RL policy over ESP-NOW. See `docs/ESPNOW_BRINGUP.md` and the [2026-10-11 note](notes/2026-10-11-john-tethersmall-rl-over-espnow.md).
