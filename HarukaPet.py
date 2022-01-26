import sys, os
import json
import random
from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
import MyTrayIcon
import MySplashScreen
import Tanoshi
from SoundEffect import voicePlayer, soundPlayer
import Note
import LifeManage
import MouseStalker


class MainWindow(QtWidgets.QWidget):                        # 主窗口
    def __init__(self):
        super().__init__()
        self.w, self.h = 175, 175                           # 初始化长宽（后面为了长方图等比例缩放会被改变，但init之后不再改变，记录初始长宽）
        self.leftClicked = False                            # 鼠标左键被单击
        self.rightClicked = False                           # 鼠标右键被单击
        self.midClicked = False                             # 鼠标中键被单击
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)# 透明背景
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)   # 无边框
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)  # 窗口置顶
        self.setWindowFlag(QtCore.Qt.Tool)                  # 不显示到任务栏

        self.trayicon = MyTrayIcon.TrayIcon(self)           # 系统托盘
        self.trayicon.show()

        self.portrait = QtWidgets.QLabel(self)              # 立绘
        self.portraitMap = QtGui.QPixmap(r'source\Portrait.png')
        if self.portraitMap.width() <= self.portraitMap.height():   # 固定比例缩放图片
            self.portraitMap = self.portraitMap.scaled(self.w,
                                                       int(self.portraitMap.height()*self.w/self.portraitMap.width()),
                                                       QtCore.Qt.IgnoreAspectRatio,
                                                       QtCore.Qt.SmoothTransformation)  # 防止锯齿
            self.h = self.portraitMap.height()
        else:
            self.portraitMap = self.portraitMap.scaled(int(self.portraitMap.width()*self.h/self.portraitMap.height()),
                                             self.h,
                                             QtCore.Qt.IgnoreAspectRatio,
                                             QtCore.Qt.SmoothTransformation)
            self.w = self.portraitMap.width()
        self.resize(self.w*2, self.h)                       # 设置大小（窗口设大一圈，方便后面做挂件）
        self.portrait.setPixmap(self.portraitMap)
        self.portrait.setGeometry(int(self.w/2), 0,         # 立绘位置设为中间
                                  self.w, self.h)
        self.blackholeMap = QtGui.QPixmap(r'source\BlackHole.png')
        self.blackholeMap = self.blackholeMap.scaled(250, 250,
                                                     QtCore.Qt.IgnoreAspectRatio,
                                                     QtCore.Qt.SmoothTransformation)
        self.blackhole = QtWidgets.QLabel(self)
        self.blackhole.setPixmap(self.blackholeMap)
        self.blackhole.setGeometry(int(self.width()/2), 125, 1, 1)
        self.blackhole.setScaledContents(True)  # 可自动缩放
        self.portrait.setScaledContents(True)
        self.blackhole.lower()                              # 黑洞图摆在后面，平时隐藏

        # try:
        #     self.alermWindow = Tanoshi.AlermWindow(self)    # 开播提醒窗口
        # except:
        #     msgBox = QtWidgets.QMessageBox.warning(self, '肥肠抱歉',
        #                                            '由于频繁访问B站API，您已被暂时封禁\n本次启动将失去开播提醒功能！\n建议您暂时亲自去您的单推对象直播间蹲点。')
        self.noteWindow = Note.NoteWindow()                 # 便签窗口
        self.lifeWindow = LifeManage.RemindWindow()         # 生活管理提示窗口
        self.stalker = MouseStalker.Stalker(self)
        self.moveToCorner(right=True,                       # 初始位置设在右下角，NO动画（这行放在最后，避免警示窗口出到右下角）
                          bottom=True, init=True)

    def moveToCorner(self, right: bool, bottom: bool, init: bool=False):    # 安放到角落
        desktop = QtWidgets.QDesktopWidget()
        x, y = 0, 0                                         # 目标位置
        if right and bottom:                                # 右下
            x = desktop.availableGeometry().width() - self.width()
            y = desktop.availableGeometry().height() - self.height()
        elif right and not bottom:                          # 右上
            x = desktop.availableGeometry().width() - self.width()
            y = 0
        elif not right and bottom:                          # 左下
            x = 0
            y = desktop.availableGeometry().height() - self.height()
        elif not right and not bottom:                      # 左上
            x, y = 0, 0
        if not init:
            self.teleport(x, y)
        else:
            self.move(x, y)

    def teleport(self, x: int, y: int):
        """瞬移动画"""
        # 步骤一：消失特效
        soundPlayer.play_music(r'source\SoundEffect\Teleport.wav')
        blackholeAppear = QtCore.QPropertyAnimation(self.blackhole, b'geometry', self)
        blackholeAppear.setStartValue(QtCore.QRect(int(self.width()/2), 125, 1, 1))
        blackholeAppear.setEndValue(QtCore.QRect(int((self.width()-250)/2), 0, 250, 250))
        blackholeAppear.setDuration(350)
        portraitDisappear = QtCore.QPropertyAnimation(self.portrait, b'geometry', self)
        portraitDisappear.setStartValue(QtCore.QRect(int(self.w/2), 0, self.w, self.h))
        portraitDisappear.setEndValue(QtCore.QRect(int(self.width()/2), 125, 1, 1))
        portraitDisappear.setDuration(350)
        blackholeDisappear = QtCore.QPropertyAnimation(self.blackhole, b'geometry', self)
        blackholeDisappear.setStartValue(QtCore.QRect(int((self.width()-250)/2), 0, 250, 250))
        blackholeDisappear.setEndValue(QtCore.QRect(int(self.width()/2), 125, 1, 1))
        blackholeDisappear.setDuration(350)
        stepOne = QtCore.QSequentialAnimationGroup(self)
        stepOne.addAnimation(blackholeAppear)
        stepOne.addAnimation(portraitDisappear)
        stepOne.addAnimation(blackholeDisappear)
        # 步骤二：瞬移（本来应该用move，但finished.connect出问题了）
        stepTwo = QtCore.QPropertyAnimation(self, b'pos', self)
        stepTwo.setStartValue(self.pos())
        stepTwo.setEndValue(QtCore.QPoint(x, y))
        stepTwo.setDuration(1)
        # 步骤三：出现特效
        blackholeAppear2 = QtCore.QPropertyAnimation(self.blackhole, b'geometry', self)
        blackholeAppear2.setStartValue(QtCore.QRect(int(self.width()/2), 125, 1, 1))
        blackholeAppear2.setEndValue(QtCore.QRect(int((self.width()-250)/2), 0, 250, 250))
        blackholeAppear2.setDuration(350)
        portraitAppear = QtCore.QPropertyAnimation(self.portrait, b'geometry', self)
        portraitAppear.setStartValue(QtCore.QRect(int(self.width()/2), 125, 1, 1))
        portraitAppear.setEndValue(QtCore.QRect(int(self.w/2), 0, self.w, self.h))
        portraitAppear.setDuration(350)
        blackholeDisappear2 = QtCore.QPropertyAnimation(self.blackhole, b'geometry', self)
        blackholeDisappear2.setStartValue(QtCore.QRect(int((self.width()-250)/2), 0, 250, 250))
        blackholeDisappear2.setEndValue(QtCore.QRect(int(self.width()/2), 125, 1, 1))
        blackholeDisappear2.setDuration(350)
        stepTri = QtCore.QSequentialAnimationGroup(self)
        stepTri.addAnimation(blackholeAppear2)
        stepTri.addAnimation(portraitAppear)
        stepTri.addAnimation(blackholeDisappear2)
        # 三个步骤的组合
        animes = QtCore.QSequentialAnimationGroup(self)
        animes.addAnimation(stepOne)
        animes.addAnimation(stepTwo)
        animes.addAnimation(stepTri)
        animes.start()

    def mousePressEvent(self, QEvent):
        self.startPos = QEvent.pos()                        # 按下时记录位置
        if QEvent.button() == QtCore.Qt.LeftButton:
            self.leftClicked = True
        elif QEvent.button() == QtCore.Qt.MidButton:
            self.midClicked = True
        elif QEvent.button() == QtCore.Qt.RightButton:
            self.rightClicked = True

    def mouseMoveEvent(self, QEvent):                       # 拖动窗口
        self.move(self.pos() + QEvent.pos() - self.startPos)# 计算位置并移动
        if self.leftClicked or self.rightClicked or self.midClicked:    # 初次被调用这个Event时（拖动时只播一次音频）
            voicePlayer.play_music(r'source\Move.wav')
        self.leftClicked = False
        self.rightClicked = False
        self.midClicked = False                             # 移动了，不是单击

    def mouseReleaseEvent(self, QEvent):
        if QEvent.button() == QtCore.Qt.MidButton:          # 中键单击打开便利贴
            if self.midClicked:
                self.midClicked = False  # 左键已松开，恢复初始状态
                self.noteEvent()
        elif QEvent.button() == QtCore.Qt.RightButton:
            self.rightClicked = False
        elif QEvent.button() == QtCore.Qt.LeftButton:       # 左键单击
            if self.leftClicked:
                self.leftClicked = False                    # 左键单击交互：随机触发一种音效，同时人物跳动
                filename = r'source\Interaction\Interact.json'
                with open(filename, encoding='utf-8') as file:
                    voices = json.load(file)
                    voice = random.choice(voices)
                    voicePlayer.play_music(voice)
                soundPlayer.play_music(r'source\SoundEffect\Knock.wav')
                self.get_jump_anime().start()
    
    def get_jump_anime(self) -> QtCore.QAnimationGroup:
        upAnime = QtCore.QPropertyAnimation(self, b'pos', self)
        upAnime.setStartValue(self.pos())
        upAnime.setEndValue(self.pos() + QtCore.QPoint(0, -25))
        upAnime.setDuration(150)
        downAnime = QtCore.QPropertyAnimation(self, b'pos', self)
        downAnime.setStartValue(self.pos() + QtCore.QPoint(0, -25))
        downAnime.setEndValue(self.pos())   # 移动需要时间，而动画是多线程的，所以这里要按原来的pos去思考
        downAnime.setDuration(150)
        animeGroup = QtCore.QSequentialAnimationGroup(self)
        animeGroup.addAnimation(upAnime)
        animeGroup.addAnimation(downAnime)
        return animeGroup

    def contextMenuEvent(self, QEvent):                     # 右键菜单
        menu = QtWidgets.QMenu()                            # 创建母菜单

        menu.addSeparator() # 分割线
        mouse = menu.addAction('鼠标挂坠(M)')
        if self.stalker.stalkThread.stopped:
            mouse.setIcon(QtGui.QIcon(QtGui.QPixmap(r'source\Checked-No.png')))
        else:
            mouse.setIcon(QtGui.QIcon(QtGui.QPixmap(r'source\Checked-Yes.png')))
        # menu.addSeparator() # 分割线
        voice = menu.addAction('人声(V)')
        if json.load(open(r'source\UserData.json', encoding='utf-8'))['voice']:
            voice.setIcon(QtGui.QIcon(QtGui.QPixmap(r'source\Checked-Yes.png')))
        else:
            voice.setIcon(QtGui.QIcon(QtGui.QPixmap(r'source\Checked-No.png')))
        sound = menu.addAction('音效(S)')
        if json.load(open(r'source\UserData.json', encoding='utf-8'))['sound']:
            sound.setIcon(QtGui.QIcon(QtGui.QPixmap(r'source\Checked-Yes.png')))
        else:
            sound.setIcon(QtGui.QIcon(QtGui.QPixmap(r'source\Checked-No.png')))
        menu.addSeparator()  # 分割线
        move = menu.addMenu('安放至角落')                     # 移动-子菜单
        corner = []
        for i, text in enumerate(['右下角(3)', '左下角(1)', '右上角(9)', '左上角(7)']):
            action = move.addAction(text)
            action.setObjectName(str(i))
            action.setIcon(QtGui.QIcon(QtGui.QPixmap(f'source\\Arrow{i}.png')))
            corner.append(action)
        mini = menu.addAction('隐藏(H)')
        action = menu.exec_(self.mapToGlobal(QEvent.pos())) # 布局到全局

        if action == mouse:
            self.mouseAction()
        elif action == voice:   # 人声是否打开
            self.voiceAction()
        elif action == sound:   # 音效是否打开
            self.soundAction()
        elif action == mini:                                # 隐藏到系统托盘
            voicePlayer.play_music(r'source\Hide.wav')
            self.hide()
        elif action in corner:                              # 安放至角落
            i = int(action.objectName())
            self.moveToCorner(i % 2 - 1, int(i / 2) - 1)
    
    def mouseAction(self):
        if self.stalker.isHidden():
            soundPlayer.play_music(r'MouseStalker\effect.wav')
            self.stalker.start()
        else:
            self.stalker.pause()

    def voiceAction(self):
        """打开/关闭人声"""
        file =open(r'source\UserData.json', encoding='utf-8')
        data = json.load(file)
        file.close()
        data['voice'] = not data['voice']
        if data['voice']:
            voicePlayer.setVolume(100)
        else:
            voicePlayer.setVolume(0)
        file = open(r'source\UserData.json', 'w', encoding='utf-8')
        json.dump(data, file)
        file.close()

    def soundAction(self):
        file = open(r'source\UserData.json', encoding='utf-8')
        data = json.load(file)
        file.close()
        data['sound'] = not data['sound']
        if data['sound']:
            soundPlayer.setVolume(100)
        else:
            soundPlayer.setVolume(0)
        file = open(r'source\UserData.json', 'w', encoding='utf-8')
        json.dump(data, file)
        file.close()
    
    def noteEvent(self):
        if self.noteWindow.isHidden():
            voicePlayer.play_music(r'source\Note.wav')
            self.noteWindow.show()
        else:
            self.noteWindow.hide()
    
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """快捷键。我也不知道为啥组合键(Ctrl+*)就是搞不出来，反正不是全局监听而是只有一个窗口内部能监听，随便搞吧。"""
        if event.key() == QtCore.Qt.Key.Key_7:
            self.moveToCorner(False, False)
        elif event.key() == QtCore.Qt.Key.Key_1:
            self.moveToCorner(False, True)
        elif event.key() == QtCore.Qt.Key.Key_9:
            self.moveToCorner(True, False)
        elif event.key() == QtCore.Qt.Key.Key_3:
            self.moveToCorner(True, True)
        elif event.key() == QtCore.Qt.Key.Key_H:
            voicePlayer.play_music(r'source\Hide.wav')
            self.hide()
        elif event.key() == QtCore.Qt.Key.Key_M:
            self.mouseAction()
        elif event.key() == QtCore.Qt.Key.Key_N:
            self.noteEvent()
        elif event.key() == QtCore.Qt.Key.Key_S:
            self.soundAction()
        elif event.key() == QtCore.Qt.Key.Key_V:
            self.voiceAction()


if __name__ == '__main__':
    # 防止从奇怪的路径启动程序导致程序内使用的相对路径出错，先cd过去
    os.chdir(os.path.split(os.path.realpath(__file__))[0])

    app = QtWidgets.QApplication(sys.argv)
    with open(r'source/style.qss', 'r') as f:
        qss = f.read()
    app.setStyleSheet(qss)
    app.setFont(QtGui.QFont('微软雅黑', 9))

    soundPlayer.play_music(random.choice((
        r'source\Welcome-Z.wav',
        r'source\Welcome-DCD.wav',
    )))
    splash = MySplashScreen.SplashScreen()
    splash.show()
    app.processEvents()  # 启动画面不影响其他效果
    # 然而现在删了开播提醒功能之后启动速度太快，会一闪而过，所以sleep一下
    sleep(0.5)

    mainWindow = MainWindow()
    mainWindow.show()

    splash.hide()
    del splash

    sys.exit(app.exec_())
