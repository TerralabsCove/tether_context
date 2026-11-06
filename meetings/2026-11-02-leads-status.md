---
type: meeting
date: 2026-11-02
topic: Leads check-in. Tether status across electrical, software and hardware; demo vision; camera options; task sheets
attendees: not recorded. No speaker labels. John recorded; Steve and Ming named in the notes.
source: Granola, https://notes.granola.ai/d/11b7f3e3-c2cb-4bcb-ac16-ff8f1832d989
decisions_logged: D-034, D-035
---

<!-- Granola summary, with comments about individual members removed at John's request. Otherwise as-is.
     The camera plan here (test ESP32-CAM first) was overtaken by the 2026-11-05 meeting. -->

# Electrical Status

- All core electrical work verified and functional
- Batteries acquired, robot powered successfully
- Motor powered and tested wirelessly
- Robot now fully wireless

# Software Team Concerns

- Steve is effectively the sole active software contributor
- Proposed mitigations:
  - Shift low-level software (ESP interfacing) to electrical team
  - Leah (ECE, working on robotic arm software on another team) flagged as potential resource
  - Once robot is assembled, electrical members can be redirected to software

# Hardware Status

- Jack is highly engaged and leading hardware
  - Parts expected to be machined by this week
  - Module assembly targeting start of next week
  - Jack skipping retreat to continue work over the weekend
- Thanksgiving timeline is tight but manageable
  - John, Hansi, and Iris (1-2 days) will be around
  - Jack is local (Diamond Bar), available over break

# Demo Vision and Field Design

- Tether demo concept: robot navigating a 3D environment, picking up objects, docking
  - Mini hill terrain with docking ports at various heights
  - End effector claw for smaller objects, docking port for heavier ones
  - Designers providing visual sketches; capabilities already shared with them
- Localization approach: AprilTags on docking ports plus joint states should give sufficient positional approximation
  - No need for external localization sensor if docking port is the known reference point
- LiDAR ruled out for current scope (relevant only for future bar-swinging capability)
- Future direction floated: monkey bar swinging with proper ML, redesigned docking

# Camera and Sensor Architecture

- End effector camera needed for docking and object identification
- FPV analog systems ruled out: image quality too poor for AprilTag recognition
- Preferred pipeline: onboard compute camera handles AprilTag localization, streams XYZ/pose data over ESP-NOW
  - Keeps bandwidth low, avoids video streaming overhead
- Cameras under consideration:
  - ESP32-CAM: available now, worth testing this week; low-light quality a concern
  - OpenMV: functional but older, MicroPython-based
  - Re-Camera 2002: Ming has one, can test compute load
  - Fisheye cameras: John has researched options, will share picks
  - Stereo cameras (e.g. ZED): flagged but expensive
- Plan: test ESP32-CAM first; source a quality fisheye camera in parallel
- LED light needed at end effector for low-light conditions
- Testing to begin after Wednesday (post-3:20 PM midterm)

# Task Sheets and Timeline

- Task sheets need to be updated by tomorrow morning
  - Format: broken down per person, per task, per week
  - Must project through to Thanksgiving at minimum
  - Reference: Glade and Ripple task sheets cited as good examples
- Weekly updates required every Friday going forward
- Suggestion: members log work times on shared Google Calendar

# Club Logistics

- Funding: ~$15K from Ming, $10K from Amazon; sponsorship team also active
- New partner: Seemingly Virtual (digital twins, immersive concert design) interested in collaboration
- Metal CNC now available for machining parts
- Laser cutter: Steve may have 1-2 units at home; will check and potentially sell or lease to Terra
- Photoshoot: November 11th and 12th, 11 AM to 2 PM; John and Steve tentatively available
- Retreat payment: Steve to confirm dues were received by the right person

# Next Steps

- **Reformat Tether task sheet** (John)

  Break down by person, task, and week through Thanksgiving; follow Glade's format.
- **Test ESP32-CAM for AprilTag localization**

  Start after Wednesday 5th November (post 3:20 PM); assess image quality and compute load.
- **Source and share fisheye camera options** (John)

  Share picks in Tether chat so parts can be ordered promptly.
- **Check laser cutter stock and send photos to Ming** (Steve)

  Terra is actively looking for a laser cutter; Steve may have 1-2 units available to sell or lease.
- **Meet with Ming to discuss sensor sourcing**

  Already scheduled; follow up on camera picks and parts ordering.

---

Meeting transcript and chat: https://notes.granola.ai/d/11b7f3e3-c2cb-4bcb-ac16-ff8f1832d989
