---
status: draft
owner: John Peng
last_reviewed: 2026-11-23
---

# ESP-NOW firmware read against the reliability list (2026-11-23)

Written by John's AI agent on 2026-11-23. Not authoritative. A code read, nothing run on hardware. It follows
the [antenna placement note](2026-11-23-john-antenna-placement.md). John asked for fast, reliable ESP-NOW and for
the arm firmware to be checked against a seven-item list.

What was read:

- [tethersmall](https://github.com/TerralabsCove/tethersmall) `main` at `5e50e29` (2026-10-28): `firmware/`.
- tethersmall branch `hansi/gateway-camera` at `83f60e0` (2026-11-22, not merged): the gateway that also receives
  the end camera, and one node driving three motors.
- [tether_camera](https://github.com/TerralabsCove/tether_camera) `main`: `esp/camera_slave`, `esp/libraries/TetherLink`.
  Its 5 GHz branch was not read.
- [tether_ros](https://github.com/TerralabsCove/tether_ros) `main`: `gateway_node.py`.

## Against the list

| # | Item | In the code | Verdict |
|---|---|---|---|
| 1 | Cleanest channel | Arm boards: one define, `ESPNOW_CHANNEL_5G` (default 36), in `espnow_radio.h`. Camera side: `LINK_CHANNEL` in tether_camera's `TetherLink.h`, and a copy of that file in tethersmall. | Works. A channel change is two edits in two repos and seven boards to flash. See finding 4. |
| 2 | USB gateway, no SoftAP | `gateway_c5_5g` is a plain station with ESP-NOW. The SoftAP master is a separate build (`master_b_c6`). | Good. |
| 3 | Antennas | Not firmware. The gateway stamps each status frame with its RSSI and each node prints the RSSI it hears. | The numbers needed for the checks are already there. |
| 4 | Camera traffic against control traffic | The camera gateway handles one camera. | **Three problems.** Findings 1 to 3. |
| 5 | Radio set explicitly | 5 GHz band, modem sleep off and 6 Mbit/s are all set on the gateway and the nodes. Power is left at the chip's maximum. | Good. The result of the rate call is only kept in the `RADIO_SNIFF` build. |
| 6 | Acknowledged commands | One broadcast frame carries every motor's target. The laptop sends each one twice, 2 ms apart. No acknowledgement. | Fine as a design. **The gateway does not check whether a send worked.** Finding 5. |
| 7 | Watchdog | 200 ms without a command, then damping only, at the last commanded kd. The next command re-engages from where the joint is. | Works as written. For an arm holding itself up, damping only means it sags. Finding 7. |

## Findings, most important first

1. **Two cameras will fight over the camera link.** [assumed: from the code]
   `gateway_camera.h` keeps one peer. Every packet from the other camera makes it delete that peer and add the new
   one, inside the receive callback. Its hello goes only to the current peer once it has one. Its gap counter is
   one counter for both senders, so it will report losses that did not happen.
2. **A camera C5 takes any link packet as "the computer".** [assumed: from the code]
   `camera_slave`'s receive handler adopts the sender of any packet with the right magic and group. A second
   camera that is still broadcasting qualifies. Two cameras can start sending to each other.
3. **A camera that is off still transmits.** After 2 s with no line from the camera, `camera_slave` sends made-up
   tags 20 times a second and made-up objects, flagged `fake`. On the robot that is traffic on the motor channel
   for nothing, from a camera that is booting or unplugged.
4. **Nothing sets a Wi-Fi country.** Channels 149 to 165 may be refused without it. [assumed: not tested] The
   nodes print the channel they are really on at boot, and the camera gateway reports its own once a second.
   Check both after any channel change.
5. **The gateway throws away the result of `esp_now_send`.** It has no send counter. On 10-28 all three motors
   lost the same number of commands in every run, and that note suspected a loss before the commands split.
   One frame carries all three targets, so a frame the gateway failed to send looks exactly like that. Counting
   failed sends in the once-a-second diagnostics frame would settle it.
6. **Status frames are one per motor.** The three-motor node sends three frames every 5 ms. Seven motors would be
   1400 broadcast frames a second. At 6 Mbit/s that is roughly 30 % of the channel's time, counting the gaps
   each frame needs. [assumed: my estimate] One frame per node would cut it to 600. Broadcasts are not retried,
   so this is where collisions cost.
7. **Watchdog action.** Damping only is right for the crawler on the floor. For Tether with one end free, a
   200 ms outage lets the arm drop until commands return. Holding the last position for a short time, with the
   torque cap, is the alternative. It is a safety choice for the team, not a bug.
8. **The three-motor node is a bench build.** `NODE_MULTI` takes consecutive motor ids from `MULTI_FIRST_ID`.
   D-028's ids are not consecutive (`0x02`, `0x05`, `0x01`). No 1 + 3 + 3 arm build was found in what was read.

## Smallest fixes, in order

1. Gateway: count failed sends and report them (finding 5). A few lines, and it explains the 10-28 losses or
   rules the gateway out.
2. Camera link for two cameras: `camera_slave` takes a peer only from a hello or a command; the gateway keeps
   both cameras as peers and always broadcasts its hello (findings 1, 2).
3. Turn the made-up messages off in robot builds (finding 3).
4. One status frame per node (finding 6). This changes the wire format, so tether_ros and tethersim's gateway
   link change with it.
5. One place for the channel, and a country set at start-up (finding 4).

## Not checked

- Nothing was flashed or measured. Every finding is from reading the code.
- tether_camera's 5 GHz branch, and whatever is on the boards now.
- The laptop side beyond `gateway_node.py`'s send rate (50 Hz, each command twice).
