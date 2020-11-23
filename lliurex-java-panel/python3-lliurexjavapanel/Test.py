from PyQt5 import QtCore, QtGui, QtWidgets

class LoadingButton(QtWidgets.QLabel):
    #@QtCore.pyqtSlot()
    def start(self):
        if hasattr(self, "_movie"):
            self._movie.start()

   # @QtCore.pyqtSlot()
    def stop(self):
        if hasattr(self, "_movie"):
            self._movie.stop()
            pixmap=QtGui.QPixmap("ok.svg")
            self.setPixmap(pixmap)

    def setGif(self, filename):
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setFileName(filename)
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

   
    @QtCore.pyqtSlot(int)
    def on_frameChanged(self, frameNumber):
        self.setPixmap(self._movie.currentPixmap().scaled(50,50))

if __name__ == '__main__':
    import sys
    import random
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(w)
   # for i in range(5):

    button = LoadingButton("Install")
    button.setGif("loading2.gif")
    button.start()

       # QtCore.QTimer.singleShot(random.randint(3000, 6000), button.start)
    QtCore.QTimer.singleShot(random.randint(8000, 12000), button.stop)
    lay.addWidget(button)
    button.setAlignment(QtCore.Qt.AlignCenter)
    label=QtWidgets.QLabel()
    label.setText("Loading...")
    label.setAlignment(QtCore.Qt.AlignCenter)
    lay.addWidget(label)

    container=QtWidgets.QVBoxLayout()

    hbox=QtWidgets.QHBoxLayout()
   # hbox.addStretch(1)
    l1=QtWidgets.QLabel()
    pixmap=QtGui.QPixmap("openjdk.png").scaled(50,50)
    l1.setPixmap(pixmap)
    l1.setAlignment(QtCore.Qt.AlignCenter)
    l1.setStyleSheet("background-color: white") 
    hbox.addWidget(l1)

    l2=QtWidgets.QLabel()
    l2.setText("openjdk-8")
    l2.setAlignment(QtCore.Qt.AlignLeft)
    l2.setStyleSheet("background-color: white") 
    hbox.addWidget(l2)

    l3=QtWidgets.QLabel()
    pixmap=QtGui.QPixmap("ok.svg").scaled(50,50)
    l3.setPixmap(pixmap)
    l3.setAlignment(QtCore.Qt.AlignCenter)
    l3.setStyleSheet("background-color: white") 

    hbox.addWidget(l3)

    container.addLayout(hbox)
   # lay.addStretch(1)

    hbox1=QtWidgets.QHBoxLayout()
   # hbox.addStretch(1)
    l11=QtWidgets.QLabel()
    pixmap=QtGui.QPixmap("openjdk.png").scaled(50,50)
    l11.setPixmap(pixmap)
    l11.setAlignment(QtCore.Qt.AlignCenter)
    l11.setStyleSheet("background-color: white") 

    hbox1.addWidget(l11)

    l21=QtWidgets.QLabel()
    l21.setText("openjdk-8")
    l21.setAlignment(QtCore.Qt.AlignLeft)
    l21.setStyleSheet("background-color: white") 

    hbox1.addWidget(l21)

    l31=QtWidgets.QLabel()
    pixmap=QtGui.QPixmap("ok.svg").scaled(50,50)
    l31.setPixmap(pixmap)
    l31.setAlignment(QtCore.Qt.AlignCenter)
    l31.setStyleSheet("background-color: white") 

    hbox1.addWidget(l31)
    container.addLayout(hbox1)

    lay.addLayout(container)
    w.show()
    sys.exit(app.exec_())