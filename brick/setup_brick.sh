#!/usr/bin/env bash
# One-time setup on the pocket brick (Raspberry Pi 5, Raspberry Pi OS Bookworm 64-bit, desktop).
#   bash brick/setup_brick.sh
set -euo pipefail
sudo apt update && sudo apt install -y python3-opencv python3-numpy v4l-utils
# Wi-Fi hotspot the visor MCU joins (must match firmware Kconfig: ASG-BRICK / glasses123, gateway 10.42.0.1)
sudo nmcli dev wifi hotspot ifname wlan0 ssid ASG-BRICK password glasses123 || true
sudo nmcli connection modify Hotspot connection.autoconnect yes || true
# HDMI: the dual micro-OLED board expects 3840x1080 side by side [MEASURE: check your board's mode list]
echo "Set the HDMI output to 3840x1080 in Screen Configuration, then run:"
echo "  python3 $(cd "$(dirname "$0")" && pwd)/passthrough.py"
v4l2-ctl --list-devices || true
