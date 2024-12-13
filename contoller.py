# Program to control passerelle between Android application
# and micro-controller through USB tty
import time
import argparse
import signal
import sys
import socket
import socketserver
import serial
import threading

FILENAME        = "values.txt"
LAST_VALUE      = ""

# send serial message 
SERIALPORT = "/dev/ttyACM0"
BAUDRATE = 115200
ser = serial.Serial()

def initUART():        
        # ser = serial.Serial(SERIALPORT, BAUDRATE)
        ser.port=SERIALPORT
        ser.baudrate=BAUDRATE
        ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        ser.parity = serial.PARITY_NONE #set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        ser.timeout = None          #block read

        # ser.timeout = 0             #non-block read
        # ser.timeout = 2              #timeout block read
        ser.xonxoff = False     #disable software flow control
        ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        #ser.writeTimeout = 0     #timeout for write
        print('Starting Up Serial Monitor')
        try:
                ser.open()
        except serial.SerialException:
                print("Serial {} port not available".format(SERIALPORT))
                exit()



def sendUARTMessage(msg):
    ser.write(msg)
    print("Message <" + msg + "> sent to micro-controller." )


# Main program logic follows:
if __name__ == '__main__':
        initUART()
        f= open(FILENAME,"a")
        print ('Press Ctrl-C to quit.')

        try:
                # while ser.isOpen() :
                        for i in range(5600):
                                ser.write(("data"+str(i)+"\n").encode())
                                by = b'0'
                                data_str = b""
                                while by != b'\n':
                                    by = ser.read(1)
                                    data_str+=by
                                print(data_str.decode("utf-8"),"")
                        # ser.write("pouet\n".encode())
                        # by = b'0'
                        # data_str = b""
                        # while by != b'\n':
                        #     by = ser.read(1)
                        #     data_str+=by
                        # print(data_str.decode("utf-8"),"")
        except (KeyboardInterrupt, SystemExit):
                f.close()
                ser.close()
                exit()

