---
status: draft
owner: John Peng
last_reviewed: 2026-11-20
---

# reCamera as USB host for the end-effector C5 (2026-11-20)

Written by John's AI agent from a working session with John on 2026-11-20. Not authoritative. Nothing here
changes `truth/`.

The question: can the end-effector ESP32-C5 get tag data from the reCamera over USB-C, without opening the
camera? This answers John's 11-18 #tether question on getting AprilTag pose into the end-effector C5. It touches
[open question 7](../truth/open-questions.md) (camera data path).

It sits beside the [UART link note](2026-11-19-john-camera-c5-uart-link.md), which wires the camera's debug UART
test pads (TP1, TP6) to the C5. That route means opening the camera. This note looks for one that doesn't. See
[Relation to the UART note](#relation-to-the-uart-note).

## Bottom line

- **A plain cable between the two won't work as shipped.** The C5's only USB is a fixed serial + JTAG device. It
  has no host mode ([Espressif](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/usb-serial-jtag-console.html)).
  The reCamera boots as a USB device too (the network link at 192.168.42.1). One side has to be the host.
- **The camera can be the host.** It switched to USB host mode and back from software, with no replug.
  **[verified]**, one camera, no device attached.
- **The camera has no serial driver for the C5, but doesn't need one.** Python on the camera did a raw USB
  transfer through `/dev/bus/usb`. A short script can talk to the C5 that way. **[verified]** for the raw
  transfer, against the camera's own root hub. Not yet tried with a C5.
- **The C5 can't power the camera through its USB-C.** A load switch blocks that path. Feed 5 V into the cable
  instead (see Power). **[verified]** from the schematic, not measured.
- **Not yet tested:** a C5 plugged into the camera in host mode. That is the next step.

## Options considered

| Option | What | Status |
|---|---|---|
| A | Camera as USB host, C5 as USB device | Chosen to try. Camera side checks out |
| B | XIAO ESP32-S3 as USB host between camera and C5, UART to the C5 | Fallback. The S3 has USB host and Espressif ships an [RNDIS host driver](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_host/usb_rndis.html), so it could read `tagstream`'s UDP over the camera's existing USB network with no camera changes. Costs an extra board. The S3 is 2.4 GHz only, so it can't replace the C5 on the 5 GHz link |
| UART | Camera debug UART test pads to the C5 | Covered in the [UART link note](2026-11-19-john-camera-c5-uart-link.md). Needs the camera opened |
| Wi-Fi | Camera joins a C5-hosted network | Not pursued. The [UART link note](2026-11-19-john-camera-c5-uart-link.md) (option C) advises against it: it puts Wi-Fi station traffic on the motor channel |

## What the camera has

Checked over SSH on 2026-11-20. This was **not camera 2**: its hotspot is `reCamera_E49A4F`, and camera 2's
is `reCamera_02DE69`. Which unit it is wasn't recorded. Linux 5.10.4, Buildroot.

| Check | Result |
|---|---|
| Host switch | `/proc/cviusb/otg_role` exists, `device` at boot |
| USB controller | `CONFIG_USB_DWC2_DUAL_ROLE=y`, `CONFIG_USB=y`, root hub `1d6b:0002` present |
| Serial driver | `CONFIG_USB_ACM` and `CONFIG_USB_SERIAL` not set. No module in `/mnt/system/ko` |
| Raw USB from user space | `usbfs` driver present. `/dev/bus/usb/001/001` exists |
| Tools | Python 3.9 (`ctypes`, `fcntl`, no pyusb), `lsusb`, `node`. No libusb |
| Root | `recamera` user has passwordless `sudo` |
| Reach while USB is host | Its own hotspot `reCamera_E49A4F`, 192.168.16.1, 2.4 GHz ch 6 |
| CAN | `mcp251xfd` driver loads, but dmesg says "Failed to detect MCP2518FD". No CAN chip |

reCamera-OS ships the switch as `/etc/uhubon.sh host|device`
([source](https://github.com/Seeed-Studio/reCamera-OS)). On this camera, `dwc2` is built in, so writing the proc
file is enough.

## Tests run

1. **Host mode round trip.** A detached script ran `echo host > /proc/cviusb/otg_role`, waited 10 s, then
   `echo device`. In host mode only the root hub showed, as expected with the Mac on the cable. After the revert,
   the gadget was `configured`, `usb0` was up, and the Mac reconnected with no replug. dmesg: "Do port resume
   before switching to device mode", then re-enumeration. The camera stayed powered from the Mac's VBUS while in
   host mode. **[verified]**
2. **Raw USB control transfer.** Python `fcntl.ioctl(USBDEVFS_CONTROL)` with a GET_DESCRIPTOR request on
   `/dev/bus/usb/001/001` returned the 18-byte device descriptor (`1d6b:0002`). On this camera the ioctl number
   is `0xc0185500` and the struct is 24 bytes. **[verified]**

Both scripts were left in the camera's `/tmp`, which clears on reboot. They are not saved in any repo.

**Hazard: don't read `/proc/cviusb/chg_det`.** A batch of read-only checks that included it hung, and the camera
dropped off USB until it was replugged. That read is the likely cause, probably a charger-detect that resets the
port. Not confirmed.

## How the bridge would work

The C5's USB port is a serial device with two bulk pipes, in and out. A script on the camera finds the C5
(`303a:1001`), claims its data interface, and writes `tagstream`'s packets to the out pipe. It uses the same
`usbfs` calls as test 2. No kernel change and no reflash. The C5 firmware reads its USB serial and forwards over
ESP-NOW. Neither is written yet. Camera code goes in `tether_camera`.

## Power

From the XIAO schematics, checked 2026-11-20:

- **XIAO ESP32-S3 (v1.4):** both USB-C VBUS pins and the 5V pad are the same `VBUS` net. 5 V on the pad comes out
  of the USB-C port. ([schematic](https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32S3/new-res/202003751_XIAO%20ESP32S3_v1.4_SCH_260226.pdf.pdf))
- **XIAO ESP32-C5 (V1.1):** USB-C VBUS (`TYPEC_5V`) goes through a load switch, U4 (TPS22916CNYFPR), to the
  `VBUS` net and the 5V pad. The switch turns on only when 5 V is at the USB-C port. It blocks reverse current
  (300 nA max, [TI datasheet](https://www.ti.com/lit/ds/symlink/tps22916.pdf)). So 5 V on the pad does not reach
  the USB-C port. The CN version has no output discharge. ([schematic](https://files.seeedstudio.com/wiki/XIAO_ESP32C5/res/Seeed_Studio_XIAO_ESP32C5.pdf))
- V1.0 C5 boards (2025-07-01) had no U4. The revision log says "V1.1: Add U4, U10". Our boards are probably
  V1.1. Not checked. To check: feed 5 V into the pad and measure VBUS at the USB-C port. About 0 V means V1.1.

The camera is powered through its USB-C, so in Option A the 5 V has to go into the cable.

**Spliced cable (planned):**

- Use a USB 2.0 data cable, not charge-only.
- Strip a window. Splice the buck's + onto VBUS and − onto GND and the shield. VBUS doesn't need cutting. Both
  ends get 5 V, and the C5's load switch turns on from it.
- Leave D+, D− and CC alone. The C5's USB is full speed (12 Mbit/s), so a short splice is fine.
- Buck at 5.0–5.1 V. Check polarity before connecting the camera. An inline 1.5–2 A fuse is cheap insurance.
  Camera draw is budgeted at 5 W **[assumed]**, about 1 A.
- Never plug either end into a laptop while the buck is on. The buck would push 5 V into the laptop's port. Turn
  it off to flash the C5 or SSH into the camera.
- Bench alternative: USB-C screw-terminal breakouts instead of cutting a cable. A phone-style USB-C OTG splitter
  with a charge input might also work. Untested.

## Relation to the UART note

- **USB is not ruled out after all.** The [UART link note](2026-11-19-john-camera-c5-uart-link.md#ruled-out)
  lists USB as ruled out because both ends are USB devices. That holds for the C5. The camera, though, can switch
  to USB host (test 1 above). That note is left as it is. This one updates it.
- **Where the C5 sits decides it.**
  - On 11-19 John said the slip ring is dropped and the end effector gets its own power and radio. These are being
    filed as D-047 and D-048 and are not in `truth/` yet. If they hold, the C5 sits next to the camera on the end
    effector. USB is then a short cable with nothing in between. This is the case this note assumes.
  - If the camera stays on the far side of a slip ring from the module's ESP ([D-044](../truth/decisions.md),
    [D-033](../truth/decisions.md)), UART needs one signal wire through it, and USB needs two, D+ and D−, as a
    12 Mbit/s pair. Signals through this slip ring are untested. In that case UART is the safer bet.
  - A C5 at the end effector is one more radio per end on the ESP-NOW channel
    ([open question 15](../truth/open-questions.md)), with its antenna on a rotating part. The UART note's
    alternative B has the same cost.
- **Power plans agree.** Both notes have the camera and its C5 on one 5 V buck converter.

## Next

1. Bench test with a C5. Power from a bench supply at 5 V with about 1.5 A current limit, through the spliced
   cable or breakouts. Join the camera's hotspot, `sudo sh -c 'echo host > /proc/cviusb/otg_role'`, and check
   `lsusb` for `303a:1001`.
2. If it shows up: write the camera-side bridge script and the C5 forwarder in `tether_camera`. Measure latency
   and packet rate.
3. If it doesn't: try Option B with an S3.
4. Decide whether host mode is set at boot. While it is, SSH over USB is gone and the camera is reached over its
   hotspot.
