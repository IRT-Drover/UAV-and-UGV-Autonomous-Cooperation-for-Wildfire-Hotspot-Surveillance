#!/bin/bash

VEHICLE=$1

prompt_err() {
  echo -e "COMMAND FAILED"
}

status() {
$1
if !( $? -eq 0 ); then
  prompt_err
  exit -1
fi
}

echo
echo "Type 'mode MANUAL' to switch to remote control"
echo "Arm: 'arm throttle force' | Disarm: 'disarm' or 'disarm force' (only use for rover)"
echo
echo '||>>>RUNNING MAVPROXY<<<||'

status 'mavproxy.py --master=/dev/ttyTHS1 --baudrate 57600 --out udp:172.20.10.10:14550 --out udp:127.0.0.1:14551 --aircraft MyRover'