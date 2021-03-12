#!/bin/bash
config='-o 1 -b 32 -A 0 -G 8 -g 1 -f 30 -R -t 120'
F=$(head -n 1 /home/volumio/mpd_oled/F.txt)
T=$(head -n 1 /home/volumio/mpd_oled/T.txt)

if [ $T = '0' ]
then
  sudo mpd_oled_service_edit $config -F $F -T 1
  echo "1" > /home/volumio/mpd_oled/T.txt
fi

if [ $T = '1' ]
then
  sudo mpd_oled_service_edit $config -F $F -T 2
  echo "2" > /home/volumio/mpd_oled/T.txt
fi

if [ $T = '2' ]
then
  sudo mpd_oled_service_edit $config -F $F -T 0
  echo "0" > /home/volumio/mpd_oled/T.txt
fi
