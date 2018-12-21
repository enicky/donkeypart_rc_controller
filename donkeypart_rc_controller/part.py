import serial
from time import sleep


class RcController:

    def __init__(self, hz=20):
        dev = '/dev/ttyACM0' #arduino

        self.ser = serial.Serial(dev, 57600)
        print("Initialized Serial Port")
        self.running = True
        self.hz = hz
        self.sleep_time = 1000/float(self.hz) / 1000.0


    def getLatestStatus(self):
        ''' This clears the buffer and returns only the last value
            This is faster than polling the arduino for the latest value
        '''
        status = b''
        while self.ser.inWaiting() > 0:
            # read and discard any values except the most recent.
            # when Arduino Hz = 2x python Hz this results in 1 to 2
            # discarded results
            status = self.ser.readline()

        # return it as an array
        # raw format = b'1234 1234\r\n' from the Arduino
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
        while self.running:
            vel_angle_raw = self.getLatestStatus()

            if(len(vel_angle_raw) == 2):
                print(list(map(int, vel_angle_raw)))

            sleep(self.sleep_time)

    def run(self):
        print("run")

    def shutdown(self):
        self.running = False
        print("Stopping rc parsing thread")
        sleep(.5)
        self.ser.close()
