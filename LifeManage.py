import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import json
from SoundEffect import voicePlayer

#eyeSlugger = {  # 护眼
#    "frequency": 60,    # 经过几个40s来一次护眼提示（60相当于刚好一节课的时间）
#    "message": "阿伟你又在打电动喔，休息一下吧！",
#    "voice": "source\\LifeManage\\Training.wav",
#    "choice": ["好啦，我这就休息一下","烦耶"]
#    }

class RemindWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(250, 365)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.Tool)
        self.setStyleSheet('background-color: #ffe1e6;')
        
        gif = QtGui.QMovie(r'source\LifeManage\Video.gif')
        gif.setScaledSize(QtCore.QSize(200, 200))
        self.gifLabel = QtWidgets.QLabel(self)
        self.gifLabel.setMovie(gif)
        self.gifLabel.setGeometry(25, 25, 200, 200)
        gif.start()

        self.msgLabel = QtWidgets.QLabel('一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十', self)
        self.msgLabel.setWordWrap(True)
        self.msgLabel.setGeometry(25, 225, 200, 50)

        self.btnYes = QtWidgets.QPushButton('test-Yes', self)
        self.btnYes.setStyleSheet('background-color: white;')
        self.btnYes.setGeometry(25, 275, 200, 35)
        self.btnYes.clicked.connect(self.yesEvent)
        self.btnNo = QtWidgets.QPushButton('test-No', self)
        self.btnNo.setStyleSheet('background-color: rgb(225,225,225);')
        self.btnNo.setGeometry(50, 315, 150, 25)
        self.btnNo.clicked.connect(self.noEvent)

        self.refreshThread = TimerThread()
        self.refreshThread.data.connect(self.refreshEvent)
        self.refreshThread.start()

    def refreshEvent(self, data):
        voicePlayer.play_music(data['voice'])
        self.msgLabel.setText(data['message'])
        self.btnYes.setText(data['choice'][0])
        self.btnNo.setText(data['choice'][1])
        self.show()

    def yesEvent(self, QEvent):
        self.hide()
        voicePlayer.play_music(r'source\LifeManage\Yes.wav')

    def noEvent(self, QEvent):
        self.hide()
        voicePlayer.play_music(r'source\LifeManage\No.wav')
    
    def closeEvent(self, event):
        self.refreshThread.loop = False


class TimerThread(QtCore.QThread):
    data = QtCore.pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        file = open(r'source\LifeManage\Life.json', encoding='utf-8')
        self.datas = json.load(file)
        file.close()
        self.loop = True

    def run(self):
        print('Live Manage Thread started.')
        #checkTime = 0   # 检查次数
        count = 0
        while self.loop:
            time.sleep(1)
            count += 1
            if count % 40 != 0:  # 不要刚好60s一次，可能有延迟；也别都30s一次，一起上可能占用大
                continue
            toki = time.localtime() # toki=とき=時，这里不能叫time，所以说变量命名真tm麻烦
            hour = int(time.strftime('%H', toki))
            minute = int(time.strftime('%M', toki))
            # print('%d:%d' % (hour, minute), '检测生活管理事件')
            for data in self.datas.values(): # 遍历Life.json中读取到的事件信息
                i = 0
                for toki in data['times']:  # 遍历事件的每个时间点
                    if toki['hour'] == hour and toki['minute'] == minute:
                        self.data.emit(data)    # 时间正确，发射信息
                        data['times'].pop(i)    # 删除已提醒的时间点
                        i -= 1
                    i += 1
            #checkTime += 1
            #if checkTime % eyeSlugger['frequency'] == 0:
            #    self.data.emit(eyeSlugger)
        print('Live Manage Thread stopped.')


class EyeProtect(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 300)
        # 改成图片处理，像MouseStalker模块一样做个tool.py


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QtGui.QFont('微软雅黑', 14))
    w = EyeProtect()
    w.show()
    sys.exit(app.exec_())
