import sys
import signal
import glob
import os #remove
import time
import collections
import RPi.GPIO as GPIO
from display import Display
from util import Util
from adsb import Adsb
from tweet import Tweet

BUTTON_HOLD = 17
BUTTON_MIL = 22
#BUTTON_3 = 23 # configured for shutdown
BUTTON_QUIT = 27

LOG_DIR = 'logs'

def setupButtonHardware():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_HOLD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_MIL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_QUIT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def shutdownEvent(signal, frame):
    sys.exit(0)

def writeADSBHeader(filename):
    theFile = open(filename, "a")
    theFile.write("ICAO ID,Date,Time,Callsign,Altitude,Ground Speed,Ground Track Angle,Lat,Lon,Vertical Rate,Squawk\n")
    theFile.close()

def getDateTime(theDate, theTime):
    return theDate.replace("/","") + "-" + theTime[:8].replace(":","")

def writeADSBData(filename, adsb):
    theFile = open(filename, "a")
    dataRow = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n"
    theFile.write(dataRow.format(adsb.ICAOid, adsb.theDate, adsb.theTime, adsb.callsign, adsb.altitude,
                                 adsb.groundSpeed, adsb.track, adsb.lat, adsb.lon, adsb.verticalRate, adsb.squawk))
    theFile.close()

def writeCallsigns(filename, callsigns):
    theFile = open(filename, "w")
    for cs in callsigns:
        theFile.write(cs + "\n")
    theFile.close()

def addToRecents(callSign, que, count):
    try:
        x = list(que).index(callSign)
    except ValueError:
        que.appendleft(callSign)
        count+=1
    return que, count

def checkAndMakeDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def setupTodaysDir(theDate):
    dateParts = theDate.split("/")
    dateDir = dateParts[1] + "-" + dateParts[2] + "-" + dateParts[0]
    path = LOG_DIR + "/" + dateDir
    checkAndMakeDir(path)
    return path

def getHomeLatLon(filename):
    try:
        f = open(filename, "r")
    except:
        return 41.499741, -81.693726

    lat = float(f.readline())
    lon = float(f.readline())
    f.close()
    return lat, lon

Util.timestamp('ads-b scanner starting')

Util.timestamp('registering signals')
signal.signal(signal.SIGTERM, shutdownEvent)
signal.signal(signal.SIGINT, shutdownEvent)
signal.signal(signal.SIGTSTP, shutdownEvent)

Util.timestamp('getting lat/lon')
HOME_LAT, HOME_LON = getHomeLatLon("home-lat-lon.txt")

Util.timestamp('defining data structures')
loggedCivCallsigns = set()
loggedMilCallsigns = set()
csCivCount = 0
csMilCount = 0
recentCallsigns = collections.deque(maxlen=20)
recentCount = 0
firstRow = 1
adsbCount = 0
holdMode = False
currentCallsign = ""
currentID = ""

# Setup page options
milMode = False
tweetAllRecent = True
tweetMil = True
remoteHead = False

Util.timestamp('creating objects')
dsp = Display()
adsbObj = Adsb()
tweeter = Tweet()   # make conditional if tweets not enabled

Util.timestamp('configuring GPIO')
setupButtonHardware()

Util.timestamp('starting GUI')
# Get initial options
dsp.setupOptionsDisplay()


dsp.setupAdsbDisplay()

dsp.drawHoldButton(holdMode)
dsp.drawMilButton(milMode)
dsp.drawOffButton()
dsp.drawExitButton()

checkAndMakeDir(LOG_DIR)

