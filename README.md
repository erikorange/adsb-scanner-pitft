# adsb-scanner-pitft

## Overview
This is python code for an ads-b scanner running on a Raspberry Pi.  It uses dump1090-fa to provide the mode S records.  The output is rendered onto a TFT display.

## Features
* Separate Military and Civilian callsign displays
* Last 20 callsigns are shown on a rolling display
* Military callisigns highlihted in bold yellow and red
* Always logs all ads-b records and callsigns to files in datestamped directories
* Hold mode for displaying telemetry for a specific aircraft, including distance and bearing
* Military mode only displays military callsigns
* Optional Twitter integration for notifying you of recent callsigns
* Remote head functionality (hardware under development)
* Startup page for choosing various options

## How do I build one?
Read the [install guide](docs/install.md).

## Prerequisites
The install guide assumes you:

* Know how to download the Raspberry Pi OS
* Know how to write the OS to a SD Card
* Know how to boot a rPi, login with SSH, and perform basic configuration with raspiConfig
* Know how to use a bash shell, and have the ability to troubleshoot if you type something in wrong

## How do I use it?
Read the [using guide](docs/using.md).