ACLOCAL_AMFLAGS = -I m4
SUBDIRS = src
EXTRA_DIST = README.md NEWS AUTHORS COPYING mpd_oled.jpg \
	bootstrap commands.txt \
	\
	doc scripts
docdir = @docdir@
doc_DATA = README.md NEWS AUTHORS COPYING mpd_oled.jpg
docdocdir = ${docdir}/doc
docdoc_DATA = \
	doc/FAQ.md \
	doc/install_moode10_source.md \
	doc/wiring_i2c.png \
	doc/wiring_spi.png
filesdir = ${datarootdir}/${PACKAGE}
files_DATA = scripts/mpd_oled_fifo.conf
bin_SCRIPTS = \
	scripts/mpd_oled_service_install \
	scripts/mpd_oled_service_edit \
	scripts/mpd_oled_service_uninstall \
	scripts/mpd_oled_launch \
	scripts/mpd_oled_usrlocal_check \
	scripts/mpd_oled_usrlocal_uninstall
format_all:
	for f in src/*.cpp src/*.h ; do \
	clang-format -style=file -i $$f; \
	done
