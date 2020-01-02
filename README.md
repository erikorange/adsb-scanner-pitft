# adsb-logger-pitft

## Overview
This is python code for an ads-b scanner running on a Raspberry Pi.  It uses dump1090-mutability to provide the mode S records.  The output is rendered onto a TFT display.

## Setup
All files are contained in folder named adsb-logger.

## Required Files not in this rep

### auth.py
API key for twitter notifications:
- consumer_key
- consumer_secret
- access_token
- access_token_secret

### home-lat-lon.txt
The home lat and lon of the device:
- lat
- lon

## To Do
- main thread: create queue that accepts ads-b records, then launch remote thread
- remote thread: consume queue, send via UDP to remote head
- Add remote logo (wifi)
- consume 1 ads-b record before entering main loop to prevent fallthrough on no stdin
- detect if no network and create page for manually entering time
- display temperature
- keep track of date change and create new folder
- Turn Exit into options page -> redo options choices, display recent mil and civ
- detect if Internet available -> if not, get manual time/date and disable twitter
- detect if local network available -> if not, disable remote head option

## Done
- button borders
- truncate display of recent callsigns to 8 characters