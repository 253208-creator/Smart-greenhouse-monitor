from machine import I2C, Pin
import time
from bme280 import BME280
import framebuf
from machine import Timer

timer_event = False

def timer_handler(timer):
    global timer_event

    timer_event = True


class OLED:
    def __init__(self, width, height, i2c, address):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.address = address
        self.offset = 2

        self.buffer = bytearray(width * height // 8)

        self.fb = framebuf.FrameBuffer(
            self.buffer,
            width,
            height,
            framebuf.MONO_VLSB
        )

        self.init_display()

    def command(self, cmd):
        self.i2c.writeto(
            self.address,
            bytes([0x00, cmd])
        )

    def init_display(self):
        time.sleep_ms(100)

        commands = [
            0xAE,       # Display OFF
            0xD5, 0x80, # Clock
            0xA8, 0x3F, # Multiplex ratio
            0xD3, 0x00, # Display offset
            0x40,       # Start line
            0xAD, 0x8B, # DC-DC control
            0xA1,       # Segment remap
            0xC8,       # COM scan direction
            0xDA, 0x12, # COM pins
            0x81, 0xCF, # Contrast
            0xD9, 0xF1, # Precharge
            0xDB, 0x40, # VCOM
            0xA4,       # Display follows RAM
            0xA6,       # Normal display
            0xAF        # Display ON
        ]

        for cmd in commands:
            self.command(cmd)

        self.fill(0)
        self.show()

    def show(self):
        for page in range(8):
            self.command(0xB0 + page)
            self.command(0x02)
            self.command(0x10)

            start = page * 128
            data = self.buffer[start:start + 128]

            self.i2c.writeto(
                self.address,
                b'\x40' + data
            )

    def fill(self, color):
        self.fb.fill(color)

    def text(self, string, x, y, color=1):
        self.fb.text(string, x, y, color)

    def pixel(self, x, y, color=1):
        self.fb.pixel(x, y, color)

    def line(self, x1, y1, x2, y2, color=1):
        self.fb.line(x1, y1, x2, y2, color)

    def rect(self, x, y, w, h, color=1):
        self.fb.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color=1):
        self.fb.fill_rect(x, y, w, h, color)

    def hline(self, x, y, w, color=1):
        self.fb.hline(x, y, w, color)

    def vline(self, x, y, h, color=1):
        self.fb.vline(x, y, h, color)






#SETUP



def main():
    global timer_event
    timer = Timer(-1)
    WIDTH = 128
    HEIGHT = 64
    ADDRESS = 0x3C

    clk = Pin(17, Pin.IN, Pin.PULL_UP)
    dt = Pin(18, Pin.IN, Pin.PULL_UP)
    global last_state
    last_state = clk.value()

    Tset = 25

    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
    sensor = BME280(i2c)

    devices = i2c.scan()
    if ADDRESS not in devices:
        if 0x3D in devices:
            ADDRESS = 0x3D
        else:
            raise Exception("OLED not found! Check wiring.")

    oled = OLED(WIDTH, HEIGHT, i2c, ADDRESS)

    oled.fill(0)

    timer.init(
            period=500,
            mode=Timer.PERIODIC,
            callback=timer_handler,
        )

    def refreshDisplay(temperature, humidity, pressure):
        oled.fill(0)
        oled.text("T:", 4, 0)
        oled.text("{:.1f} C".format(temperature), 22, 0)
        oled.text("H:", 4, 15)
        oled.text("{:.1f} %".format(humidity), 22, 15)
        oled.text("P:", 4, 30)
        oled.text("{:.1f} Pa".format(pressure), 22, 30)
        oled.show()

    def encoder_callback(pin):
        global Tset, last_state

        current = clk.value()

        if current != last_state:
            if dt.value() != current:
                Tset += 1
            else:
                Tset -= 1

            last_state = current

    clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
        handler=encoder_callback)

    while True:

        temperature, humidity, pressure, _ = sensor.read_values()
        print(Tset)


    
        if timer_event:
            timer_event = False
            refreshDisplay(temperature,humidity,pressure)



if __name__ == "__main__":
    main()