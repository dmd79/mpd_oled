# Moode, Volumio, RuneAudio and MPD OLED Spectrum Display for Raspberry Pi

The mpd_oled program displays an information screen including a music
frequency spectrum on an OLED screen connected to a Raspberry Pi (or similar)
running MPD, this includes Moode, Volumio and rAudio (RuneAudio fork).
The program supports I2C and SPI 128x64 OLED displays with an SSD1306,
SSD1309, SH1106 or SSH1106 controller.
![OLED with mpd_oled](mpd_oled.jpg)

## Install

A binary installation package is provided for Moode and Volumio,
and is the quickest and easiest way to install mpd_oled on these systems.
All other systems should install from source code (Note: the build
commands take a long time to run on a Pi Zero).

### Moode

* [Install mpd_oled from source on Moode 10](doc/install_moode10_source.md)

## Program Help and Options

The following text is printed by running `mpd_oled -h`
```
Usage: mpd_oled -o oled_type [options] [input_file]

Display information about an MPD-based player on an OLED screen

Options
  -h,--help this help message
  --version version information
  -o <type>  OLED type, specified as a number, from the following:
      1 Adafruit SPI 128x64
      3 Adafruit I2C 128x64
      4 Seeed I2C 128x64
      6 SH1106 I2C 128x64
      7 SH1106 SPI 128x64
  -b <num>   number of bars to display (default: 16)
  -g <sz>    gap between bars in, pixels (default: 1)
  -f <hz>    framerate in Hz (default: 15)
  -t <secs>  display timeout in stop mode: -1 always on, 0-3600 secs
  -s <vals>  scroll rate (pixels per second) and start delay (seconds), up
             to four comma separated decimal values (default: 8.0,5.0) as:
                rate_all
                rate_all,delay_all
                rate_title,delay_all,rate_artist
                rate_title,delay_title,rate_artist,delay_artist
  -C <fmt>   clock format: 0 - 24h leading 0 (default), 1 - 24h no leading 0,
                2 - 24h leading 0, 3 - 24h no leading 0
  -d         use USA date format MM-DD-YYYY (default: DD-MM-YYYY)
  -P <val>   pause screen type: p - play (default), s - stop
  -k         cava executable name is cava (default: mpd_oled_cava)
  -c         cava input method and source (default: 'fifo,/tmp/mpd_oled_fifo')
             e.g. 'fifo,/tmp/my_fifo', 'alsa,hw:5,0', 'pulse'
  -R         rotate display 180 degrees
  -I <val>   invert black/white: n - normal (default), i - invert,
             number - switch between n and i with this period (hours), which
             may help avoid screen burn
  -a <addr>  I2C address, in hex (default: default for OLED type)
  -B num     I2C bus number (default: 1, giving device /dev/i2c-1)
  -r <gpio>  I2C/SPI reset GPIO number, if needed (default: 25)
  -D <gpio>  SPI DC GPIO number (default: 24)
  -S <num>   SPI CS number (default: 0)
  -p <plyr>  Player: mpd, moode, volumio, runeaudio (default: detected)
Example :
mpd_oled -o 6 use a SH1106 I2C 128x64 OLED
```

## Spectrum Types

| Type | Description | Channel |
|------|-------------|---------|
| 0 | Filled spectrum | mono |
| 1 | Filled spectrum + peak hold | mono |
| 2 | Dot spectrum | mono |
| 3 | Inverted spectrum | mono |
| 4 | Inverted spectrum + peak hold | mono |
| 5 | VU meter filled | stereo |
| 6 | VU meter filled + peak hold | stereo |
| 7 | VU meter dot | stereo |
| 8 | VU meter inverted | stereo |
| 9 | VU meter inverted + peak hold | stereo |

## Runtime Controls

mpd_oled accepts commands via a named pipe at `/tmp/mpd_oled_ctrl`:

```
echo "next_type"       > /tmp/mpd_oled_ctrl  # cycle spectrum type forward
echo "prev_type"       > /tmp/mpd_oled_ctrl  # cycle spectrum type backward
echo "next_screen"     > /tmp/mpd_oled_ctrl  # cycle screen layout forward
echo "prev_screen"     > /tmp/mpd_oled_ctrl  # cycle screen layout backward
echo "bars_up"         > /tmp/mpd_oled_ctrl  # increase number of bars
echo "bars_down"       > /tmp/mpd_oled_ctrl  # decrease number of bars
echo "sens:150"        > /tmp/mpd_oled_ctrl  # set sensitivity (not persisted)
echo "sens:-1"         > /tmp/mpd_oled_ctrl  # reset sensitivity to default
echo "screensaver"     > /tmp/mpd_oled_ctrl  # toggle screensaver
echo "screensaver_off" > /tmp/mpd_oled_ctrl  # turn off screensaver
```

Please check the [FAQ](doc/FAQ.md)

## Credits

C.A.V.A. is a bar spectrum audio visualizer: <https://github.com/karlstav/cava>

OLED interface based on ArduiPI_OLED: <https://github.com/hallard/ArduiPi_OLED>
(which is based on the Adafruit_SSD1306, Adafruit_GFX, and bcm2835 library
code).

C library for Broadcom BCM 2835: <https://www.airspayce.com/mikem/bcm2835/>
