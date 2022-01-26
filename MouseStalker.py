import json
from math import pi, sin, cos, ceil
import sys
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class StalkThread(QThread):
    poses = pyqtSignal(list)

    def __init__(self, labels, data):
        super().__init__()
        self.labels = labels
        self.speeds = data["datas"][data["choice"]]["speeds"]
        self.radiuses = data["datas"][data["choice"]]["radiuses"]
        self.angles = data["datas"][data["choice"]]["angles"]
        self.stopped = True

    def run(self):
        self.stopped = False
        print('Mouse Stalker Thread started.')
        t = 0   # 度数
        while not self.stopped:
            poses = []
            for i in range(len(self.labels)):
                x = QCursor.pos().x()\
                    + self.radiuses[i] * cos((t * self.speeds[i] + self.angles[i]) / 180 * pi)\
                    - self.labels[i].width() / 2
                y = QCursor.pos().y()\
                    + self.radiuses[i] * sin((t * self.speeds[i] + self.angles[i]) / 180 * pi)\
                    - self.labels[i].height() / 2
                poses.append([int(x), int(y)])
            self.poses.emit(poses)
            t += 1
            sleep(0.017)    # 60帧
        print('Mouse Stalker Thread stopped.')


class Stalker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.maxW = QDesktopWidget().availableGeometry().width()
        self.maxH = QDesktopWidget().availableGeometry().height()
        self.resize(self.maxW, self.maxH)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.Tool)

        file = open(r'MouseStalker\data.json', encoding='utf-8')
        self.data = json.load(file)
        file.close()
        self.labels = []
        self.initLabels(self.data["datas"][self.data["choice"]]["paths"],
                        self.data["datas"][self.data["choice"]]["widths"])
        self.stalkThread = StalkThread(self.labels, self.data)
        self.stalkThread.poses.connect(self.moveLabels)

    def initLabels(self, paths, widths):
        for i in range(len(paths)):
            label = QLabel(self)
            map = QPixmap('MouseStalker\\' + paths[i])
            map = map.scaledToWidth(widths[i], Qt.SmoothTransformation)
            label.setPixmap(map)
            label.setGeometry(QCursor.pos().x(), QCursor.pos().y(), map.width(), map.height())
            self.labels.append(label)

    def moveLabels(self, poses):
        speed = 0.12  # 跟踪鼠标速度比实际鼠标移动速度慢，反而看起来会更流畅更舒服
        # 如果每个label的移动速度有点快慢之分，鼠标快速移动时阵型会被破坏，更有动感，但容易眼花而且实现效果不好，放弃
        for i in range(len(self.labels)):
            self.labels[i].move(
                ceil(self.labels[i].x() + (poses[i][0] - self.labels[i].x()) * speed),
                ceil(self.labels[i].y() + (poses[i][1] - self.labels[i].y()) * speed)
            )
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def pause(self):
        self.stalkThread.stopped = True
        self.hide()

    def start(self):
        self.stalkThread.stopped = False
        self.stalkThread.start()
        self.show()
    
    def mousePressEvent(self, event):  # 只是个突发奇想的小彩蛋
        print('好厉害！你居然点到鼠标挂坠了耶！')
    
    def closeEvent(self, event):
        self.stalkThread.stopped = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    stalker = Stalker()
    stalker.show()
    sys.exit(app.exec_())
