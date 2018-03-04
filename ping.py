import RPi.GPIO as GPIO
import time
from pythonosc import osc_message_builder
from pythonosc import udp_client



GPIO.setmode(GPIO.BCM)

class DistanceSensor:
    def __init__(self, trig_pin, echo_pin):
        self.TRIG = trig_pin
        self.ECHO = echo_pin
        GPIO.setup(self.TRIG,GPIO.OUT)
        GPIO.setup(self.ECHO,GPIO.IN)
        GPIO.output(self.TRIG,False)

    def trig(self):
        GPIO.output(self.TRIG,True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG,False)

    def ping(self):
        self.trig()
        echo_wait_init = time.time()
        while GPIO.input(self.ECHO)==0:
            pulse_start=time.time()
            if (pulse_start > echo_wait_init + 0.01):
                print("RETRY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                return self.ping()
        while GPIO.input(self.ECHO)==1:
            pulse_end=time.time()
        return pulse_end-pulse_start

dist = DistanceSensor(23, 24)
dist2 = DistanceSensor(27, 22)

sender = udp_client.SimpleUDPClient('127.0.0.1', 4559)

time.sleep(2)

but = 17
GPIO.setup(but, GPIO.IN)

def dist_to_pitch(d):
    low = 0.002
    high = 0.005
    too_high = 0.007
    if d > too_high:
        return None
    if d < low:
        d = low
    elif d > high:
        d = high
    pitch_coefficient = (d - low) / (high - low)
    low_pitch = 60
    high_pitch = 72
    pitch = high_pitch - (high_pitch - low_pitch) * pitch_coefficient
    return round(pitch)

while True:
    time.sleep(0.01)
    d1 = dist.ping()
    d2 = dist2.ping()
    print("d1:", d1, "\td2:", d2, "\tbut:", GPIO.input(but))
    d = (d1 + d2) / 2
    p = dist_to_pitch(d)
    print("p:", p)
    if p != None:
        sender.send_message('/a', p)
