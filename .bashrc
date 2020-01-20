# this is appended to the end of .bashrc
cd ~/adsb-scanner
if [ -n "$SSH_CLIENT" ]; then
  echo "Remote login detected"
else
  echo "Starting ads-b scanner"
  ./start.sh > debug.log 2>&1
fi
