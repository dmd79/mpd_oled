#!/bin/bash
config='-o 1 -A 0 -f 30 -R -t 120 -c alsa,plughw:Loopback,1'
F=$(head -n 1 /home/pi/mpd_oled/F.txt)
T=$(head -n 1 /home/pi/mpd_oled/T.txt)

if [ $T = '0' ]
then
  echo "1" > /home/pi/mpd_oled/e.txt
  echo "32" > /home/pi/mpd_oled/b.txt
  echo "16" > /home/pi/mpd_oled/G.txt
  echo "1" > /home/pi/mpd_oled/g.txt
  sudo mpd_oled_service_edit $config -F $F -T 1 -e 1 -b 32 -G 16 -g 1
  echo "1" > /home/pi/mpd_oled/T.txt
fi

if [ $T = '1' ]
then
  echo "1" > /home/pi/mpd_oled/e.txt
  echo "32" > /home/pi/mpd_oled/b.txt
  echo "16" > /home/pi/mpd_oled/G.txt
  echo "1" > /home/pi/mpd_oled/g.txt
  sudo mpd_oled_service_edit $config -F $F -T 2 -e 1 -b 32 -G 16 -g 1
  echo "2" > /home/pi/mpd_oled/T.txt
fi

if [ $T = '2' ]
then
  echo "1" > /home/pi/mpd_oled/e.txt
  echo "32" > /home/pi/mpd_oled/b.txt
  echo "16" > /home/pi/mpd_oled/G.txt
  echo "1" > /home/pi/mpd_oled/g.txt
  sudo mpd_oled_service_edit $config -F $F -T 3 -e 1 -b 32 -G 16 -g 1
  echo "3" > /home/pi/mpd_oled/T.txt
fi

if [ $T = '3' ]
then
  echo "2" > /home/pi/mpd_oled/e.txt
  echo "2" > /home/pi/mpd_oled/b.txt
  echo "420" > /home/pi/mpd_oled/G.txt
  echo "10" > /home/pi/mpd_oled/g.txt
  sudo mpd_oled_service_edit $config -F $F -T 4 -e 2 -b 2 -G 420 -g 10
  echo "4" > /home/pi/mpd_oled/T.txt
fi

if [ $T = '4' ]
then
  echo "2" > /home/pi/mpd_oled/e.txt
  echo "2" > /home/pi/mpd_oled/b.txt
  echo "420" > /home/pi/mpd_oled/G.txt
  echo "10" > /home/pi/mpd_oled/g.txt
  sudo mpd_oled_service_edit $config -F $F -T 5 -e 2 -b 2 -G 420 -g 10
  echo "5" > /home/pi/mpd_oled/T.txt
fi

if [ $T = '5' ]
then
  echo "2" > /home/pi/mpd_oled/e.txt
  echo "2" > /home/pi/mpd_oled/b.txt
  echo "420" > /home/pi/mpd_oled/G.txt
  echo "10" > /home/pi/mpd_oled/g.txt
  sudo mpd_oled_service_edit $config -F $F -T 0 -e 2 -b 2 -G 420 -g 10
  echo "0" > /home/pi/mpd_oled/T.txt
fi

