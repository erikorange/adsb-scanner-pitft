import pygame
from pygame.locals import *
import os
from util import Util
import time
import datetime

class Display():

    def __init__(self):
        self.__displayWidth = 320
        self.__screenWidth = 290
        self.__screenHeight = 240

        self.__initDisplay()
        self.__initFonts()
        self.__initColors()
    
    def __initDisplay(self):
        os.putenv('SDL_FBDEV', '/dev/fb1')
        pygame.init()
        pygame.mouse.set_visible(False)
        flags = FULLSCREEN | DOUBLEBUF | HWSURFACE
        self.__lcd = pygame.display.set_mode((self.__displayWidth, self.__screenHeight), flags)
        self.__lcd.set_alpha(None)

    def __initFonts(self):
        fontDir="/usr/share/fonts/truetype/freefont/"
        self.__idFont = pygame.font.Font(fontDir + "FreeMono.ttf", 23) # ICAO ID
        self.__csFont = pygame.font.Font(fontDir + "FreeSans.ttf", 40) # callsign
        self.__fltFont = pygame.font.Font(fontDir + "FreeMono.ttf", 18) # flight data
        self.__lastSeenFont = pygame.font.Font(fontDir + "FreeSans.ttf", 16) # time last seen
        self.__distFont = pygame.font.Font(fontDir + "FreeSans.ttf", 14) # distance and bearing
        self.__btnFont = pygame.font.Font(fontDir + "FreeSans.ttf", 13)
        self.__recentFont= pygame.font.Font(fontDir + "FreeSans.ttf", 12)
        self.__statsFont= pygame.font.Font(fontDir + "FreeSans.ttf", 14)
        self.__optsFont = pygame.font.Font(fontDir + "FreeSans.ttf", 17)
        self.__titleFont= pygame.font.Font(fontDir + "FreeSans.ttf", 18)


    def __initColors(self):
        self.__green = (0,255,0)
        self.__black = (0,0,0)
        self.__yellow = (255,255,0)
        self.__mediumBlue = (100,149,237)
        self.__brighterBlue = (0,128,255)
        self.__cyan = (0,255,255)
        self.__darkRed = (64,0,0)
        self.__medRed = (128,0,0)
        self.__darkPurple=(64,0,64)
        self.__medPurple=(128,0,128)
        self.__medOrange=(255,129,0)
        self.__darkOrange=(128,60,0)
        self.__white = (255,255,255)
        self.__gray = (128,128,128)
        self.__red = (255,0,0)
        self.__orange = (255,215,0)
        self.__purple = (255,0,255)

    def setupAdsbDisplay(self):
        self.__lcd.fill(self.__black)
        pygame.draw.rect(self.__lcd, self.__green, (0,0,self.__screenWidth, self.__screenHeight), 1) # screen border
        pygame.draw.lines(self.__lcd, self.__green, False, [(0,95), (self.__screenWidth-1,95)], 1) # midline
        pygame.draw.lines(self.__lcd, self.__green, False, [(148,96), (148, self.__screenHeight)], 1) # vertical line
        pygame.draw.lines(self.__lcd, self.__green, False, [(1,204), (148, 204)], 1) # lower line

    def showOpeningMessage(self):
        txt = self.__csFont.render("Acquiring...", 1, self.__yellow)
        self.__lcd.blit(txt, ((self.__screenWidth - txt.get_width())/2, 30))

    def drawHoldButton(self, isOn):
        if (isOn):
            txtColor = self.__white
            bgColor = self.__medPurple
        else:
            txtColor = self.__gray
            bgColor = self.__darkPurple

        pygame.draw.rect(self.__lcd, bgColor, (292,30,28,30))
        pygame.draw.rect(self.__lcd, self.__purple, (292,30,28,30), 1)
        txt = self.__btnFont.render("Hold", 1, txtColor)
        self.__lcd.blit(txt, (293, 37))

    def drawMilButton(self, isOn):
        if (isOn):
            txtColor = self.__white
            bgColor = self.__medOrange
        else:
            txtColor = self.__gray
            bgColor = self.__darkOrange

        pygame.draw.rect(self.__lcd, bgColor, (292,92,28,30))
        pygame.draw.rect(self.__lcd, self.__orange, (292,92,28,30), 1)
        txt = self.__btnFont.render("Mil", 1, txtColor)
        self.__lcd.blit(txt, (298, 99))

    def drawOffButton(self):
        pygame.draw.rect(self.__lcd, self.__darkRed, (292,154,28,30))
        pygame.draw.rect(self.__lcd, self.__red, (292,154,28,30), 1)
        txt = self.__btnFont.render("Off", 1, self.__white)
        self.__lcd.blit(txt, (298, 161))

    def drawExitButton(self):
        pygame.draw.rect(self.__lcd, self.__darkRed, (292,220,28,20))
        pygame.draw.rect(self.__lcd, self.__red, (292,220,28,20), 1)
        txt = self.__btnFont.render("Exit", 1, self.__white)
        self.__lcd.blit(txt, (296, 222))

    def clearCallsignAndID(self):
        pygame.draw.rect(self.__lcd, self.__black, (1,3,self.__screenWidth-2,92))

    def displayICAOid(self, id):
        txt = self.__idFont.render(id, 1, self.__yellow)
        self.__lcd.blit(txt, ((self.__screenWidth - txt.get_width())/2, 4))

    def displayCallsign(self, cs, isMil):
        if (isMil):
            pygame.draw.rect(self.__lcd, self.__medRed, (1,30,self.__screenWidth-2,43))
        txt = self.__csFont.render(cs.strip(), 1, self.__yellow)
        self.__lcd.blit(txt, ((self.__screenWidth - txt.get_width())/2, 30))

    def displayLastSeen(self, adsbObj):
        dateParts = adsbObj.theDate.split("/")
        formattedDate = dateParts[1] + "-" + dateParts[2] + "-" + dateParts[0]
        formattedTime = adsbObj.theTime.split(".")[0]
        txt = self.__lastSeenFont.render("Last seen:  " + formattedTime + "  " + formattedDate, 1, self.__cyan)
        self.__lcd.blit(txt, ((self.__screenWidth - txt.get_width())/2, 73))
    
    def displayRecents(self, recentCs):
        xpos = 152
        yAnchor = 98
        ypos = yAnchor
        pygame.draw.rect(self.__lcd, self.__black, (151,yAnchor,136,140))
        for x in range(0, len(recentCs)):
            if (x == 10):
                xpos = 221
                ypos = yAnchor
            if (Util.isMilCallsign(recentCs[x])):
                foreColor = self.__yellow
                backColor = self.__medRed
            else:
                foreColor = self.__mediumBlue
                backColor = self.__black
            cs = recentCs[x]
            txt = self.__recentFont.render(cs[:8], 1, foreColor, backColor)
            self.__lcd.blit(txt, (xpos, ypos))
            ypos += 14
    
    def updateCallsignCount(self, civCnt, milCnt):
        pygame.draw.rect(self.__lcd, self.__black, (3,207,143,15))
        lab = self.__statsFont.render("civ:", 1, self.__cyan)
        self.__lcd.blit(lab, (3,206))
        num = self.__statsFont.render("{:,}".format(civCnt), 1, self.__white)
        self.__lcd.blit(num, (3 + lab.get_width() + 1,206))

        lab = self.__statsFont.render("mil:", 1, self.__cyan)
        self.__lcd.blit(lab, (79,206))
        num = self.__statsFont.render("{:,}".format(milCnt), 1, self.__white)
        self.__lcd.blit(num, (79 + lab.get_width() + 1,206))

    def updateAdsbCount(self, cnt):
        pygame.draw.rect(self.__lcd, self.__black, (3,223,143,15))
        lab = self.__statsFont.render("adsb:", 1, self.__cyan)
        self.__lcd.blit(lab, (3,222))
        num = self.__statsFont.render("{:,}".format(cnt), 1, self.__white)
        self.__lcd.blit(num, (3 + lab.get_width() + 1,222))

    def displayDistance(self, dist, bearing):
        pygame.draw.rect(self.__lcd, self.__black, (204,3,84,27))
        txt = self.__distFont.render("{0:0.1f}".format(dist) + " mi", 1, self.__cyan)
        width = txt.get_width()
        self.__lcd.blit(txt, (self.__screenWidth-width-4, 2))
        txt = self.__distFont.render("{0:0.1f}".format(bearing) + u'\N{DEGREE SIGN}' + " " + Util.getCompassDir(bearing), 1, self.__cyan)
        width = txt.get_width()
        self.__lcd.blit(txt, (self.__screenWidth-width-4, 15))

    def displayFlightData(self, adsbObj, persist):
        altitude = adsbObj.altitude
        groundSpeed = adsbObj.groundSpeed
        lat = adsbObj.lat
        lon = adsbObj.lon
        verticalRate = adsbObj.verticalRate
        squawk = adsbObj.squawk

        if (persist):
            if (altitude == ""):
                altitude = adsbObj.lastAltitude
            else:
                adsbObj.lastAltitude = altitude

            if (lat == ""):
                lat = adsbObj.lastLat
            else:
                adsbObj.lastLat = lat

            if (lon == ""):
                lon = adsbObj.lastLon
            else:
                adsbObj.lastLon = lon

            if (verticalRate == ""):
                verticalRate = adsbObj.lastVerticalRate
            else:
                adsbObj.lastVerticalRate = verticalRate

            if (groundSpeed == ""):
                groundSpeed = adsbObj.lastGroundSpeed
            else:
                adsbObj.lastGroundSpeed = groundSpeed

            if (squawk == ""):
                squawk = adsbObj.lastSquawk
            else:
                adsbObj.lastSquawk = squawk

        xpos = 3
        ypos = 97
        txt = self.__fltFont.render("Alt: " + altitude, 1, self.__medOrange)
        self.__lcd.blit(txt, (xpos, ypos))
        txt = self.__fltFont.render("Lat: " + lat, 1, self.__medOrange)
        self.__lcd.blit(txt, (xpos, ypos+17))
        txt = self.__fltFont.render("Lon:" + lon, 1, self.__medOrange)
        self.__lcd.blit(txt, (xpos, ypos+34))
        txt = self.__fltFont.render("VRt: " + verticalRate, 1, self.__medOrange)
        self.__lcd.blit(txt, (xpos, ypos+51))
        txt = self.__fltFont.render("GSp: " + groundSpeed, 1, self.__medOrange)
        self.__lcd.blit(txt, (xpos, ypos+68))
        txt = self.__fltFont.render("Sqk: " + squawk, 1, self.__medOrange)
        self.__lcd.blit(txt, (xpos, ypos+85))

    def clearFlightData(self):
        pygame.draw.rect(self.__lcd, self.__black, (3,98,144,102))

    def refreshDisplay(self):
        pygame.display.update()

    def displayTwitterLogo(self):
        image = pygame.image.load(r'twitter-logo.png')
        self.__lcd.blit(image, (self.__screenWidth+1, 0)) 

    def displayRemoteLogo(self):
        image = pygame.image.load(r'remote-logo.png')
        self.__lcd.blit(image, (self.__screenWidth+18, 2)) 

    def displayOptionsTitle(self):
        pygame.draw.rect(self.__lcd, self.__darkPurple, (0, 0, self.__displayWidth, 23), 0)
        txt = self.__titleFont.render('ads-b scanner - ' + u'\N{COPYRIGHT SIGN}' + ' Erik Orange', 1, self.__yellow)
        self.__lcd.blit(txt, ((self.__displayWidth - txt.get_width())/2, 0))

    def displayOptionsLabels(self, baseY):
        lblX=14
        labels = [("Mode:", lblX, baseY), ("Tweet:", lblX, baseY+40), ("Remote:", lblX, baseY+80), ("Mil Test:", lblX, baseY+120)]
        for lbl in labels:
            txt = self.__optsFont.render(lbl[0], 1, self.__cyan)
            self.__lcd.blit(txt, (lbl[1], lbl[2]))

    def drawOptionsButtons(self):
        txt = self.__titleFont.render(u'\N{WHITE UP-POINTING TRIANGLE}', 1, self.__green)
        self.__lcd.blit(txt, (302, 37))

        txt = self.__titleFont.render(u'\N{DOWNWARDS ARROW}', 1, self.__green)
        self.__lcd.blit(txt, (302, 96))

        txt = self.__titleFont.render(u'\N{LEFTWARDS ARROW}', 1, self.__green)
        self.__lcd.blit(txt, (302, 220))

    def drawOptionPointer(self, posX, posY, visible):
        if (visible):
            color = self.__green
        else:
            color = self.__black

        pygame.draw.polygon(self.__lcd, color, [(posX, posY), (posX-7, posY-5), (posX-7, posY+5), (posX, posY)], 0)
            
    def setupOptionsDisplay(self):
        BUTTON_CHANGE= 17
        BUTTON_DOWN = 22
        BUTTON_QUIT = 27

        self.__lcd.fill(self.__black)
        self.displayOptionsTitle()

        baseY=50
        self.displayOptionsLabels(baseY)
        self.drawOptionsButtons()

        options = [ ('Military', 'Military + Civilian'),
                    ('Disable', 'Military Only', 'Military + Civilian'),
                    ('Disable', 'Enable'),
                    ('Disable', 'Enable')]

        # order of line item options in tuple
        modeT = 0       # milMode: T|F
        tweetT = 1      # tweetAllRecent,tweetMil: (F,F) | (F,T) | (T,T)
        remoteT = 2     # remoteHead: F|T
        milTestT = 3    # milTestMode: F|T

        # track current choice in each line item
        modeIdx = 0
        tweetIdx = 0
        remoteIdx = 0
        milTestIdx = 0

        # draw initial choices
        valX=87
        txt = self.__optsFont.render(options[modeT][modeIdx], 1, self.__yellow)
        self.__lcd.blit(txt, (valX, baseY))
        txt = self.__optsFont.render(options[tweetT][tweetIdx], 1, self.__yellow)
        self.__lcd.blit(txt, (valX, baseY+40))
        txt = self.__optsFont.render(options[remoteT][remoteIdx], 1, self.__yellow)
        self.__lcd.blit(txt, (valX, baseY+80))
        txt = self.__optsFont.render(options[milTestT][milTestIdx], 1, self.__yellow)
        self.__lcd.blit(txt, (valX, baseY+120))

        # set up coords for option pointer
        arX=9
        arY=baseY+8
        arCoords=[(arX, arY), (arX, arY+40), (arX,arY+80), (arX,arY+120)]
        arIdx=0
        self.drawOptionPointer(arCoords[arIdx][0], arCoords[arIdx][1], True)
        self.refreshDisplay()

        exitFlag=False
        totalSeconds=20
        currentSeconds=totalSeconds

        timeTxt = self.__optsFont.render(str(currentSeconds), 1, self.__yellow)
        timeTxtPos = (5,220)
        self.__lcd.blit(timeTxt, timeTxtPos)
        self.refreshDisplay()
        
        startTime=datetime.datetime.now()
        while (not exitFlag):
            endTime=datetime.datetime.now()
            elapsedSeconds=(endTime-startTime).seconds
            if (elapsedSeconds >= 1):
                currentSeconds-=1
                pygame.draw.rect(self.__lcd, self.__black, timeTxt.get_rect(topleft=timeTxtPos))
                if (currentSeconds <= 3):
                    timeColor = self.__red
                else:
                    timeColor = self.__yellow

                timeTxt = self.__optsFont.render(str(currentSeconds), 1, timeColor)
                self.__lcd.blit(timeTxt, timeTxtPos)
                self.refreshDisplay()
                startTime=datetime.datetime.now()
            
            if (currentSeconds == 0):
                exitFlag = True

            if Util.isButtonPressed(BUTTON_DOWN):
                self.drawOptionPointer(arCoords[arIdx][0], arCoords[arIdx][1], False)
                arIdx+=1
                if (arIdx == len(arCoords)):
                    arIdx = 0
                
                self.drawOptionPointer(arCoords[arIdx][0], arCoords[arIdx][1], True)
                self.refreshDisplay()
                currentSeconds=totalSeconds+1
                time.sleep(0.25)
            
            if Util.isButtonPressed(BUTTON_CHANGE):
                if (arIdx == 0):
                    txt = self.__optsFont.render(options[modeT][modeIdx], 1, self.__black)
                    pygame.draw.rect(self.__lcd, self.__black, txt.get_rect(topleft=(valX,baseY)))
                    modeIdx+=1
                    if (modeIdx == len(options[modeT])):
                        modeIdx = 0

                    txt = self.__optsFont.render(options[modeT][modeIdx], 1, self.__yellow)
                    self.__lcd.blit(txt, (valX, baseY))

                elif (arIdx == 1):
                    txt = self.__optsFont.render(options[tweetT][tweetIdx], 1, self.__black)
                    pygame.draw.rect(self.__lcd, self.__black, txt.get_rect(topleft=(valX,baseY+40)))
                    tweetIdx+=1
                    if (tweetIdx == len(options[tweetT])):
                        tweetIdx = 0

                    txt = self.__optsFont.render(options[tweetT][tweetIdx], 1, self.__yellow)
                    self.__lcd.blit(txt, (valX, baseY+40))

                elif (arIdx == 2):
                    txt = self.__optsFont.render(options[remoteT][remoteIdx], 1, self.__black)
                    pygame.draw.rect(self.__lcd, self.__black, txt.get_rect(topleft=(valX,baseY+80)))
                    remoteIdx+=1
                    if (remoteIdx == len(options[remoteT])):
                        remoteIdx = 0

                    txt = self.__optsFont.render(options[remoteT][remoteIdx], 1, self.__yellow)
                    self.__lcd.blit(txt, (valX, baseY+80))

                elif (arIdx == 3):
                    txt = self.__optsFont.render(options[milTestT][milTestIdx], 1, self.__black)
                    pygame.draw.rect(self.__lcd, self.__black, txt.get_rect(topleft=(valX,baseY+120)))
                    milTestIdx+=1
                    if (milTestIdx == len(options[milTestT])):
                        milTestIdx = 0

                    txt = self.__optsFont.render(options[milTestT][milTestIdx], 1, self.__yellow)
                    self.__lcd.blit(txt, (valX, baseY+120))

                self.refreshDisplay()
                currentSeconds=totalSeconds+1
                time.sleep(0.25)

            if Util.isButtonPressed(BUTTON_QUIT):
                exitFlag=True
                time.sleep(0.25)

        # determine final options            
        if (modeIdx == 0):
            milMode = True
        else:
            milMode = False
        
        if (tweetIdx == 0):
            tweetLast10CivMil = False
            tweetMil = False
        elif (tweetIdx == 1):
            tweetLast10CivMil = False
            tweetMil = True
        else:
            tweetLast10CivMil = True
            tweetMil = True

        if (remoteIdx == 0):
            remoteHead = False
        else:
            remoteHead = True
    
        if (milTestIdx == 0):
            milTestMode = False
        else:
            milTestMode = True

        return milMode, tweetMil, tweetLast10CivMil, remoteHead, milTestMode
        



    