for adsbdata in sys.stdin:

    if adsbObj.isValidRec(adsbdata):

        adsbObj.loadData(adsbdata)

        if (firstRow):
            logPath = setupTodaysDir(adsbObj.theDate)
            dt = getDateTime(adsbObj.theDate, adsbObj.theTime)
            csCivfn = os.path.join(logPath, "civ-callsign-" + dt + ".txt")
            csMilfn = os.path.join(logPath, "mil-callsign-" + dt + ".txt")
            adsbfn = os.path.join(logPath, "adsbdata-" + dt + ".txt")
            writeADSBHeader(adsbfn)
            firstRow = 0

        # always log ADSB data and save the current ICAO ID
        writeADSBData(adsbfn, adsbObj)
        adsbCount += 1
        dsp.updateAdsbCount(adsbCount)
        dsp.refreshDisplay()
        currentID = adsbObj.ICAOid

        # update just the recent callsign display and the logged callsigns if new
        currentCallsign = adsbObj.callsign.strip()
        if (currentCallsign != ""):

            # Mil callsign:     if not mil mode, then display, add to recents, tweet if enabled
            #                   if mil mode, then do the same
            #
            # Civ callsign:     if not mil mode, then display, add to recents, tweet if enabled
            #                   if mil mode, then discard, no tweet
            if (not milMode or (milMode and Util.isMilCallsign(currentCallsign))):
                recentCallsigns, recentCount = addToRecents(currentCallsign, recentCallsigns, recentCount)
                dsp.displayRecents(recentCallsigns)

                if (tweetAllRecent):
                    if (recentCount == 10):
                        recentCount = 0
                        msg = ""
                        for idx in range(0, 10):
                            if (idx < 9):
                                msg += recentCallsigns[idx] + "; "
                            else:
                                msg += "{0} {1}".format(recentCallsigns[idx], getDateTime(adsbObj.theDate, adsbObj.theTime))
                        tweeter.sendTweet(msg)

            # update the count of civ and mil callsigns and log to file
            if (Util.isMilCallsign(currentCallsign)):
                oldLen = len(loggedMilCallsigns)
                loggedMilCallsigns.add(currentCallsign)
                newLen = len(loggedMilCallsigns)
                if newLen > oldLen:
                    csMilCount += 1
                    writeCallsigns(csMilfn, sorted(loggedMilCallsigns))
                    if (tweetMil):
                        tweeter.sendTweet("{0} Mil {1}".format(currentCallsign,getDateTime(adsbObj.theDate, adsbObj.theTime)))
            else:
                oldLen = len(loggedCivCallsigns)
                loggedCivCallsigns.add(currentCallsign)
                newLen = len(loggedCivCallsigns)
                if newLen > oldLen:
                    csCivCount += 1
                    writeCallsigns(csCivfn, sorted(loggedCivCallsigns))

            dsp.updateCallsignCount(csCivCount, csMilCount)

        if (holdMode and (currentID == lastID)):
            dsp.clearCallsignAndID()
            dsp.clearFlightData()
            dsp.displayICAOid(lastID)
            dsp.displayCallsign(lastCallSign, Util.isMilCallsign(lastCallSign))
            dsp.displayLastSeen(adsbObj)
            dsp.displayFlightData(adsbObj, True)

            aclat = adsbObj.lat
            aclon = adsbObj.lon
            if (aclat != "" and aclon != ""):
                dist = Util.haversine(HOME_LON, HOME_LAT, float(aclon), float(aclat)) * 0.62137 # convert km to mi
                bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(aclat), float(aclon))
                dsp.displayDistance(dist, bearing)
                adsbObj.lastDist = dist
                adsbObj.lastBearing = bearing
            elif (not adsbObj.lastDist is None):
                dsp.displayDistance(adsbObj.lastDist, adsbObj.lastBearing)

        elif (not holdMode and ((not milMode and currentCallsign != "") or (milMode and Util.isMilCallsign(currentCallsign)))):
            dsp.clearCallsignAndID()
            dsp.clearFlightData()
            dsp.displayICAOid(currentID)
            dsp.displayCallsign(currentCallsign, Util.isMilCallsign(currentCallsign))
            dsp.displayLastSeen(adsbObj)
            dsp.displayFlightData(adsbObj, False)
            lastCallSign = currentCallsign
            lastID = currentID

        dsp.refreshDisplay()

        if (tweeter.tweetCount % 5 == 0):           # change if tweet and adsb count %50000; still need tweetCount?
            civCnt = "{:,}".format(csCivCount)
            milCnt = "{:,}".format(csMilCount)
            adsbCnt = "{:,}".format(adsbCount)
            cpuTemp = Util.getCPUTemp() + u'\N{DEGREE SIGN}'
            uptime = Util.getUptime()
            status = "civ:" + civCnt + " mil:" + milCnt + " adsb:" + adsbCnt + " cpu temp:" + cpuTemp + " uptime:" + uptime
            tweeter.sendTweet(status)


    if (Util.isButtonPressed(BUTTON_HOLD) and holdMode == False):
        holdMode = True
        dsp.drawHoldButton(holdMode)
        adsbObj.clearLastFlightData()
        dsp.refreshDisplay()
        time.sleep(1)
        
    if (Util.isButtonPressed(BUTTON_HOLD) and holdMode == True):
        holdMode = False
        dsp.drawHoldButton(holdMode)
        dsp.refreshDisplay()
        adsbObj.clearLastCallsignID()
        time.sleep(1)

    if (Util.isButtonPressed(BUTTON_MIL) and milMode == False):
        milMode = True
        dsp.drawMilButton(milMode)
        dsp.clearCallsignAndID()
        dsp.clearFlightData()
        dsp.refreshDisplay()
        time.sleep(1)
        
    if (Util.isButtonPressed(BUTTON_MIL) and milMode == True):
        milMode = False
        dsp.drawMilButton(milMode)
        dsp.refreshDisplay()
        time.sleep(1)
      
    if (Util.isButtonPressed(BUTTON_QUIT)):
        sys.exit(0)
