from machine import I2C, Pin
import time
from pack.led_display import OLED
from pack.vent import set_fan_rpm
from pack.wifi import WiFiThingSpeak
from bme280 import BME280
from machine import Timer
from pack.rgb_led import RGBLed


timer_event = False
lOn = False
Tset = 25
last_state = 0
last_time = 0

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
    API_URL = "https://api.thingspeak.com/update"

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
    wMod = WiFiThingSpeak(API_URL)
    rgb = RGBLed(2,3,12)


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
        oled.text("F:", 4, 45)
        oled.text(b2s(temperature > Tset), 22, 45)
        oled.show()

    def b2s(bool):
        if (bool):
            return "ON"
        else:
            return "OFF"

    def vent(e):
        x = max(0, min(1, e / 5))
        return x * x * (3 - 2 * x)

    def encoder_callback(pin):
        global Tset, last_state, last_time
        last_time = time.ticks_ms()
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
        if (last_time + 1000 > time.ticks_ms()):
            continue
        if timer_event:
            timer_event = False
            temperature, humidity, pressure, _ = sensor.read_values()
            refreshDisplay(temperature,humidity,pressure)
            wMod.send(temperature,humidity,pressure)
            set_fan_rpm(19,vent(temperature-Tset))
            rgb.update_ventilation_status(temperature > Tset)

if __name__ == "__main__":
    main()