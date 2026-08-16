#!/usr/bin/env python3
"""Animate the brick-built night emblem on the 2.1-inch round display."""

import signal
import time
from pathlib import Path

from PIL import Image

from library.lcd.lcd_comm import Orientation
from library.lcd.lcd_comm_rev_c import LcdCommRevC


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "res" / "custom" / "bat-emblem-480.png"
PORT = "/dev/serial/by-id/usb-Android_Android_20080411-if00"
FRAME_SECONDS = 0.12
ROTATION_STEP = 6

running = True


def stop(*_args):
    global running
    running = False


def main() -> None:
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    screen = LcdCommRevC(com_port=PORT, display_width=480, display_height=480)
    screen.InitializeComm()
    screen.SetBrightness(level=35)
    screen.SetOrientation(Orientation.PORTRAIT)

    source = Image.open(SOURCE).convert("RGB")
    angle = 0
    while running:
        frame = source.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=(0, 0, 0))
        screen.DisplayPILImage(frame)
        angle = (angle + ROTATION_STEP) % 360
        time.sleep(FRAME_SECONDS)

    screen.closeSerial()


if __name__ == "__main__":
    main()
