from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QPoint
import sys
import os
import json
import downloader
import downloading
import youtube_dlc
import subprocess
from fbs_runtime.application_context.PyQt5 import ApplicationContext

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = downloader.Ui_MainWindow()
        self.dw = DownloadingWindow()
        self.ui.setupUi(self)

        self.getDirectory()
        self.removeLinks()

        self.ui.pushButton.clicked.connect(self.downloadVideo)
        self.ui.pushButton_3.clicked.connect(self.chooseDir)
        self.ui.pushButton_2.clicked.connect(self.addLink)
        self.ui.pushButton_4.clicked.connect(self.viewLinks)
        self.ui.pushButton_5.clicked.connect(self.removeLinks)

        self.dw.ui.pushButton_2.clicked.connect(self.openManager)
        self.dw.ui.pushButton_4.clicked.connect(self.tryAgain)

        self.setWindowTitle("VDown")
        self.setWindowIcon(QIcon("./icon.ico"))

    def getDirectory(self):
        file = open('directory.json', 'r')
        json_file = json.load(file)
        self.directory = json_file['directory']

        if self.directory == "":
            self.directory == os.getcwd()
        else:
            self.directory = json_file['directory']

    def viewLinks(self):
        with open('links.txt', 'r') as file:
            links = file.readlines()
            print(links)

        self.dw.show()
        self.dw.viewLinks(links)

    def removeLinks(self):
        with open('links.txt', 'w') as file:
            file.truncate()

    def downloadVideo(self):
        with open('links.txt', 'r') as file:
            links = file.readlines()

        if links == []:
            self.dw.show()
            self.LinksNotFound()

        else:
            ydl_opts = {'format': 'bestvideo/best',
                        'outtmpl': f"{self.directory}\%(title)s.%(ext)s",
                        'progress_hooks': [self.progressHook],
                        'postprocessors': [{ 'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp4', 'preferredquality': '192',}]}

            for link in links:
                with youtube_dlc.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])


    def chooseDir(self):
        self.path = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Music folder:', 'F:\\',QtWidgets.QFileDialog.ShowDirsOnly)
        with open('directory.json', 'r') as f:
            file = json.load(f)

        file['directory'] = self.path

        with open('directory.json', 'w') as f:
            json.dump(file, f)

    def addLink(self):
        with open('links.txt', 'a') as file:
            file.write(self.ui.lineEdit.text()+"\n")
        self.ui.lineEdit.clear()

    def progressHook(self, d):
        self.dw.show()
        if d['status'] == 'finished':
            self.dw.ui.stackedWidget.setCurrentIndex(2)

        if d['status'] == 'downloading':
            self.dw.ui.stackedWidget.setCurrentIndex(1)
            p = d['_percent_str']
            p = p.replace('%', '')
            self.dw.ui.progressBar.setValue(float(p))

    def tryAgain(self):
        self.downloadVideo()

    def openManager(self):
        subprocess.Popen(r'explorer /select', self.directory)

    def SuccessfulDown(self):
        self.dw.ui.stackedWidget.setCurrentWidget(self.dw.ui.page_2)
        self.dw.ui.label_3.setText(self.directory)

    def UnsuccessfulDown(self):
        self.dw.ui.stackedWidget.setCurrentWidget(self.dw.ui.page_3)

    def LinksNotFound(self):
        self.dw.ui.stackedWidget.setCurrentWidget(self.dw.ui.page_4)

class DownloadingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = downloading.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.ui.pushButton.clicked.connect(lambda: self.close())
        self.ui.pushButton_3.clicked.connect(lambda: self.close())
        self.ui.pushButton_6.clicked.connect(lambda: self.close())
        self.ui.pushButton_7.clicked.connect(lambda: self.close())

    def viewLinks(self, list):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_5)
        self.ui.listWidget.addItems(list)
        self.ui.label_7.setText(f"There are {self.ui.listWidget.count()} links in the list")

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    appctxt = ApplicationContext()
    Window = MainWindow()
    Window.show()
    sys.exit(appctxt.app.exec_())