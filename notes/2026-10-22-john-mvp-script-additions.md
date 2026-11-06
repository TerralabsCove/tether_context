---
status: draft
owner: John Peng
last_reviewed: 2026-10-22
---

# MVP presentation script: intro, video, and software (2026-10-22)

Drafted by John's AI agent to fill the empty sections of the Google Doc
[Tether MVP Presentation Script](https://docs.google.com/document/d/1eINUK2hw3YguJt-GyQVBv4ym73Za0QDc0bJGiBZm2-c/edit).
It follows the deck `Tether MVP Template (F26 - Terra Labs)`. Spoken text is plain. Stage cues are in [brackets].
Timings assume about 150 words a minute.

---

## What it is (~1 min)

[Slide 1, Tether title]

Hi, we're Tether.

Last spring, Terra Labs built Cove, a seven-joint robot arm. Like almost every robot arm, it was bolted down.
It could only work on whatever was within reach of where it was mounted.

So we asked: what if the arm didn't need a base?

[Slide 2, 7-DoF Inchworm Robot]

Tether is a 7-degree-of-freedom robot arm that moves like an inchworm. It has a claw on both ends. One end
grabs on and becomes the base. The other end swings to the next handhold and grabs. Then they swap. Repeat
that, and the arm can walk, climb, and still work as an arm wherever it ends up.

It's 1.5 meters long and weighs 9.8 kilograms. It's split into three modules, and each module carries its
own battery and its own radio. No cables run between the modules, and none run back to a wall, so the joints
can spin freely. All the computing happens off the robot: a laptop plans the motion and sends joint commands
over the air.

For Demo Day, our goal is to have Tether move across a set of bars.

---

## Hardware demo video (~1 min)

[Slide 3, video]

Keep the voice-over short and let the footage carry it. Match each cue to the final cut. Drop any line whose
clip isn't in the video.

**[Rendered segment, ~0:00–0:20]**

- *If it's the simulation:* This is Tether in our simulator. One claw anchors and the other reaches for the
  next hold. Running on our previous arm's model, it walked a meter, climbed a five-rung ladder, and circled
  a table, all without hitting itself or anything around it.
- *If it's a CAD render:* This is the full design. Three modules, aluminum links with the batteries inside,
  and a claw on each end.

**[Hardware segment, ~0:20–0:50]**

This is real hardware: three of Tether's motors, each driven by its own wireless module. There are no wires
between them.

We set the arm down in a random bent pose. The laptop sends commands over the radio, and all three joints
straighten together, arrive at the same moment, and stop within about a degree of straight. It takes just
over a second.

- *Only if the clip shows the arm on its base:* Here the same arm is bolted to a base and lifts itself
  straight up, against gravity.

**[Close, ~0:50–1:00]**

Three wireless modules acting as one arm. That's the core of Tether working. Next is all seven joints.

---

## Previous challenges: Software (~35 s)

[Slide 4, "Wireless lag past the 70 ms RL policy limit"]

On software, our biggest challenge was lag. All the thinking happens on a laptop. Fifty times a second, it
sends a command over the radio to every module and waits to hear back where the motors are. Our controller
was trained in simulation to handle a round trip of up to 70 milliseconds. On our first two-motor test,
about 1 command in 20 came back later than that, and the worst took over 200 milliseconds.

[Slide 5, "Revised radio link: 99.6% on time"]

We attacked it from both sides. In software, we trained the controller against a model of our real radio,
with delays and dropped packets built in. Every command is sent twice, and each module runs its own safety
rules: if it hears nothing for 200 milliseconds, it goes limp instead of doing something dangerous. Add a
better master radio, and now 99.6% of commands make it back within 70 milliseconds, with a typical round
trip of 12. On the three-module arm, all three hardware test runs passed.

---

## Current challenges: Software (~45 s)

[Slide 8]

We have three software challenges left.

First, Wi-Fi latency. In the standing demo, the laptop reaches the middle module over Wi-Fi instead of
through a USB radio. That hop is slower: up to 80 to 130 milliseconds round trip for the slowest 5% of
commands. That's fine for a scripted motion but at the edge for our learned controller. It's the same wired
versus wireless question electrical raised, and it's why we need range and latency tests with obstructions.

Second, gravity. When the arm stands up, the learned controller is a third faster than a scripted motion.
But in simulation it succeeds 86% of the time, against 98% for the script. So for now we run the script,
and we're working on a controller that corrects the script instead of replacing it.

Third, scale. Everything so far is three joints bending in one plane. Tether has seven joints moving in 3D,
and it needs to know where it is. Our plan is IR cameras around the demo set that track small IR LEDs on
each module, with encoders and gyros filling in between frames. That isn't built yet.

---

## Where the numbers come from

| Claim | Source |
|---|---|
| 1.5 m, 9.8 kg, 70 ms limit, 99.6% on time | The MVP deck |
| Cove: 7 joints, spring 2026, fixed base | [truth/robot.md](../truth/robot.md), [truth/project.md](../truth/project.md) |
| Claw on both ends, 3 wireless modules, battery per module, offboard compute | D-001, D-005, D-006, D-013, D-020 in [truth/decisions.md](../truth/decisions.md) |
| Demo Day bars, IR camera + IR LED localization plan | John, 2026-10-16, in the [one-pager note](2026-10-16-john-mvp-one-pager.md). Not yet in `truth/`. |
| Sim: walked 1.08 m, 5 rungs, table loop, collision-checked, on Cove's model | [truth/robot.md](../truth/robot.md#wire-routing-comparison-sim-2026-09-27) (sim, assumed) |
| 50 Hz, sent twice, 200 ms watchdog, trained on a link model | tethersmall `docs/ESPNOW_BRINGUP.md`, `docs/STRAIGHTLINE.md` |
| First test: 5.1% over 70 ms, max 212 ms | [latency slides note](2026-10-22-john-latency-slides.md), run-20261011-013601 |
| Three-module arm: 0.35% over 70 ms (99.6% on time), median 12 ms | [latency slides note](2026-10-22-john-latency-slides.md), 2026-10-19 runs |
| 3 of 3 hardware runs passed, final error under 1°, settled in 1.04–1.28 s | tethersmall `docs/STRAIGHTLINE.md`, "On hardware (2026-10-19)" |
| Wi-Fi master p95 80–130 ms | tethersmall `docs/STANDUP.md` and commit `9c1019c` |
| Stand-up in sim: policy 86% vs ramp 98%, 1.70 s vs 2.53 s; residual policy next | tethersmall `docs/STANDUP.md` |

## Check before presenting

- **"Better master radio."** The 99.6% run used an ESP32-S3 master and XIAO ESP32-C6 modules, and three
  modules instead of two. No A/B test isolates which change helped, so the script doesn't credit one. The
  C5 radios (D-029) were not in that test.
- **RL vs D-014.** The script talks about a trained controller, as the deck does. D-014 still says "no RL
  at this stage". That conflict is open in [truth/open-questions.md](../truth/open-questions.md).
- **Stand-up results are from simulation.** No hardware stand-up results are recorded yet. Use the
  "on its base" video line only if the clip shows a successful stand.
- **Time.** The electrical and mechanical sections are already long. Previous challenges (1 min) and
  current challenges (1:30) will run over if all three disciplines read their full text.
