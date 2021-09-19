#!/bin/bash
config='-o 1 -A 0 -f 30 -R -t 120 -c alsa,plughw:Loopback,1'
F=$(head -n 1 /home/pi/mpd_oled/F.txt)
T=$(head -n 1 /home/pi/mpd_oled/T.txt)
e=$(head -n 1 /home/pi/mpd_oled/e.txt)
b=$(head -n 1 /home/pi/mpd_oled/b.txt)
G=$(head -n 1 /home/pi/mpd_oled/G.txt)
g=$(head -n 1 /home/pi/mpd_oled/g.txt)

if [ $F = '0' ]
then
  sudo mpd_oled_service_edit $config -F 1 -T $T -e $e -b $b -G $G -g $g
  echo "1" > /home/pi/mpd_oled/F.txt
fi

if [ $F = '1' ]
then
  sudo mpd_oled_service_edit $config -F 2 -T $T -e $e -b $b -G $G -g $g
  echo "2" > /home/pi/mpd_oled/F.txt
fi

if [ $F = '2' ]
then
  sudo mpd_oled_service_edit $config -F 0 -T $T -e $e -b $b -G $G -g $g
  echo "0" > /home/pi/mpd_oled/F.txt
fi
