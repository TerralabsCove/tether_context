---
status: draft
owner: Steve Lu
last_reviewed: 2026-11-28
---

# Sim: table-top bench, physics-proven planner, tag alignment, camera object messages. Arm: first run on the new firmware, most motor reports lost on the air (2026-11-28)

Written by Steve's AI agent on 2026-11-28, from a session with Steve at the laptop (11-27 evening) and at the arm
(11-28, about 01:30 to 02:10). Not authoritative. Follows the
[11-27 arm session note](2026-11-27-steve-arm-calibration-imu-sim-controllers.md) and runs beside the
[firmware note](2026-11-28-steve-firmware-monorepo-2g4.md), which was written in another session the same night.
Touches open questions [7](../truth/open-questions.md) (camera data path), [14 and 15](../truth/open-questions.md)
(radio margin, nodes on one channel) and [32](../truth/open-questions.md) (two end cameras, one gateway), and adds
[33](../truth/open-questions.md) (which tag plate is on which port) and [34](../truth/open-questions.md) (the
latches while the bridge runs).

Code: tethersim `main` at `9d65539` (PRs 4 to 8). tether_ros `main` at `6ea9d0a` (PR 10); PR 12 is open
(`steve/camera-ends-hold-stops`, `39d85b9`) and is what ran at the arm; PR 11 (latch control) is closed, branch
kept. tether_camera PR 6 was merged before that repo was archived, and its change is in tether-firmware
`tether_camera/`.

**The one thing to read:** with the bridge running, the gateway received 5 to 39 % of each motor's 200 Hz reports,
and the arm went limp within seconds of every enable. See [At the arm](#at-the-arm-11-28).

## Simulator (tethersim)

All of this is simulation only **[as built]**, checked in the sim's Docker image. Nothing here has moved the arm.

- **Scene `table_flat`.** The big table's 0.80 m top flat on the floor with its two ports (`short_walkway`,
  `short_bridge`, 0.58 m apart), arm upright on `short_walkway` on EE_1. The bench for docking and first moves.
- **A plan is run in full physics before it is offered** (`planning.proven`, `planning.rollout`): on a private copy
  of the world, with the real-arm motor model and the selected controller from the 11-27 note. What that exposed,
  each fixed:
  - Plans ran at 0.4 rad/s whatever the controller. Fine (0.2 rad/s) fell 46° behind and missed the port by
    30 mm. Plans now ask for 0.8 of the controller's speed and acceleration.
  - A controller with easing trails a moving target by v²/(2·acc), a different share per joint: the end left its
    path by 46 mm with Smooth on the 0.58 m step. During a trajectory the target now leads the plan by that
    much (15 mm left).
  - Going into a port 60 mm in 0.6 s wedged the nose in the ring 17 mm short (Stock). The end now stops above
    the port and goes in, and backs out, at 20 mm/s. At 40 mm/s Stock missed 1 of 7.
  - A trajectory ended on a timer. It now ends when the arm has arrived.
  - Results, each plan executed after planning: the table step docks with Stock, Smooth, Brisk and Fine; 24 of 24
    from random starting poses; the Watt Hall stage's 6-step route 6 of 6 with Stock and with Smooth. A plan
    takes about 2 s on the table scene and about 8 s a step on the stage.
- **Reach any object** (`POST /api/reach`): a port is stepped into; anything else is approached square to its
  surface to 5 mm. Picking up a magnetic box works with ideal motors and is refused with the real motor model:
  the 0.3 kg box sags the arm until it stands on the table again and the tilted tip peels the bond off.
- **Tag alignment.** The end stops above the port for 1.2 s, its camera's tag sightings of the last 0.4 s place the
  port, and the way in is aimed there; on the way in it keeps reading whichever tags are still in view (near the
  port, the plate's corner tags) and moves the aim across the port's face. Tags that agree with the scene to
  1.5 mm and 1° change nothing; tags more than 30 mm or 8° off stop the arm above the port.
  - With the port believed 0 to 22 mm and 0 to 5° from where it is (Stock, Smooth, one run each): blind, 6 of
    12 fail (from 16 mm on the nose wedges 31 to 34 mm short); with tags, 12 of 12 seat within 1.3 mm.
  - The first two versions of the on-the-way-in correction made docking worse (2 to 3 of 6 failed): they placed
    the port from the arm's command, the arm swings about its command, and the swing fed back into the aim. It
    now places each sighting from where the arm was.
- **A running path can be paused and its speed changed** (10 to 100 %) from the Plan page. A bridge following the
  sim's targets gets both.
- **The camera's object messages.** `camera_objects.py` is tether_camera `tagstream/objects.c` in Python from a
  frame's 2D boxes on (size, plane and held methods, track ids, the message's fields), checked against the C
  file on 300+ random objects **[verified against the C code, not against a camera]**. The NPU model itself is not
  run. On a 10 cm cube 0.6 m below the camera: with no surface sent, the camera's size guess (a 25 cm box) puts
  it 44 to 71 cm too far; with the surface, 0.2 to 0.4 cm when the box faces the camera.
- **The real camera's lines can be fed in** (`POST /api/robot/tags`, `/api/robot/objects`); a tag alignment then
  uses them and not the simulated camera's.

## Tag sizes: the camera's program and the dock plates

`tagstream` took every id but 0 and 2 for a 50.1 mm tag. The docks' v6 plates carry a 20.32 mm tag (id 10k) and
four 9.12 mm tags (10k+1 to 10k+4), so a plate's tags came out 2.5 and 5.5 times too far.

- tether_camera PR 6 (now tether-firmware `tether_camera/tagstream/tagstream.c`) gives `tagstream` the plates'
  sizes and adds `size_mm` to each line **[as built]**. Built for the Mac only. **Not built for the camera and
  not on either camera** as far as this session knows.
