import time
import board
import neopixel
import touchio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

pixel_pin = board.NEOPIXEL
num_pixels = 4

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.05, auto_write=False)

pixels_top = [pixels[0], pixels[1]]
pixels_bottom = [pixels[2], pixels[3]]

usb_left = True
usb_right = False
if usb_left:
    top_touch = touchio.TouchIn(board.TOUCH1)
    bot_touch = touchio.TouchIn(board.TOUCH2)
if usb_right:
    top_touch = touchio.TouchIn(board.TOUCH2)
    bot_touch = touchio.TouchIn(board.TOUCH1)
    
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)
alt_key = Keycode.ALT


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)


RED = (255, 0, 0)
GREEN = (0, 255, 0)

bot_pressed = False
top_pressed = False
mic_mute = True
vid_mute = True
clock = time.monotonic()
escape = False
escape_1 = False
escape_2 = False

while True:

    if not top_touch.value and top_pressed:
        top_pressed = False
    if not bot_touch.value and bot_pressed:
        bot_pressed = False
    if mic_mute:
        pixels[2] = RED
        pixels[3] = RED
        pixels.show()
    if vid_mute:
        pixels[0] = RED
        pixels[1] = RED
        pixels.show()
    if not mic_mute:
        pixels[2] = GREEN
        pixels[3] = GREEN
        pixels.show()
    if not vid_mute:
        pixels[0] = GREEN
        pixels[1] = GREEN
        pixels.show()
    if escape:
        rainbow_cycle(0)
        escape = False
        escape_1 = False
        escape_2 = False

    if (top_touch.value and not top_pressed):
        top_pressed = True
        clock = time.monotonic()
        time.sleep(0.12)
        if top_touch.value and top_pressed:
            print("escape top")
            escape_1 = True
        else:
            if mic_mute:
                print("top")
                mic_mute = False
                escape_1 = False
            elif not mic_mute:
                print("top")
                mic_mute = True
                escape_1 = False
            keyboard.send(alt_key, Keycode.A)
    if (bot_touch.value and not bot_pressed):
        bot_pressed = True
        clock = time.monotonic()
        time.sleep(0.12)
        if bot_touch.value and bot_pressed:
            print("escape bot")
            escape_2 = True
        else:
            if vid_mute:
                print("bot")
                vid_mute = False
                escape_2 = False
            elif not vid_mute:
                print("bot")
                vid_mute = True
                escape_2 = False
            keyboard.send(alt_key, Keycode.V)
    if ((clock + 2) < time.monotonic()) and (escape_1 and escape_2):
        print("escape")
        escape = True
        keyboard.send(alt_key, Keycode.Q)
        time.sleep(0.1)
        keyboard.send(Keycode.ENTER)
