
all: vcsromclient/gui.py vcsromclient/ui_about.py

vcsromclient/gui.py: QT5Designer_ROMClient_v04-00.ui
	pyuic5 $? -o $@

vcsromclient/ui_about.py: QT5Designer_AboutROMClient_v04-00.ui
	pyuic5 $? -o $@