---
status: draft
owner: John Peng
last_reviewed: 2026-10-11
---

# tethersmall: an RL policy running over ESP-NOW on real Damiao motors (2026-10-11)

Written by John's AI agent from the bring-up session. Not authoritative. The facts promoted to `truth/` are
listed at the end.

## What tethersmall is

[TerralabsCove/tethersmall](https://github.com/TerralabsCove/tethersmall) is a small testbed built from Cove
parts: two DM10010 pitch modules and their brackets, joined by a spacer, with no other joints. It crawls on
a table by swinging its two clevises. A MuJoCo RL policy was trained for it with a model of the ESP-NOW link
(latency, loss bursts, Mac stalls) and the motor-node firmware rules (slew limit, watchdog, overspeed cut).

The question it answers: **can a learned policy on an offboard computer drive Damiao motors through
per-module ESP32s over ESP-NOW, with no wires between the modules?** That is the Tether architecture in
miniature: offboard compute (D-013), wireless modules with one ESP each (D-020), ESP-NOW first (D-019).

## Result

Yes. On 2026-10-11 the policy ran on the real robot for 20 s with no faults and reproduced the sim gait:

| | hardware | sim, same settings |
|---|---|---|
| B−A phase (target +90° ± 45°) | +89.9° | +86° |
| swing amplitude A / B | 0.45 / 0.59 rad | 0.49 / 0.57 rad |
| peak joint speed A / B | 3.25 / 3.42 rad/s | 2.86 / 3.29 rad/s |
| forward progress in 20 s | ~0.20 m, limited by cable length | 0.63 m |
| command→state round trip p50 / p95 / max | 13 / ~70 / ~210 ms | — |
| commands delivered (each sent twice) | 91–94 % | — |

The progress number isn't a policy result. The robot was tethered by cables that pulled it sideways and ran
out of slack.

Full write-up, with numbers, setup and 16 takeaways:
[docs/ESPNOW_BRINGUP.md](https://github.com/TerralabsCove/tethersmall/blob/main/docs/ESPNOW_BRINGUP.md).
Raw logs and per-run summaries:
[deploy/hardware_logs/](https://github.com/TerralabsCove/tethersmall/tree/main/deploy/hardware_logs).
Merged in [TerralabsCove/tethersmall#1](https://github.com/TerralabsCove/tethersmall/pull/1).

## Architecture that worked

```
Mac (policy, 50 Hz) --USB--> master ESP32 --ESP-NOW broadcast--> slave ESP32 A --CAN--> Damiao A
                    <-------              <-- state @200 Hz ----  slave ESP32 B --CAN--> Damiao B
```

* Master: Seeed XIAO ESP32-C3 on the Mac's USB. It forwards frames only.
* Slaves: XIAO ESP32-C3 (A) and XIAO ESP32-C6 (B), each with a CAN transceiver on D0 (TX) / D1 (RX).
* ESP-NOW broadcast, channel 11, 1 Mbit/s. Every command is sent twice and the slaves keep the newest
  sequence number. Each slave streams its motor state at 200 Hz.
* The slaves run the safety rules locally: 2.5 rad/s target slew, a 200 ms watchdog that goes limp, an
  overspeed cut at 3.5 rad/s, and a 12 Nm torque cap. The policy was trained against exactly these.
* Firmware: [firmware/](https://github.com/TerralabsCove/tethersmall/tree/main/firmware) (PlatformIO).

## Lessons that likely carry over to Tether's modules

1. **ESP-NOW works for closed-loop motor control, but with little margin.** Losses are bursty: the two
   copies of a command tend to drop together. The policy tolerated it because it was trained on bursts.
   A planner or controller on Tether needs the same tolerance, or a better link. This bears on open
   question 12 (packet loss and redundancy) and on D-019's ESB fallback.
2. **Choose the Wi-Fi channel by measuring.** Channel 1, the default, lost 10–34 % of one slave's packets
   to nearby Wi-Fi. Channel 11 lost 0 %.
3. **Losses happen at the master's radio, not at the slaves.** The slaves heard each other almost perfectly.
   Placement of the offboard-side ESP matters: away from the computer and its Bluetooth, with a clear line
   to the robot. A slave sitting right next to the master drowns out a farther one (near–far).
4. **The XIAO ESP32-C3 needs its U.FL antenna attached.** The C6 has an on-board antenna.
5. **A Damiao position reading can wrap by a full turn.** One motor's straight pose sat next to its wrap,
   and a 50° move read as −309°. Uncorrected, that is a full-turn command error that drives the joint the
   wrong way. Relevant to any Damiao joint, especially the continuous middle joint (D-003).
6. **CAN "nothing is answering" signature:** TX error counter stuck at 128, bus errors climbing ~7000/s,
   nothing received. That means motor power or CANH/CANL wiring, not IDs or software.
7. **Run safety on the module, not only on the computer.** The watchdog and slew limits on the ESP kept
   every fault benign, including an e-stop mid-motion.
8. **Ease into the start pose.** The policy's first move from flat was a fast lunge into its stance, which
   startled the operator into the e-stop. The runner now glides there first.
9. **Calibrate joint signs by moving each joint by hand.** The two motors face each other, so nobody could
   say in advance which way was positive. A tool now detects it.
10. **Toolchain:** PlatformIO's stock ESP32-C3 compiler is x86-only and fails on Apple Silicon. Use the
    pioarduino platform.

## Open items

* Command delivery of 91–94 % and RTT p95 of ~70 ms are at the edge of what the policy was trained on. Next:
  move the master off the Mac on a USB extension and try an external antenna.
* Peak joint speed on B reaches 3.42 rad/s, against the 3.5 rad/s overspeed cut.
* Route the cables and measure progress again.
* Not yet tested: three or more nodes on one channel, which Tether needs (D-020), or battery power on the
  modules (D-004, D-008).

## Promoted to truth/ on 2026-10-11 (at John's request)

* [truth/project.md](../truth/project.md): status line, and the G4 gate note.
* [truth/robot.md](../truth/robot.md): new "tethersmall testbed" section with tagged facts.
* [truth/open-questions.md](../truth/open-questions.md): the RL conflict with D-014, a note on question 12,
  and new questions.
* [truth/glossary.md](../truth/glossary.md): tethersmall, master/slave, and the XIAO variants.
