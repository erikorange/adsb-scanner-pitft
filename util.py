import re
import os
from math import degrees, radians, cos, sin, asin, sqrt, atan2
import RPi.GPIO as GPIO
from datetime import datetime

class Util:

    @staticmethod
    def timestamp(txt):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + txt)

    @staticmethod
    def isButtonPressed(button):
        if not(GPIO.input(button)):
            return 1
        else:
            return 0

    @staticmethod
    def getCPUTemp():
        res = os.popen('vcgencmd measure_temp').readline()
        tempC = float(res.replace("temp=","").replace("'C\n",""))
        tempF = (tempC * (9/5)) + 32
        return "{0:0.2f}".format(tempF)
    
    @staticmethod
    def getUptime():
        ut = os.popen('uptime -p').readline()
        return ut.replace("\n","")
    
    @staticmethod
    def shutdownSystem():
        sd = os.popen('sudo shutdown -h now').readline()
        return

    @staticmethod
    def isMilCallsign(cs):
    # starts with at least 4 letters, then at least 2 numbers; or starts with RCH or TOPCAT; or is GOTOFMS.  Remove spaces for VADER xx
        match = re.search(r'(^[A-Z]{4,}[0-9]{2,}$)|(^RCH)|(^TOPCAT)|(GOTOFMS)', cs.replace(' ',''))
        if match:
            return 1
        else:
            return 0

    @staticmethod
    def getHomeLatLon(filename):
        try:
            f = open(filename, "r")
        except:
            return 41.499741, -81.693726

        lat = float(f.readline())
        lon = float(f.readline())
        f.close()
        return lat, lon

    @staticmethod
    def haversine(homeLat, homeLon, aircraftLat, aircraftLon):
        # convert decimal degrees to radians 
        homeLon, homeLat, aircraftLon, aircraftLat = map(radians, [homeLon, homeLat, aircraftLon, aircraftLat])

        # haversine formula 
        dlon = aircraftLon - homeLon 
        dlat = aircraftLat - homeLat
        a = sin(dlat/2)**2 + cos(homeLat) * cos(aircraftLat) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers is 6371.
        return c * r * 0.62137 # convert km to mi

    @staticmethod
    def calculateBearing(homeLat, homeLon, aircraftLat, aircraftLon):
        homeLat = radians(homeLat)
        aircraftLat = radians(aircraftLat)
        diffLong = radians(aircraftLon - homeLon)
        x = sin(diffLong) * cos(aircraftLat)
        y = cos(homeLat) * sin(aircraftLat) - (sin(homeLat) * cos(aircraftLat) * cos(diffLong))
        initial_bearing = atan2(x, y)
        initial_bearing = degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing

    @staticmethod
    def getCompassDir(bearing):
        tmp = round(bearing / 22.5)
        if (tmp == 1):
            return "NNE"
        elif (tmp == 2):
            return "NE"
        elif (tmp == 3):
            return "ENE"
        elif (tmp == 4):
            return "E"
        elif (tmp == 5):
            return "ESE"
        elif (tmp == 6):
            return "SE"
        elif (tmp == 7):
            return "SSE"
        elif (tmp == 8):
            return "S"
        elif (tmp == 9):
            return "SSW"
        elif (tmp == 10):
            return "SW"
        elif (tmp == 11):
            return "WSW"
        elif (tmp == 12):
            return "W"
        elif (tmp == 13):
            return "WNW"
        elif (tmp == 14):
            return "NW"
        elif (tmp == 15):
            return "NNW"
        else:
            return "N"