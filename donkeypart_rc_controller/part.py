import serial
from time import sleep
from datetime import datetime


class Arduino:
    import threading

    arduino_device = None
    arduino_lock = threading.Lock()

    def __init__(self, pwmPort, frequency=60):
        self.frequency = frequency

        if Arduino.arduino_device is None:
            Arduino.arduino_device = serial.Serial(pwmPort, 9600, timeout=0.01)
        print("Arduino initialized")

    def readLine(self):
        ret = None
        with Arduino.arduino_lock:
            if Arduino.arduino_device.inWaiting() > 0:
                ret = Arduino.arduino_device.readline()

        if ret is not None:
            ret = ret.rstrip()
        return ret


class RcController:

    def __init__(self, hz=20):
        self.inSteering = 0.0
        self.inThrottle = 0.0

        self.sensor = Arduino(0)

        self.num_channels = 2
        print("Initialized Serial Port")
        self.running = True
        self.hz = hz
        self.sleep_time = 1000/float(self.hz) / 1000.0
        print("Sleep Time " + str(self.sleep_time))


    def getLatestStatus(self):
        ''' This clears the buffer and returns only the last value
            This is faster than polling the arduino for the latest value
        '''
        status = self.sensor.readLine()
        if status is None:
            return ['0' for x in range(self.num_channels)]

        decoded = status.strip().decode("utf-8")
        if  not decoded.startswith('B') and len(decoded.strip()) == 0:
            vel_angle_raw = ['0' for x in range(self.num_channels)]
            return vel_angle_raw

        # return it as an array
        # raw format = b'B 1234 1234\r\n' from the Arduino
        try:
            vel_angle_raw = status.strip().decode("utf-8").split(" ")
        except Exception:
            # unable to decode the values from the Arduino. Typically happens
            # at startup when the serial connection is being started and lasts
            # a few cycles. Junk in the trunk..
            vel_angle_raw = ['0' for x in range(self.num_channels)]
        return vel_angle_raw



    def update(self):
        """ Start the threa for reading the arduino """
        print("Start Update Thread")
        while self.running:
            start = datetime.now()

            p = self.getLatestStatus()
            if len(p) != 2:
                i = float(p[1])
                k = float(p[2])

                self.inSteering = i * 1.0 / 100.0
                self.inThrottle = k * 1.0 / 100.0

                #print("matched %.2f  %.2f  %.2f  %.2f" % (i, (self.inSteering), k, (self.inThrottle)))
            stop = datetime.now()
            s = 0.01 - (stop - start).total_seconds()
            if s > 0:
                sleep(s)

    def run_threaded(self):
        return self.inSteering, self.inThrottle

    def shutdown(self):
        self.running = False
        print("Stopping rc parsing thread")
        sleep(.5)


if __name__ == "__main__":
    '''
    publish rc controller
    '''
    p = RcController()
    p.update()
