'''便签：可选保存或不保存'''
from PyQt5 import QtGui, QtCore, QtWidgets
import sys


class NoteWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(250, 300)
        self.setWindowOpacity(0.85) # 便签半透明
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.Tool)

        self.notebox = QtWidgets.QTextEdit()
        self.notebox.setPlaceholderText('便签/备忘录')
        self.initNoteboxText()
        self.btnSave = QtWidgets.QPushButton('保存内容')
        self.btnSave.clicked.connect(self.saveText)
        self.btnHide = QtWidgets.QPushButton('隐藏便签')
        self.btnHide.clicked.connect(self.hide)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.notebox)
        layout.addWidget(self.btnSave)
        layout.addWidget(self.btnHide)
        self.setLayout(layout)

    def initNoteboxText(self):  # 初始化便签内容（从文件读取）
        file = open(r'private\Note.dat', encoding='utf-8')
        content = ''
        for line in file:
            content += line
        self.notebox.setPlainText(content)

    def saveText(self): # 保存便签内容到文件
        content = self.notebox.toPlainText()
        file = open(r'private\Note.dat', 'w', encoding='utf-8')
        file.write(content)

    def mousePressEvent(self, event):
        self.startPos = event.pos()

    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.pos() - self.startPos)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.hide()


if __name__ == '__main__':  # test
    app = QtWidgets.QApplication(sys.argv)
    noteWindow = NoteWindow()
    noteWindow.show()
    sys.exit(app.exec_())
