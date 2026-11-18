from machine import I2C, Pin
from pack.led_display import OLED
from pack.vent import set_fan_rpm
from bme280 import BME280
from machine import Timer

timer_event = False
lOn = False
Tset = 25
last_state = 0

def timer_handler(timer):
    global timer_event

    timer_event = True

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
        oled.text("{:.1f} / {:.1f} C".format(temperature,Tset), 22, 0)
        oled.text("H:", 4, 15)
        oled.text("{:.1f} %".format(humidity), 22, 15)
        oled.text("P:", 4, 30)
        oled.text("{:.1f} Pa".format(pressure), 22, 30)
        oled.show()

    def vent(e):
        x = max(0, min(1, e / 5))
        return x * x * (3 - 2 * x)

    def encoder_callback(pin):
        global Tset, last_state
        
        current = clk.value()

        if current != last_state:
            if dt.value() != current:
                Tset += 1
            else:
                Tset -= 1
            refreshDisplay(temperature,humidity,pressure)
            last_state = current

    clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
        handler=encoder_callback)

    while True:
        if timer_event:
            timer_event = False
            temperature, humidity, pressure, _ = sensor.read_values()
            refreshDisplay(temperature,humidity,pressure)
            set_fan_rpm(19,vent(temperature-Tset))

if __name__ == "__main__":
    main()