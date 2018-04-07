
all: Src/ui.py

Src/ui.py: QT5Designer_ROMClient_v04-00.ui
	pyuic5 QT5Designer_ROMClient_v04-00.ui -o Src/gui.py