from machine import Pin, PWM
import time

def set_fan_rpm(pin_num, rpm, freq=200, kickstart_time=0.3, _fans={}):
    rpm = max(0.0, min(1.0, float(rpm)))

    if pin_num not in _fans:
        pwm = PWM(Pin(pin_num))
        pwm.freq(freq)
        _fans[pin_num] = {"pwm": pwm, "rpm": 0.0}

    fan = _fans[pin_num]
    pwm = fan["pwm"]

    # kickstart pulse
    if fan["rpm"] == 0.0 and 0.0 < rpm < 0.7:
        pwm.duty_u16(65535)
        time.sleep(kickstart_time)

    pwm.duty_u16(int(rpm * 65535))
    fan["rpm"] = rpm