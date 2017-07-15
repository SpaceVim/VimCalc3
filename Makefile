all: unittest manualtest

unittest:
	cd plugin && python3 -m unittest -v

manualtest:
	gvim --noplugin -c "set rtp+=$$PWD" -c "runtime! plugin/vimcalc.vim" \
		-c "Calc" -c "wincmd o"
