#!/bin/bash
config='-o 1 -b 32 -A 0 -G 16 -g 1 -f 30 -R -t 120 -c alsa,plughw:Loopback,1'
F=$(head -n 1 /home/pi/mpd_oled/F.txt)
T=$(head -n 1 /home/pi/mpd_oled/T.txt)

if [ $F = '0' ]
then
  sudo mpd_oled_service_edit $config -F 1 -T $T
  echo "1" > /home/pi/mpd_oled/F.txt
fi

if [ $F = '1' ]
then
  sudo mpd_oled_service_edit $config -F 2 -T $T
  echo "2" > /home/pi/mpd_oled/F.txt
fi

if [ $F = '2' ]
then
  sudo mpd_oled_service_edit $config -F 0 -T $T
  echo "0" > /home/pi/mpd_oled/F.txt
fi
