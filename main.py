import time
from rotary_irq_rp2 import RotaryIRQ
import os
os.chdir("/")
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

r = RotaryIRQ(
    pin_num_clk=0,
    pin_num_dt=16,
    min_val=0,
    max_val=1000000-1,
    reverse=False,
    incr=100,
    range_mode=RotaryIRQ.RANGE_WRAP,
    pull_up=True,
    half_step=False,
)
delay_file = "delay.txt"
with open(delay_file, "r") as f:
    r.set(value=int(f.readline()))

WIDTH =128
HEIGHT= 64
i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def display(number, order_of_mag=-1):
    oled.fill(0)
    num_pos = WIDTH//2 - len(number)*8//2
    oled.text(number, num_pos, HEIGHT//2 - 8//2)
    shift_chars = (order_of_mag < 0) - order_of_mag
    oled.text("^", num_pos + shift_chars * 8, HEIGHT // 2 + 8//2)
    oled.show()

in_p = Pin(9, mode=Pin.IN)
out_p = Pin(10, mode=Pin.OUT)

def display_time():
    print(r.value())
    display(f"{r.value()/1000:.1f} ms")
    with open(delay_file, "w") as f:
        f.write(str(r.value()))

r.add_listener(display_time)
display_time()

pulse_length = 200
while True:
    # wait for the next rising edge
    while not in_p.value():
        pass
    deadline = time.ticks_add(time.ticks_us(), r.value())
    while time.ticks_diff(deadline, time.ticks_us()) > 0:
        pass
    out_p.value(1)
    deadline = time.ticks_add(time.ticks_us(), pulse_length)
    while time.ticks_diff(deadline, time.ticks_us()) > 0:
        pass
    out_p.value(0)
    while in_p.value():
        pass
