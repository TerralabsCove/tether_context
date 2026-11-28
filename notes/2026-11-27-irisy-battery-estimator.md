---
status: draft
owner: Irisy
last_reviewed: 2026-11-27
---

# Battery runtime estimates and a charge estimator for all five packs (2026-11-27)

Written by Irisy's AI agent on 2026-11-27, from a session with Irisy. Not authoritative. Nothing here was measured on the
arm: every number comes from a model, and the inputs marked **[assumed]** are guesses. Touches
[open question 5](../truth/open-questions.md) (battery layout), [6](../truth/open-questions.md) (end-effector power) and
[25](../truth/open-questions.md) (does D-008's battery protection hold?). Code: `tools/battery_estimator.py` and
`tools/robot_control.py` in [tether_ros](https://github.com/TerralabsCove/tether_ros), branch `irisy/battery-estimator`.
Scripts and output: [2026-11-27-irisy-battery-estimator/](2026-11-27-irisy-battery-estimator/).

## What the sources say about battery life

No pack has been run down. The 2 h target (D-004) is a target, and "long enough for our use" for the end-effector pack
(John, 2026-11-20) has no number. The G4 battery bench test is not started.

## Runtime estimates

Model: the estimator in `robot_control.py` (idle watts + |torque x speed| / 0.8 + copper-loss term per motor). Torques are
the static values from John's [step-reach sim](2026-10-28-john-step-reach-sim.md) (57 Nm on the stance 10010 pitch motor,
10 to 13 Nm on the 4340 rolls). 85 % of nominal energy is usable. **[assumed]** for every input.

Walking mix (20 % standby, 45 % hold mid-reach, 35 % stepping), modules 11 and 13 sharing the anchored end equally:

| Pack | Nominal | Draw | Runtime, Monte Carlo P10 / P50 / P90 |
|---|---|---|---|
| Module 11, 6S 5,000 mAh | 111 Wh | 46 W | 1.0 / 1.8 / 3.0 h |
| Module 13, 6S 5,000 mAh | 111 Wh | 46 W | 1.0 / 1.8 / 3.0 h |
| Module 12, 2 x 3,200 mAh counted as parallel (6.4 Ah) | 142 Wh | 23 W | 2.6 / 4.5 / 7.5 h |
| Module 12 if only one 3,200 mAh pack is wired | 71 Wh | 23 W | 1.3 / 2.2 / 3.7 h |
| End effector, 3S 450 mAh, camera on | 5.0 Wh | about 5 W | 34 / 43 / 57 min |
| End effector, camera off | 5.0 Wh | about 2 W | 82 / 112 / 170 min |

- **The 2 h target holds only about half the time** for the end modules. It needs an average under about 47 W, and the walking
  mix is 46 W. Holding full reach for long, or stepping continuously, gives 1.4 h or 0.9 h.
- **The end-effector pack is the weak point.** With the camera on it lasts about 40 minutes. This disagrees with "long
  enough" only if the camera runs the whole demo.
- The 11-24 bench runs (one unloaded 4340) draw almost nothing beyond the 4 W idle figure, so they say little about the arm.
- Sag is small: 0.2 to 0.4 V at about 3 A, assuming 50 to 120 mOhm. Cutoff will come from capacity, not sag.
- The end-effector loads (camera 1.5 to 3.5 W, C5 0.35 to 0.6 W, servos 0.4 to 1.8 W, LED ring 0.1 to 0.5 W) are **[assumed]**:
  no end-effector current has been measured.

## What the motors can report

- **Every 5 ms:** position, velocity, torque, one temperature byte and a fault code (`0x09` undervoltage, `0x08` overvoltage,
  `0x0A` overcurrent, `0x0B` and `0x0C` overtemp, `0x0D` comm lost, `0x0E` overload). No voltage, no current. **[as built]**
- **At 1 Hz, new on 2026-11-27 and not flashed:** `T_POWER` carries each motor's `UV_Value`, `OV_Value` and a `VBus` field.
  It was only tested against `fake_gateway.py`. **[as built]**
- **`VBus` probably does not work.** The public register table (cmjang/DM_Control_Python, a third-party driver, not Damiao's own
  manual) lists registers 0 to 36, 50 to 55, 80 and 81. `UV_Value` (0), `OV_Value` (29) and `OC_Value` (3) are thresholds
  you set. None is a measured bus voltage or phase current. **[assumed]**, from one third-party table. Newer firmware may differ.
  Check `sw_ver` and `sub_ver` (registers 14 and 36).
- **The end-effector servos do report pack voltage and current** (0.1 V and 6.5 mA per unit, 50 Hz). That is the one real
  measurement today. **[as built]**
- Correction to my earlier answer: the 11-26 note says the firmware never reads `UV_Value`. As of 11-27 it does, and sends it.

## The estimator

The old estimator counted energy from a typed 100 %. Mine adds three things:

1. **A learned gain `g`** on the modelled power, from resting voltages at most every 10 minutes. It absorbs wrong capacity and
   wrong idle and loss constants.
2. **An uncertainty** on the charge, from the gain's uncertainty and the energy counted since the last reading.
3. **A warning level** from `pct - 1.28 sigma`: `low` at 30 %, `land` at 20 %, `empty` on a `0x09` fault.

It also handles the 3S end-effector packs (their servos give a voltage reading every frame), and the `0x09` fault as a charge reading.

Test on 300 simulated packs per row (capacity 85 to 100 % of nominal, true loss constants differing from the repo's, 3 h walking session):

| | Charge error at 60 min, P90 | "Land now" failed |
|---|---|---|
| Old: count from 100 %, never corrected | 30.5 % | 23 % |
| One typed voltage at plug-in, then counting | 21.5 % | 9 % |
| Plus a resting reading every 10 to 15 min and the learned gain | **7.9 %** | **14 %** |

- **Charge tracking improves a lot. The warning does not yet.** "Failed" means no warning, or under 5 minutes left when it
  fired. The new estimator warns at about 25 % true charge, against 36 to 38 % before, so it wastes less battery, but it misses more
  often than a single typed voltage. It is overconfident once it has a reading. I did not find why.
- Minutes remaining are not offered as a result. They are very noisy (P90 error about 110 minutes at 60 minutes).
- These are simulated packs that use the same family of model as the estimator, so the result flatters it.
- **Not run on the arm or with the sim.** `robot_control.py` as a whole needs the sim; 44 unit tests pass (28 existing, 16 new).

## What I would do on the robot

1. Raise `UV_Value` to about 21 V on all seven motors (open question 25), so the hard cutoff is predictable.
2. Assume a motor undervoltage fault drops the arm: it kills holding torque. Do not hold full-reach poses near the end.
3. Get a real pack voltage: a divider into a C5 ADC pin (D0 is the only ADC header pin and INT uses it), or clip-on LiPo alarms.
4. Run one pack down on the bench while logging, and run the end-effector pack down from the servo readings. That checks `g`.
5. Log a resting voltage reading every 10 minutes during the demo, with the arm idle.

## Open

- Whether `VBus` returns anything on our motors.
- How the middle module's two 3,200 mAh packs are wired (parallel, or one in use). It sets 71 or 142 Wh.
- The end-effector rail load. One USB power-meter reading on the camera and C5 would replace the assumed 3.3 W.
- Why the "land now" warning is overconfident, and whether the 20 % threshold is right.
