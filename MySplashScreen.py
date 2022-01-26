from PyQt5 import QtCore, QtGui, QtWidgets

class SplashScreen(QtWidgets.QSplashScreen):                # 启动画面
    def __init__(self):
        super().__init__()
        self.setPixmap(QtGui.QPixmap(r'source\SplashScreen.png'))

    def mousePressEvent(self, event):
        pass
