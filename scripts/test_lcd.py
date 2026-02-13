#!/usr/bin/env python3
"""
Test script for SPI TFT LCD on Raspberry Pi (ILI9341 or GC9A01A).

Run on the device: python scripts/test_lcd.py

Use DISPLAY_TYPE=gc9a01a for the Adafruit 1.28" 240x240 Round TFT (GC9A01A, EYESPI).
Default is ili9341 (320x240).

Cycles solid colors then draws a simple pattern.
"""
import os
import sys
import time

sys.path.insert(0, ".")


def rgb_to_565(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def main():
    try:
        import board
        import busio
        from digitalio import DigitalInOut
    except ImportError:
        print("This script must run on a Raspberry Pi with adafruit_rgb_display installed.")
        print("Install: pip install adafruit-circuitpython-rgb-display adafruit-blinka spidev")
        sys.exit(1)

    cs = DigitalInOut(board.D22)
    dc = DigitalInOut(board.D17)
    rst = DigitalInOut(board.D27)
    spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)

    display_type = (os.environ.get("DISPLAY_TYPE") or "ili9341").strip().lower()
    rotation = int(os.environ.get("LCD_ROTATION", "0"))
    if rotation not in (0, 90, 180, 270):
        rotation = 0

    if display_type == "gc9a01a":
        from adafruit_rgb_display import gc9a01a
        W, H = 240, 240
        print("Initializing GC9A01A 240x240 round (rotation={})...".format(rotation))
        display = gc9a01a.GC9A01A(
            spi, dc=dc, cs=cs, rst=rst, width=W, height=H, rotation=rotation
        )
    else:
        from adafruit_rgb_display import ili9341
        W, H = 320, 240
        print("Initializing ILI9341 320x240 (rotation={})...".format(rotation))
        display = ili9341.ILI9341(
            spi, cs=cs, dc=dc, rst=rst, width=W, height=H, rotation=rotation
        )
    colors = [
        ("Red",   rgb_to_565(255, 0, 0)),
        ("Green", rgb_to_565(0, 255, 0)),
        ("Blue",  rgb_to_565(0, 0, 255)),
        ("White", rgb_to_565(255, 255, 255)),
        ("Black", rgb_to_565(0, 0, 0)),
    ]
    for name, color in colors:
        print("Fill {}...".format(name))
        display.fill(color)
        time.sleep(1.5)

    # Draw a white rectangle in the center (verify coordinates)
    print("Drawing center rectangle...")
    display.fill(rgb_to_565(0, 0, 0))
    cx, cy = W // 2, H // 2
    hw, hh = 40, 30
    for dy in range(-hh, hh + 1):
        for dx in range(-hw, hw + 1):
            x, y = cx + dx, cy + dy
            if 0 <= x < W and 0 <= y < H:
                display.pixel(x, y, rgb_to_565(255, 255, 255))
    time.sleep(2)

    # Border (full frame)
    print("Drawing border...")
    display.fill(rgb_to_565(0, 0, 0))
    border_color = rgb_to_565(0, 255, 255)
    for x in range(W):
        display.pixel(x, 0, border_color)
        display.pixel(x, H - 1, border_color)
    for y in range(H):
        display.pixel(0, y, border_color)
        display.pixel(W - 1, y, border_color)
    time.sleep(2)

    display.fill(rgb_to_565(0, 0, 0))
    print("Done. If you saw nothing or wrong colors:")
    print("  - Check wiring (CS=GPIO22, DC=GPIO17, RST=GPIO27, SCK=23, MOSI=19).")
    print("  - For 1.28\" round display: DISPLAY_TYPE=gc9a01a python scripts/test_lcd.py")
    print("  - Try: LCD_ROTATION=180 python scripts/test_lcd.py")
    print("  - Some boards use BGR; we use RGB.")


if __name__ == "__main__":
    main()
