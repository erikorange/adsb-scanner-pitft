# ads-b scanner build

## Parts List
* Raspberry Pi 3B or 3B+. This was built using a 3B, but should work on a 3B+.
* 16GB or 32GB Class 10 Micro SD card.  The OS & software uses < 2GB, but you'll want space for the ads-b logs.
* AdaFruit PiTFT Plus 320x240 2.8" TFT, Model 2298.  Has 4 built-in buttons.
  https://www.adafruit.com/product/2298
* One RTL-SDR (__NooElec NESDR Smart__ or __RTL-SDR Blog R820T2 RTL2832U__)
* Recommended:
  * Case: https://www.adafruit.com/product/2253
  * Faceplate: https://www.adafruit.com/product/2807

## Install Raspbian
1.	Download Raspbian Buster lite.
2.	Format SD card.
3.	Write the Raspbian image to SD card.
4.	Enabling wifi: Paste the config below into a file called __wpa_supplicant.conf__. Put your SSID and passphrase into __ssid__ and __psk__, then save the file to the root of the SD card __boot__ volume.

    *Do not use Notepad or Wordpad which will add CRLFs and cause problems. Use a code editor like Notepad++.*

    ```
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=US

    network={
     ssid="your-ssid"
     psk="your-passphrase"
    }
    ```

5.	Create an empty file named __ssh__ in the root of the SD card __boot__ volume to enable the SSH interface.
6.	Boot the Pi with the SD card, and locate its IP address using your router.

## Configure Raspbian
1.	SSH into the pi (username: pi, password: raspberry)
2.	`sudo raspi-config`
3.	__Change User Password__
4.  __Network Options -> Hostname__
5.	__Localisation Options -> Change Locale -> en_US.UTF-8 UTF-8__, then __en_US.UTF-8__
6.	__Localisation Options -> Change Timezone__
7.	__Advanced Options -> Expand Filesystem__
8.	Finish and reboot.
9.  Log in and update the OS:
    ```
    sudo apt-get update
    sudo apt-get upgrade --fix-missing
    sudo reboot
    ```

## Install Adafruit TFT display drivers
```
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pitft.sh
chmod +x adafruit-pitft.sh
sudo ./adafruit-pitft.sh		[Choose 90 degrees rotation, and yes to boot to console]
```
References:

https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install-2

## Install dump1090-fa
```
wget https://flightaware.com/adsb/piaware/files/packages/pool/piaware/p/piaware-support/piaware-repository_3.8.0_all.deb
sudo dpkg -i piaware-repository_3.8.0_all.deb
sudo apt-get update
sudo apt-get install -y dump1090-fa
sudo reboot
```
References:

https://flightaware.com/adsb/piaware/install

https://discussions.flightaware.com/t/piaware-v-3-7-1-on-debian-10-0-buster-amd64-intel-pc/52414

## Install Python packages
```
sudo apt install python3-rpi.gpio
sudo apt-get install python3-pygame
sudo apt install python3-pip
sudo pip3 install twython
```

## The Latitude & Longitude File
The ads-b scanner requires the latitude and longitude of the scanner's location. This enables calculation of the distance and bearing of aircraft relative to the scanner.

Create a file (*not using Notepad or Wordpad*) called __home-lat-lon.txt__ containing 2 separate lines:

```
xx.xxxxxx
yy.yyyyyy
```
where xx.xxxxxx is your latitude (N) and yy.yyyyyy is your  longitude (W) in decimal degrees. Save this file for the __Application Install__ step.

The scanner also maintains a default latitude and longitude if  __home-lat-lon.txt__ can't be read.  You can change these coordinates in __getHomeLatLon()__ in util.py.

## The Twitter API Keys
The ads-b scanner can optionally tweet callsigns and stats to your Twitter account.  Create a file (*not using Notepad or Wordpad*) called __auth.py__ with this format:
```
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
```
Substitute your Twitter API keys. If you don't want the Twitter function, then use the above format as-is (no keys) and leave the Tweet option disabled when the ads-b scanner starts.

Save this file for the __Application Install__ step.

## Application Install
```
cd ~
mkdir adsb-scanner
```
Copy these files to the adsb-scanner directory:
* all .py files
* all .png files
* start.sh
* home-lat-lon.txt
* auth.py

Append this snippet to .bashrc in the pi home folder.  This will cause the ads-b scanner to start upon boot, but not when you start a SSH session.
```
cd ~/adsb-scanner
if [ -n "$SSH_CLIENT" ]; then
  echo "Remote login detected"
else
  echo "Starting ads-b scanner"
  ./start.sh > debug.log 2>&1
fi
```
Grant full permissions to the application:
```
chmod 777 adsb-scanner
chmod 777 adsb-scanner/*
sudo reboot
```


