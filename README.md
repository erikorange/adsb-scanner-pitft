# adsb-scanner-pitft

## Overview
This is python code for an ads-b scanner running on a Raspberry Pi.  It uses dump1090-fa to provide the mode S records.  The output is rendered onto a TFT display and saved to daily log files.

## Setup and Installtion
Read the install guide in the __docs__ folder.

## To Do
- consume 1 ads-b record before entering main loop to prevent fallthrough on no stdin
- change stdin to socket reads
- hook up GPIO button 23 (shutdown was deprecated after buster upgrade)
- detect if no network; manual date/time set?
- keep track of date change and dynamically create new folder
- Turn Exit into options page -> redo options choices, display recent mil and civ, show queue length
- detect if Internet available -> if not, get manual time/date and disable twitter
- detect if local network available -> if not, disable remote head option

## Done
- main thread: create queue that accepts ads-b records, then launch remote thread
- remote thread: consume queue, send via UDP to remote head
- button borders
- truncate display of recent callsigns to 8 characters
- Add remote logo
- Add Mil Test Mode startup option
- Add "TEST" to tweet if Mil Test Mode
- Don't write mill callsigns to file if Mil Test Mode