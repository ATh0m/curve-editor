.PHONY: ui

ui: src/ui/MainWindow.py

src/ui/MainWindow.py: src/ui/mainwindow.ui
	pyuic5 src/ui/mainwindow.ui -o src/ui/MainWindow.py


