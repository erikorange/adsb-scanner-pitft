import sys
import signal
import glob
import os #remove
import time
import collections
import RPi.GPIO as GPIO
from display import Display
from remote import Remote
from util import Util
from adsb import Adsb
from tweet import Tweet
from filemgr import FileMgr

BUTTON_HOLD = 17
BUTTON_MIL = 22
#BUTTON_3 = 23 # configured for shutdown
BUTTON_QUIT = 27

LOG_DIR = 'logs'
STATS_INTERVAL = 250000

def setupButtonHardware():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_HOLD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_MIL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_QUIT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def shutdownEvent(signal, frame):
    sys.exit(0)

def writeADSBHeader(fileMgr):
    header="ICAO ID,Date,Time,Callsign,Altitude,Ground Speed,Ground Track Angle,Lat,Lon,Vertical Rate,Squawk"
    fileMgr.writeToFile(header)

def getDateTime(theDate, theTime):
    return theDate.replace("/","") + "-" + theTime[:8].replace(":","")

def writeADSBData(fileMgr, adsb):
    dataRow = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}"
    record=dataRow.format(adsb.ICAOid, adsb.theDate, adsb.theTime, adsb.callsign, adsb.altitude,
                                 adsb.groundSpeed, adsb.track, adsb.lat, adsb.lon, adsb.verticalRate, adsb.squawk)
    fileMgr.writeToFile(record)

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



Util.timestamp('ads-b scanner starting')

Util.timestamp('registering signals')
signal.signal(signal.SIGTERM, shutdownEvent)
signal.signal(signal.SIGINT, shutdownEvent)
signal.signal(signal.SIGTSTP, shutdownEvent)

Util.timestamp('getting lat/lon')
HOME_LAT, HOME_LON = Util.getHomeLatLon("home-lat-lon.txt")

Util.timestamp('defining data structures')
loggedCivCallsigns = set()
loggedMilCallsigns = set()
csCivCount = 0
csMilCount = 0
recentCallsigns = collections.deque(maxlen=20)
recentCount = 0
firstRow = True
adsbCount = 0
holdMode = False
currentCallsign = ""
currentID = ""
topDist=0
topDistID=""

Util.timestamp('creating objects')
dsp = Display()
adsbObj = Adsb()
fileMgr = FileMgr()

Util.timestamp('configuring GPIO')
setupButtonHardware()

Util.timestamp('starting GUI')
milMode, tweetMil, tweetLast10CivMil, remoteHead, milTestMode = dsp.setupOptionsDisplay()    # Get initial options
if (tweetMil or tweetLast10CivMil):
    tweeter = Tweet()


dsp.setupAdsbDisplay()
dsp.showOpeningMessage()
dsp.drawHoldButton(holdMode)
dsp.drawMilButton(milMode)
dsp.drawOffButton()
dsp.drawExitButton()

rh = Remote()
if (remoteHead):
    Util.timestamp('starting remote thread')
    dsp.displayRemoteLogo()
    rh.startRemote()

if (tweetMil or tweetLast10CivMil):
    dsp.displayTwitterLogo()

checkAndMakeDir(LOG_DIR)

if (milTestMode):
    milTestList=('VADER07', 'STING42', 'POLO57', 'STEEL98', 'BISON22', 'RULE71', 'JEEP31', 'RCH285', 'SLAM90', 'FLASH29')
    milTestIdx=0

