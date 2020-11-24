class Adsb():

    def __init__(self):
        self.clearLastCallsignID()
        self.clearLastFlightData()

    def clearLastCallsignID(self):
        self.lastCallSign = ""
        self.lastID = ""

    def clearLastFlightData(self):
        self.lastDist = None
        self.lastBearing = ""
        self.lastLat = ""
        self.lastLon = ""
        self.lastAltitude = ""
        self.lastVerticalRate = ""
        self.lastGroundSpeed = ""
        self.lastSquawk = ""

    def isValidRec(self, rec):
        if rec.count(',') == 21:
            return 1
        return 0

    def loadData(self, rec):
        dataVals = rec.split(",")
        self.ICAOid = dataVals[4]
        self.theDate = dataVals[6]
        self.theTime = dataVals[7]
        self.callsign = dataVals[10]
        self.altitude = dataVals[11]
        self.groundSpeed = dataVals[12]
        self.track = dataVals[13]
        self.lat = dataVals[14]
        self.lon = dataVals[15]
        self.verticalRate = dataVals[16]
        self.squawk = dataVals[17]

    def loadNewCsId(self, adsbRec, adsbCallsign, adsbID):
        dataVals = adsbRec.split(",")
        dataVals[4] = adsbID
        dataVals[10] = adsbCallsign
        return ",".join(dataVals)
        