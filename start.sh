cd /home/pi/adsb-logger
nc 127.0.0.1 30003 | python logger.py > pylog.log
