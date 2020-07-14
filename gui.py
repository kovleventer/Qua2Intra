from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qdarkstyle
import timeit

from flowlayout import FlowLayout
import utils

import sys
import os

from config import *

from qua2intra import convert_folder


class LoadWorker(QRunnable):
    class WorkerSignals(QObject):
        result = pyqtSignal(object)
    def __init__(self, foldername, parent):
        super().__init__()
        self.foldername = foldername
        self.signals = LoadWorker.WorkerSignals()
        self.parent = parent

    @pyqtSlot()
    def run(self):
        pixmap = QPixmap(utils.get_folder_image_quaver(self.foldername))
        if pixmap.width() > pixmap.height():
            r = QRect((pixmap.width() - pixmap.height()) // 2, 0, pixmap.height(), pixmap.height())
        else:
            r = QRect(0, (pixmap.height() - pixmap.width()) // 2, pixmap.width(), pixmap.width())
        pixmap = pixmap.copy(r)
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
        songname = utils.get_song_name_quaver(self.foldername)
        self.signals.result.emit((songname, pixmap, self.foldername))

class Card(QLabel):
    def __init__(self, folder, songname, pixmap, main, *args, **kwargs):
        super(Card, self).__init__(*args, **kwargs)
        self.setFixedSize(300, 370)
        self.main = main
        layout = QVBoxLayout()
        layout.setSpacing(0)
        img_label = QLabel()

        img_label.setPixmap(pixmap)

        name_label = QLabel()
        name_label.setWordWrap(True)
        name_label.setStyleSheet("""QLabel {
                                    background-color: #224466;
                                    color: white;
                                    font-weight: bold;
                                    padding: 5px;
                                 }
                                 """)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setText(songname)

        layout.addWidget(img_label)
        layout.addWidget(name_label)

        self.foldername = folder

        self.setLayout(layout)

    def mousePressEvent(self, QMouseEvent):
        self.main.download(self.foldername)


class IconList(QLabel):
    def __init__(self, main, *args):
        super(IconList, self).__init__(*args)
        self.setMinimumSize(400, 400)
        self.main = main

        self.threadpool = QThreadPool()

        self.layout = FlowLayout()
        self.setLayout(self.layout)
        for i, dir in enumerate(os.listdir(QUAVERPATH)):
            print("asd", dir)
            w = LoadWorker(os.path.join(QUAVERPATH, dir), self)
            w.signals.result.connect(self.load_complete)
            self.threadpool.start(w)
            #if i == 5: break

    def load_complete(self, ret):
        s, p, f = ret
        # TODO why is this so god damn slow
        c = Card(folder=f, songname=s, pixmap=p, main=self.main)
        self.layout.addWidget(c)

class DownloadProgress(QLabel):
    def __init__(self, songname, *args):
        super(DownloadProgress, self).__init__(*args)
        layout = QHBoxLayout()
        name_label = QLabel()
        name_label.setStyleSheet("""QLabel {
                                            background-color: #224466;
                                            color: white;
                                            font-weight: bold;
                                            padding: 5px;
                                         }
                                         """)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setText(songname)
        name_policy = QSizePolicy()
        name_policy.setHorizontalStretch(4)
        name_label.setSizePolicy(name_policy)
        layout.addWidget(name_label)
        self.pbar = QProgressBar()
        pbar_policy = QSizePolicy()
        pbar_policy.setHorizontalStretch(1)
        self.pbar.setSizePolicy(pbar_policy)
        layout.addWidget(self.pbar)
        self.setLayout(layout)


class DownloadList(QLabel):
    def __init__(self, main, *args):
        super(DownloadList, self).__init__(*args)
        self.main = main
        self.setFixedHeight(70)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.downlist = []
        self.threadpool = QThreadPool()

    def download(self, filename):
        print("asd")
        if filename not in self.downlist:
            self.downlist.append(filename)
            d = DownloadProgress(utils.get_song_name_quaver(filename))
            self.layout.addWidget(d)
            #w = DownloadWorker(filename, self)
            #w.signals.result.connect(self.load_complete)

class DownloadWorker(QRunnable):
    def __init__(self, foldername):
        super().__init__()
        self.foldername = foldername

    @pyqtSlot()
    def run(self):
        convert_folder(self.foldername)

class DownloadTableModel(QAbstractTableModel):
    def __init__(self, data=None, *args):
        super(DownloadTableModel, self).__init__(*args)
        if data is None: data = []
        self.data = data
        self.names = set()

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            return self.data[row][column]

        return None

    def add(self, filename):
        if filename not in self.names:
            print("Item added: ", filename)
            self.data.append((filename, 0))
            self.layoutAboutToBeChanged.emit()
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self.data), 2))
            self.layoutChanged.emit()
            return self
        return None



class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)

        content = QWidget()

        self.il = IconList(self)
        self.dl = DownloadTableModel()
        self.dlw = QTableView()

        layout = QVBoxLayout()
        scrollAreaIL = QScrollArea()
        scrollAreaIL.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollAreaIL.setWidgetResizable(True)
        scrollAreaIL.setWidget(self.il)
        layout.addWidget(scrollAreaIL)
        self.dlw.setModel(self.dl)
        scrollAreaDL = QScrollArea()
        scrollAreaDL.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollAreaDL.setWidgetResizable(True)
        scrollAreaDL.setWidget(self.dlw)
        layout.addWidget(scrollAreaDL)

        content.setLayout(layout)
        self.setCentralWidget(content)

        self.threadpool = QThreadPool()
        self.show()

    def download(self, filename):
        r = self.dl.add(filename)
        if r:
            w = DownloadWorker(filename)
            self.threadpool.start(w)



app = QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
window = MainWindow()

app.exec_()