- tethersim corrects each sighting for the size its camera assumed, so either build works with the alignment
  **[as built]**.
- Check: that Mac build was run on the sim's rendered end-camera pictures of a dock plate, four poses from 3 to
  12 cm. Same tag ids in every picture; 13 sightings within 0.5 mm and 4° of the sim's geometry (most under 1°)
  **[verified against the simulator's pictures, not a real plate]**. So the ids, the tag frame, the angles and
  the camera axes agree between tether_camera and tethersim.

## Laptop side (tether_ros)

- `tools/camera_feed.py` (PR 10, merged) sends the cameras' tag lines and object messages to the sim, from gateway
  frames (the bridge does it by itself), a pc_master C5, or the camera's UDP.
- PR 12 (open): the cameras are placed by the calibration's `flip_ends` (with the ends flipped, as calibrated,
  camera 2 is on the sim's EE_1); a planned stop in the sim (a tag alignment stopping above the port, a step ending
  without latching) holds the arm where it is, where any sim fault used to drop the motors to damping; and
  `--stale-s` and `--no-send-twice`.
- **Latch control was written and set aside** (PR 11, closed). It follows the sim's latches, releases an end only
  when the other is seen docked, and never moves a latch that disagrees with the sim at enable. Tested against the
  fake end effectors only. See question 34.
- README: tether_ros is where the laptop side is started from; tethersim stays its own repo.

## At the arm, 11-28

About 01:30 to 02:10, the arm on the table bench, gateway on laptop USB. By the firmware note every board had been
flashed from tether-firmware `6f526e3` (2.4 GHz channel 11) that night; **which build each board ran during these
measurements was not checked here** **[assumed: the new builds]**. Recordings (raw gateway bytes) are on Steve's
Mac only: `~/Documents/tether-arm-logs/arm/20261128-013220`, `-013647`, `-014505`.

| What | Seen | Tag |
|---|---|---|
| Motors | All 7 report, status OK. Motor 4 showed "no CAN reply" (0xF0) for a while and recovered. | verified (recordings) |
| Module IMUs | 11, 12 and 13 report. | verified |
| End-effector boards | Both report. **Neither board's servos answer** (servo 1 and 2, both boards). | verified |
| Camera 2 | Its object messages came through the gateway into the bridge and on into the sim (shown on the sim's End 1), about 13 a second, and on UDP from the camera. It rebooted once. It saw a hand, and no tag. | verified (object messages); tags not exercised |
| Camera 1 | The gateway's link status named camera 1 for a while. No message from it arrived. | verified |
| Calibration | Steve calibrated at `vertical` from the sim panel. | as built |
| Enable | The arm went limp 0.3 to 13 s after each of 7 enables: `watchdog: motor 2: stale (5xx ms)` (once motor 1). No plan ran. | verified |

### Motor reports reaching the gateway

Each module sends every motor's report at 200 Hz and an IMU frame at 100 Hz (tethersmall `PROTOCOL.md`), so 1400
motor reports and 300 IMU frames a second leave the arm. Received, by motor 0 to 6:

| | Motor reports a second | All motors | IMU frames a second |
|---|---|---|---|
| Bridge running, limp or enabled (351 s) | 41, 19, 10, 60, 77, 46, 29 | 282 of 1400 | 15 to 30 each |
| Bridge stopped, gateway sending nothing (4 s) | 82, 52, 34, 114, 76, 43, 30 | 431 of 1400 | 120 in all |
| On 5 GHz channel 36, 11-26, laptop listening only | 0.3 to 1.3 % lost | about 1390 | 0.6 to 5.7 % lost |

**[verified]** for the first two rows (recordings; the 4 s listen is not recorded). The third row is John's
[on-arm IMU note](2026-11-26-john-imu-on-arm-bringup.md).

- Within a module the first motor arrives most and the last least (motors 2 and 6: 10 to 30 a second, gaps up to
  0.46 s). The bridge drops the arm to limp when any motor's report is older than 0.5 s, which is what tripped.
- The gateway's own counters did not rise (`queue_drops`, `short_usb_writes`): what it hears it passes on. It
  heard 440 to 540 packets a second of all kinds. The loss is on the air or in the modules' sending.
- Sending each command once instead of twice, and pausing the camera's object messages, changed nothing
  measurable. Both end-effector boards were sending telemetry (about 60 to 80 frames a second together) and
  camera 2 was being relayed (about 14 messages a second) on the same channel.
- Not done: the same listen with the end-effector boards and the cameras off; one module alone; 5 GHz again.

The gateway then left USB (the restart failed with "Board 10 gateway not found on USB") and the session ended.

## Not tested, not known

- Nothing from the new planner, the tag alignment, the path controls or the hold-on-planned-stop has run on the
  arm. Enabled never lasted long enough.
- The real cameras' tag lines have not been seen: no tag was in view. The tag alignment has only used simulated
  sightings and sim lines rewritten to the real camera's form.
- Whether the latch pins hold with their servos unpowered.
- `robot_control.py` was not run with latch control. The latch code met only the fake end effectors.
- The lens's distortion on tag poses: `tagstream` undoes it for objects, not for tags.

## Open

1. The radio. With a third or less of the motor reports arriving, the bridge cannot stay enabled at its 0.5 s
   limit. `--stale-s 1.0` would ride through the gaps seen; it was about to be tried when the gateway left USB.
   Questions 14 and 15.
2. Which numbered plate is on which real port. Question 33.
3. Camera 1 sends nothing, and the gateway takes one camera at a time. Question 32.
4. The latches while the bridge runs. Question 34.
5. tether_ros PR 12 is open. The end effectors' latch servos do not answer.