for adsbdata in sys.stdin:

    if adsbObj.isValidRec(adsbdata):

        if (remoteHead):
            rh.addToQueue(adsbdata)

        adsbObj.loadData(adsbdata)

        if (firstRow):
            logPath = setupTodaysDir(adsbObj.theDate)
            dt = getDateTime(adsbObj.theDate, adsbObj.theTime)
            csCivfn = os.path.join(logPath, "civ-callsign-" + dt + ".txt")
            csMilfn = os.path.join(logPath, "mil-callsign-" + dt + ".txt")
            adsbfn = os.path.join(logPath, "adsbdata-" + dt + ".txt")
            fileMgr.createFile(adsbfn)
            writeADSBHeader(fileMgr)
            firstRow = False

        # always log ADSB data and save the current ICAO ID
        writeADSBData(fileMgr, adsbObj)
        adsbCount += 1
        dsp.updateAdsbCount(adsbCount)
        currentID = adsbObj.ICAOid

        # update just the recent callsign display and the logged callsigns if new
        currentCallsign = adsbObj.callsign.strip()

        if (milTestMode):
            if (adsbCount % 500 == 0):
                currentCallsign = milTestList[milTestIdx]
                milTestIdx+=1
                if (milTestIdx == len(milTestList)):
                    milTestIdx=0


        if (currentCallsign != ""):

            # Mil callsign:     if not mil mode, then display, add to recents, tweet if enabled
            #                   if mil mode, then do the same
            #
            # Civ callsign:     if not mil mode, then display, add to recents, tweet if enabled
            #                   if mil mode, then discard, no tweet
            if (not milMode or (milMode and Util.isMilCallsign(currentCallsign))):
                recentCallsigns, recentCount = addToRecents(currentCallsign, recentCallsigns, recentCount)
                dsp.displayRecents(recentCallsigns)

                if (tweetLast10CivMil):
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
                    if (not milTestMode):
                        writeCallsigns(csMilfn, sorted(loggedMilCallsigns))
                        
                    if (tweetMil):
                        if (not milTestMode):
                            tweeter.sendTweet("{0} {1} {2}".format(currentCallsign, currentID, getDateTime(adsbObj.theDate, adsbObj.theTime)))
                        else:
                            tweeter.sendTweet("TEST {0} {1} {2}".format(currentCallsign, currentID, getDateTime(adsbObj.theDate, adsbObj.theTime)))

            else:
                oldLen = len(loggedCivCallsigns)
                loggedCivCallsigns.add(currentCallsign)
                newLen = len(loggedCivCallsigns)
                if newLen > oldLen:
                    csCivCount += 1
                    writeCallsigns(csCivfn, sorted(loggedCivCallsigns))

            dsp.updateCallsignCount(csCivCount, csMilCount)

        gotLatLon = False
        if (adsbObj.lat != "" and adsbObj.lon != ""):
            gotLatLon = True
            dist = Util.haversine(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
            bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
            if (dist > topDist):
                topDist = dist   
                topDistID = currentID

        if (holdMode and (currentID == lastID)):
            dsp.clearCallsignAndID()
            dsp.clearFlightData()
            dsp.displayICAOid(lastID)
            dsp.displayCallsign(lastCallSign, Util.isMilCallsign(lastCallSign))
            dsp.displayLastSeen(adsbObj)
            dsp.displayFlightData(adsbObj, True)

            if (gotLatLon):
                dsp.displayDistance(dist, bearing)
                adsbObj.lastDist, adsbObj.lastBearing = (dist, bearing)
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


        if ((adsbCount % STATS_INTERVAL == 0) and (tweetLast10CivMil or tweetMil)):
            civCnt = "{:,}".format(csCivCount)
            milCnt = "{:,}".format(csMilCount)
            adsbCnt = "{:,}".format(adsbCount)
            cpuTemp = Util.getCPUTemp() + u'\N{DEGREE SIGN}'
            uptime = Util.getUptime()
            status = "civ:{0} mil:{1} adsb:{2}\n dist:{3:0.1f} {4} cpu:{5}\n{6}".format(
                civCnt, milCnt, adsbCnt, topDist, topDistID, cpuTemp, uptime)
            tweeter.sendTweet(status)

    if (Util.isButtonPressed(BUTTON_HOLD)):
        if (holdMode):
            holdMode = False
            adsbObj.clearLastCallsignID()
        else:
            holdMode = True
            adsbObj.clearLastFlightData()
            
        dsp.drawHoldButton(holdMode)
        dsp.refreshDisplay()
        time.sleep(1)
        
    if (Util.isButtonPressed(BUTTON_MIL)):
        if (milMode):
            milMode = False
        else:
            milMode = True
            dsp.clearCallsignAndID()
            dsp.clearFlightData()
            
        dsp.drawMilButton(milMode)
        dsp.refreshDisplay()
        time.sleep(1)
        
    if (Util.isButtonPressed(BUTTON_QUIT)):
        fileMgr.closeFile()
        sys.exit(0)

print("Exiting main loop")