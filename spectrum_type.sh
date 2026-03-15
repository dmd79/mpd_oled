#!/bin/bash
config='-o 1 -A 0 -f 30 -R -t 120 -c alsa,plughw:Loopback,1'
F=$(head -n 1 /home/pi/mpd_oled/F.txt)
T=$(head -n 1 /home/pi/mpd_oled/T.txt)

# Spectrum types:
# 0 = filled spectrum       (mono, 32 bars)
# 1 = filled spectrum+peaks (mono, 32 bars)
# 2 = dot spectrum          (mono, 32 bars)
# 3 = inverted spectrum     (mono, 32 bars)
# 4 = inverted+peaks        (mono, 32 bars)
# 5 = VU filled             (stereo, 2 bars)
# 6 = VU filled+peaks       (stereo, 2 bars)
# 7 = VU dot                (stereo, 2 bars)
# 8 = VU inverted           (stereo, 2 bars)
# 9 = VU inverted+peaks     (stereo, 2 bars)

next_T=$(( (T + 1) % 10 ))

if [ $next_T -lt 5 ]; then
  E=1; B=32; G=8; GAP=1
else
  E=2; B=2; G=175; GAP=10
fi

echo "$E"      > /home/pi/mpd_oled/e.txt
echo "$B"      > /home/pi/mpd_oled/b.txt
echo "$G"      > /home/pi/mpd_oled/G.txt
echo "$GAP"    > /home/pi/mpd_oled/g.txt
echo "$next_T" > /home/pi/mpd_oled/T.txt

sudo mpd_oled_service_edit $config -F $F -T $next_T -e $E -b $B -G $G -g $GAP
