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

