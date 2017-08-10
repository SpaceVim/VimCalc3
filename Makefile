all: unittest manualtest

unittest:
	cd autoload && python3 -m unittest -v

manualtest:
	gvim --noplugin -c "set rtp+=$$PWD" -c "runtime! plugin/vimcalc.vim" \
		-c "Calc" -c "wincmd o"
