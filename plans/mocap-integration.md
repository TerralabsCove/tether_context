---
status: draft
owner: Steve Lu (software), Trent + Jason (mocap execution)
last_reviewed: 2026-10-08
source: copied from tether repo docs/MOCAP_INTEGRATION_PLAN.md (untracked there), drafted 2026-10-08
---

> **Read this first.** This plan was drafted before or alongside the mocap localization meeting. Where they differ, the meeting decisions win.
>
> - The meeting's source order is IYA/Avalon, then WISP, then open-source, then encoders (D-018). This plan assumes OptiTrack or Vicon and surveys open-source fallbacks in section 9.
> - This plan treats mocap as lab-only ground truth. The meeting treats it as primary localization. That is open question 2 in [open-questions.md](../truth/open-questions.md).
> - RL is deprioritized (D-014), so section 6 is future work.
> - The `cove2/...` paths refer to code in the [tether repo](https://github.com/TerralabsCove/tether).

# COVE2 Motion-Capture Integration Plan

_Drafted 2026-10-08. Target systems: OptiTrack (Motive + NatNet) and Vicon (Nexus/Tracker + DataStream SDK). Status: proposal, nothing implemented yet._

## 1. Why mocap matters more for COVE2 than for a fixed-base arm

COVE2 has no fixed base. Its world pose is defined by whichever end is currently anchored. Joint encoders tell us the *shape* of the chain; they do not tell us:

- where the robot actually is in the world after N anchor handovers (drift accumulates per cycle),
- whether the anchored end stayed put or slipped during a swing,
- how far the free end actually landed from the commanded anchor target,
- how much the links deflect under gravity in a cantilevered swing.

Every one of those is a core evaluation output in `docs/VALIDATION_PLAN.md` (distance per cycle, slip/regrasp rate, cycle success, anchor placement). Mocap is the only practical way to measure them on hardware. It is also the instrument that can turn the URDF from "assumed" into "verified" (gate G0), which `AGENTS.md` currently flags as unverified.

**Design principle:** mocap is a **privileged, lab-only ground-truth signal**. It is used for calibration, evaluation, system identification, and reward computation. The deployed policy must not depend on it unless the deployment environment is guaranteed to have cameras.

## 2. Hardware and capture-volume plan

### 2.1 Clarifying "IR blasters"

OptiTrack Prime/PrimeX and Vicon Vero/Vantage cameras have IR strobe rings built in. With passive retroreflective markers, no additional IR emitters are needed and extra IR floodlights will *hurt* (they wash out marker contrast and create false blobs). Two readings of "IR blasters" make sense:

| Meaning | Recommendation |
|---|---|
| Extra IR illuminators in the room | Do not add. Rely on camera strobes. |
| Active LED markers (OptiTrack Active tags / Vicon active wand) | Useful *later* if passive marker labeling swaps become a problem on the folded robot. Start passive. |

### 2.2 Markers on the robot

Treat each rigid link as a **rigid body** (OptiTrack "Rigid Body", Vicon "Object"). Two tiers:

- **Minimum viable (phase 1-3):** End A hardware (`part_1_12`), End B hardware (`wrist_link`), and one mid-chain link. Three bodies are enough for anchor-pose error, drift per cycle, and slip detection.
- **Full chain (phase 3+):** all eight rigid links (base + seven moving). This enables per-joint kinematic calibration and deflection measurement.

Marker cluster rules:

- 4-5 markers per body, non-coplanar, asymmetric, and **a different geometry on every body** so the tracker can auto-label after occlusion.
- Mount on 3D-printed bases that bolt to existing holes. Record the base-to-link transform from CAD and add each marker base as a **fixed joint in the URDF document** (`marker_A`, `marker_B`, `marker_link3`, ...). The URDF then remains the single source of truth for marker frame offsets, which the editor already stores and materializes.
- Keep the cluster away from the contact end so it does not interfere with anchoring, and far enough from other links that a fully folded pose (the IK "retract" states in `terrain.py`) does not merge two clusters.
- Cover shiny aluminum and polished fasteners with matte tape. Reflections are indistinguishable from markers.

### 2.3 Markers in the environment

Everything the planner reasons about becomes a tracked rigid body or a probed static:

| Object | Tracked how | Feeds |
|---|---|---|
| Ground plane | Probe three points, or calibration square on the floor | `ground_z` in terrain runs |
| Ladder | Rigid body on the rails plus one-time probe of each rung axis | rung centers and front-tangent contact points in `terrain.py` |
| Table | Rigid body on the tabletop plus probed corner points | table side length and face normals in `table.py` |
| Scaffold members / payload | One rigid body each | task-program grip and release poses |

Measure environment geometry once per session with the vendor probe tool and write it into the scenario config as **measured** values, not the assumed defaults.

### 2.4 Volume and camera count

The ladder challenge is 1 m of ground walking plus five rungs at 0.22 m pitch, so the volume is roughly 2 m x 2 m footprint by 2 m tall, with the ladder itself as a large occluder in the middle. Plan for 8-12 cameras in a ring at two heights, with at least two cameras looking through or past the ladder from the back side. Self-occlusion during folding and climbing is the main risk, not raw accuracy.

### 2.5 Time synchronization

Both vendors stream at 100-360 Hz. Robot control is 50 Hz and physics 500 Hz in the RL contract. Options in order of preference:

1. **Hardware sync:** OptiTrack eSync or Vicon Lock box emits a frame pulse that the robot controller records. Best, cheapest in engineering time if the box is available.
2. **Software sync:** timestamp mocap frames on arrival at the host and estimate latency with a sync gesture (tap the anchored end; find the step in both encoder and mocap streams). Expect 5-15 ms latency, which is tolerable for evaluation but marginal for closed-loop use.

Every stored frame carries three times: mocap frame number, mocap timestamp, and host monotonic time. This satisfies the telemetry invariant in `AGENTS.md` (sequence plus simulation time) once the sim clock is aligned to host time at episode start.

## 3. Frames and calibration chain

```
mocap_world ──(calibration square)──► sim_world (Z-up, origin on a physical fiducial)
    │
    ├─ T_world_markerA ──(URDF fixed joint)──► T_world_A   (part_1_12 frame)
    ├─ T_world_markerB ──(URDF fixed joint)──► T_world_B   (wrist_link frame)
    │                                              └─ + 49.5 mm local Z ──► B contact point
    └─ T_world_marker_i ──────────────────────► T_world_link_i
```

**Calibration procedure (one lab session, repeatable):**

1. Place the calibration square so mocap world matches sim world: Z up, origin on the ground at a marked floor fiducial, X along the ladder approach direction.
2. Fixture the robot at q = 0 with End A bolted down. Record 10 s of marker data. Solve each marker base's offset to its link frame and compare to CAD. Any residual above a few millimeters means the CAD mount transform or the URDF link origin is wrong.
3. Move each joint through a sweep one at a time. Fit the axis direction and the center of rotation from the downstream marker body's motion. This is a direct check of the Z-Y-Z-Y-Z-Y-Z axis assignment and of the link transforms in `simple_assembly.urdf`.
4. Probe the B contact tip with the vendor probe. This verifies or replaces the assumed 49.5 mm offset that `terrain.py` currently takes from the mesh envelope.
5. Write results to `artifacts/mocap/calibration/<date>/` and copy the verified numbers into the document's `evidence.verified` list.

Step 3 is the single highest-value thing mocap can do for this project today: it closes gate G0 and makes every downstream IK, collision, and motion result trustworthy.

## 4. Software: a `cove2/mocap/` package

Mirror the existing streaming pattern (`cove2/rl/streaming.py`, `cove2/gait/streaming.py`) so the UI, artifacts, and replay reuse what already exists.

### 4.1 Adapter layer

```
cove2/mocap/
  backend.py        # abstract MocapBackend: connect(), frames() async iterator, rigid body registry
  optitrack.py      # NatNet client (Motive streaming, UDP multicast)
  vicon.py          # Vicon DataStream SDK client
  vrpn.py           # optional: common denominator, both vendors can stream VRPN
  file.py           # replays exported CSV takes (Motive export, Vicon CSV) at recorded rate
  frame.py          # normalized MocapFrame dataclass and validation
  align.py          # marker-body -> URDF link transforms, world alignment, time offset
  fusion.py         # joins encoder q + mocap into one StateFrame; FK residuals per link
  session.py        # MocapSessionManager: WebSocket broadcast + atomic artifacts + readback
```

Build the `file.py` backend first. It lets the whole pipeline (artifacts, replay overlay, metrics) be developed and tested against exported takes before any lab time, and it makes tests deterministic.

### 4.2 Normalized frame schema

```json
{
  "kind": "mocap_frame",
  "sequence": 1234,
  "mocap_frame_id": 48812,
  "mocap_time": 406.7667,
  "host_time": 1759900000.123,
  "rigid_bodies": {
    "end_A":  {"pos": [x,y,z], "quat": [x,y,z,w], "mean_error_m": 0.0003, "tracked": true},
    "end_B":  {"pos": [...],   "quat": [...],      "mean_error_m": 0.0004, "tracked": true},
    "ladder": {"pos": [...],   "quat": [...],      "mean_error_m": 0.0002, "tracked": true}
  },
  "unlabeled_marker_count": 2,
  "dropped_since_last": 0,
  "artifact_verified": false
}
```

The fused state frame adds the robot side:

```json
{
  "kind": "state_frame",
  "sequence": 1234,
  "host_time": ...,
  "q": [7], "q_dot": [7], "q_unwrapped_turns": [7],
  "anchor_state": {"A": "anchored", "B": "free"},
  "gripper": {"A": {"current_a": ..}, "B": {...}},
  "measured":  {"T_world_A": [...], "T_world_B": [...], "T_world_link": {...}},
  "predicted": {"T_world_A": [...], "T_world_B": [...]},
  "residual":  {"B_pos_m": 0.0041, "B_rot_deg": 0.8, "A_drift_m": 0.0002}
}
```

`predicted` is FK from encoders, rooted at the **measured** pose of the anchored end at the moment of anchoring. `residual` is therefore compliance, backlash, and link deflection for the free end, and slip for the anchored end.

### 4.3 Artifacts and replay

- Sessions write to `artifacts/mocap/<session_id>/` with `manifest.json`, `frames.jsonl` (or parquet), and `latest.json` written atomically and read back, exactly like the RL stream.
- A session loader converts a recorded session into the existing replay-frame shape (full link poses per frame) so the **Motion > Replays** browser can show measured link poses overlaid on the planned ones. Add a "measured vs planned" toggle and a residual strip under the frame strip.
- A **Parity** tool entry that lists calibration sessions and shows which URDF quantities are verified by which session.

## 5. How mocap plays with planning

The motion planners (`terrain.py`, `table.py`, `task.py`) currently plan against *assumed* environment geometry and *assume* every anchor lands where commanded.

1. **Measured environment in.** Session calibration writes rung positions, table faces, and ground height into the scenario config. The planner plans against the real ladder, not the default one.
2. **Anchor-pose correction.** After each anchor handover, re-root the plan at the measured pose of the new support end instead of the commanded one. This is a small change to the support runner (it already distinguishes endpoint frame from contact point) and it stops world drift from compounding across cycles.
3. **Slip and failure labeling.** While an end is flagged anchored, any motion of its rigid body above a threshold (start with 2 mm or 1 degree) is a slip event. These become the ground-truth labels for the slip/regrasp metric and for anchor-FSM "verify" step tuning in gate G2.
4. **Replan trigger.** If the landed pose error exceeds the IK approach tolerance (the table loop already enforces 2 mm face-normal error), the runner issues a corrective approach from the measured pose rather than proceeding.

## 6. How mocap plays with the RL pipeline

The RL contract observes joint position, joint velocity, endpoint pose, anchor state, a contact peak window, and winding state, and outputs a residual joint target on top of nominal IK. Mocap enters in four distinct roles. Keep them separate.

### 6.1 System identification before training (G0-G2)

Residuals from section 4.2 give measured ranges for exactly the things gate G3 says to randomize: anchor spacing and orientation error, alignment error, and effective actuator strength (from commanded vs achieved joint motion under load). Replace guessed randomization ranges with measured distributions. This is where most sim-to-real transfer is won or lost.

### 6.2 Privileged information during training (asymmetric actor-critic)

In simulation the world pose of every link is free. Train the critic (or a teacher policy) with full world-frame state, and the actor with only the deployable observations above. Mocap on hardware then provides the *same* privileged signal for real-world evaluation of the critic's value estimates, which is a useful early warning of sim-to-real mismatch. The actor never sees it.

### 6.3 Evaluation and reward on hardware (G5)

Deterministic seeded evaluation stays separate from training curves, as the playbook requires. Define every evaluation metric **once**, as a function of a `state_frame` sequence, and compute it identically from the simulator and from fused hardware logs:

| Metric | From mocap |
|---|---|
| cycle success | free end rigid body within tolerance of target contact pose at anchor time and anchor state transitions to anchored |
| distance per cycle | displacement of the newly anchored end's rigid body between consecutive anchor events |
| slip / regrasp rate | anchored-body motion events per cycle |
| peak support-end wrench | not from mocap; from gripper or wrist sensing. Mocap gives the lever arm. |
| minimum joint margin, winding | from encoders, unchanged |

Hardware episodes get the same manifest, seed, and `latest.json` readback as sim runs so the Compare tool can put them side by side.

### 6.4 Real-world fine-tuning (optional, later)

If real-world residual fine-tuning is ever done, mocap supplies the reward (progress along the ladder, placement error). Guard it: bounded residual action, mocap tracking validity as a hard episode-termination condition, and a watchdog that freezes the robot when `tracked` goes false on the anchored end.

### 6.5 What the policy should never do

Do not add mocap poses to the policy's observation vector. Do not let the hardware state estimator fall back to mocap silently. If a mocap-dependent estimator is ever needed for a demo, make it an explicit, separately named config so the evidence lists stay honest.

## 7. Phased delivery

| Phase | Deliverable | Needs lab? | Gate |
|---|---|---|---|
| 0 | Vendor choice, sync method, marker base CAD, marker frames added to URDF documents | No | - |
| 1 | `cove2/mocap/` with `file.py` backend, normalized frames, atomic artifacts, tests on exported sample takes | No | - |
| 2 | Static calibration session: world alignment, marker offsets, per-joint axis fits, probed B tip. Parity report. Evidence lists updated. | Yes (half day) | G0 |
| 3 | Live backend (NatNet or DataStream), fused state frames, replay overlay in Motion > Replays | Yes | G2 |
| 4 | Scripted hardware trials of the ground and table programs with measured environment; residual distributions exported as randomization ranges | Yes | G2 / G5 (supported) |
| 5 | Shared metric library used by sim eval and hardware eval; Compare tool shows both | No | G3 / G5 |
| 6 | Optional real-world fine-tuning with mocap reward and safety guards | Yes | G5 |

Phases 0, 1, and 5 are pure software and can start now.

## 8. Risks and mitigations

- **Occlusion while folded or on the ladder.** Camera placement at two heights, asymmetric clusters per body, and marking frames with `tracked=false` rather than interpolating silently.
- **Marker-to-link calibration error dominates.** Sub-millimeter camera accuracy is wasted if the mount transform is off by 3 mm. The multi-pose fit in section 3 step 3 is required, not optional.
- **Reflective surfaces.** Matte tape before the first session. Budget time for it.
- **Clock drift between mocap host and robot controller.** Re-estimate offset at the start of every session and store it in the manifest.
- **Flexible links.** The rigid-body assumption breaks under cantilever load. This is a feature: residual between adjacent link bodies is the deflection measurement needed for the G2 wrench budget.
- **Mocap becoming a hidden dependency.** Section 6.5. Review any PR that adds a mocap import outside `cove2/mocap/` and `cove2/eval/`.

## 9. If OptiTrack/Vicon cannot be moved: open-source and low-cost alternatives

Surveyed 2026-10-08. There is no mature open-source replacement for a commercial passive-marker system. The DIY infrared projects stop at single-marker 3D points at roughly centimeter accuracy and leave rigid-body labeling to you. The two credible routes are below, ranked for this project.

### 9.1 Tier A (recommended): Vive trackers + Lighthouse base stations + libsurvive

- **What it is.** SteamVR Lighthouse 2.0 base stations sweep the room with IR lasers; a Vive Tracker 3.0 has photodiodes plus an IMU and solves its own 6DoF pose. It is infrared optical tracking, just inside-out instead of outside-in.
- **Open-source side.** `libsurvive` (MIT, Python bindings `pysurvive`, Linux and Windows) replaces SteamVR entirely and emits name, timecode, position, and quaternion per tracked object. SteamVR remains available as a fallback for comparison.
- **Accuracy.** A 2023 Sensors study tested Tracker 3.0 against a UR10 arm as ground truth: sub-millimeter and sub-degree static error, sub-millimeter dynamic error that degrades with speed, and four base stations noticeably better than two. That is well inside the 2 mm approach tolerance the table loop enforces. libsurvive itself publishes no accuracy figures and one third-party study saw radial drift away from the calibration origin, so measure it in our volume with the UR-style check (section 3 step 2) before trusting it.
- **Fit for COVE2.** One tracker per end gives everything section 6 needs (anchor pose, drift, slip, landing error). A third mid-chain tracker gives deflection. Trackers are about 75 g and 100 mm wide, so they are the dominant mass on a small link; the URDF documents must carry them as fixed links with mass so IK, collision, and motor-time stay honest. Each tracker needs line of sight to at least one base station, and a folded pose will occlude some sensors; four base stations at two heights is the safe layout. Power and data over USB is fine for a tethered robot and avoids the radio dropouts libsurvive warns about.
- **Cost and effort.** Roughly 2-3 trackers and 4 base stations, well under the cost of one OptiTrack camera. Software effort is one `vive.py` backend behind the existing adapter interface.
- **What it cannot do.** It does not give per-marker points, so it cannot replace the probe-based environment survey in section 2.3. Survey the ladder and table once with a tracker held against reference points instead.

### 9.2 Tier B: fiducial-tag multi-camera rig (AprilTag / ChArUco)

- **What it is.** Three to six global-shutter USB cameras around the volume, a tag board bolted to each link, calibration with `caliscope` or `multical`, pose from OpenCV plus multi-view fusion. Visible light, not IR.
- **Why it is interesting here.** Each tag carries its ID, so the marker-swap and labeling problem that breaks DIY passive-marker systems on a folding robot does not exist. Every link is identified by construction.
- **Accuracy.** Published single- and overhead-camera results sit at 10-35 mm; with several tags per body, multi-view fusion, and careful calibration, low-millimeter is plausible but not demonstrated in the literature we found. Good enough for drift-per-cycle and slip detection, marginal for 2 mm approach checks.
- **Effort.** Highest software effort of the options: calibration, synchronization, and fusion are all ours.

### 9.3 Tier C: DIY passive-IR projects (reference only)

| Project | State | Why not primary |
|---|---|---|
| Low-Cost-Mocap (jyjblrd) | MIT, PS3 Eye cameras via pseyepy, ESP32 sync, OpenCV SFM build required | Built for drones; no rigid-body labeling; author calls docs weak; needs contrib OpenCV build |
| MoCapRasp (debOliveira) | AGPL, Raspberry Pi NoIR cameras, IR LED rings, about 1 cm with 4 cameras, 90 fps | Archived Aug 2025; 1 cm is too coarse; no 6DoF bodies |
| ARAS IR-Tracker | LGPL, PS3 Eye or custom nodes, ESP32 or NTP sync | Single-marker 3D only; 6DoF listed as future work; 18 commits |

Any of these would need rigid-body fitting, labeling across occlusion, and sync written from scratch to reach the plan's needs. Use them as reference for camera sync and IR filter hardware, not as the tracking stack.

### 9.4 Tier D: markerless (FreeMoCap, Pose2Sim, anipose)

Built around human and animal skeleton keypoints. No robot-link detector exists, so they do not apply without training a custom keypoint model. Not recommended.

### 9.5 Decoupling the G0 audit from the mocap decision

The static URDF audit in section 3 does not need a room-scale system. Options that need no borrowed equipment:

- a single high-resolution camera with a ChArUco board on each link, photographed at q = 0 and through single-joint sweeps, gives sub-millimeter relative link poses at under 1 m range;
- a half-day booking on the borrowed OptiTrack or Vicon for the calibration session only is a far smaller ask than relocating the system, and the artifacts it produces (section 3 step 5) outlive the booking.

Recommended path: do the G0 audit with whichever of these is available first, build the software against the `file.py` backend, and buy the Vive kit for the dynamic trials in phases 3-4.

## 10. Open decisions

1. Can the borrowed OptiTrack/Vicon be booked for a half-day calibration session even if it cannot be moved? If not, section 9 applies and the Vive route is the default.
2. Hardware sync box available, or software sync?
3. Ends-only markers first, or full-chain from the start? Full chain costs eight printed mounts and more labeling work but is required for per-joint axis verification in phase 2.
4. Will the deployment environment ever have cameras? This decides whether a mocap-assisted state estimator is allowed to exist at all.
