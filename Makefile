
all: Src/ui.py Src/ui_about.py

Src/ui.py: QT5Designer_ROMClient_v04-00.ui
	pyuic5 $? -o $@

Src/ui_about.py: QT5Designer_AboutROMClient_v04-00.ui
	pyuic5 $? -o $@