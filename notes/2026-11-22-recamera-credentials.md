# reCamera credentials — Tether end-effector (2026-11-22)

> NOTE: tether_context is PUBLIC. This password is published here per John Peng confirmation Nov 22 ("2, CONFIRMED") after warning that tether_context is public. Requires physical camera access to exploit.
> Private backup also in: TerralabsCove/tether_camera (private) docs/recamera-credentials.md + Notion `reCamera credentials - Tether (private)`.

- Device: reCamera 2002W (wireless, 5V) + fisheye attachment, ~90deg FOV
- Units: 2x end-effector cams (cam1 / cam2 mounted Nov 18)
- Mount: fixed mount in end-effector plate (Ming design)
- Access: Seeed reCamera-OS web UI (192.168.42.1 AP or DHCP on house wifi)
- Password: terralabs123$
- Set by: John Peng, confirmed Nov 18 + Nov 22 in #tether
- Calibration: Hansi calibrated cam2 mounted Nov 18; streaming via ESP32-C5 USB-host / UART fallback (D-049)
