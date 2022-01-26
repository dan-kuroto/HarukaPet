'''
Tanoshi（単推し）模块
检查单推列表的开播情况
已废弃，因为实际运行效果并不很好，而我也已经找到了更好的替代品，不打算自己开发了
'''
import time
import webbrowser
import requests
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from random import randint
from SoundEffect import voicePlayer

API = r'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id=%s'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'}

class Room():    # 直播间类
    def __init__(self, room_id: int):
        self.room_id = room_id  # 直播间号
        r = requests.get(API % room_id)
        data = json.loads(r.text)['data']
        self.uname = data['anchor_info']['base_info']['uname']  # 主播昵称
        self.live_status = data['room_info']['live_status'] == 1    # 推测：0闲置,1直播,2轮播
        self.live_status = False    # 为了其他程序，这里初始设为False
        self.title = data['room_info']['title'] # 直播间标题
        self.cover = data['room_info']['cover'] # 直播间封面地址
        #print(self.uname, self.live_status, self.title, self.cover)
        self.face = data['anchor_info']['base_info']['face']    # 主播头像地址（无封面时的备用操作，B站似乎有头像和关键帧两种替代法，但关键帧作为封面我认为不够清晰，头像至少一览无遗）

    def check(self):    # 检查是否开播，需要发布提示
        r = requests.get(API % self.room_id)
        data = json.loads(r.text)['data']
        self.title = data['room_info']['title'] # 更新直播间标题
        self.cover = data['room_info']['cover'] # 更新直播间封面地址
        new_live_status = data['room_info']['live_status'] == 1 # 最新开播状态
        if new_live_status:
            if not self.live_status:    # 防止重复提示，只有上次检查未开播的主播才会提示
                self.live_status = new_live_status  # 更新开播状态
                return True
            else: return False
        else:
            if self.live_status:
                self.live_status = new_live_status  # 更新开播状态
            return False


class CoverLabel(QtWidgets.QLabel):
    def __init__(self, father, room_id):
        super().__init__(father)    # 推测father是指父控件
        self.room_id = room_id

    def mousePressEvent(self, QEvent):
        webbrowser.open('https://live.bilibili.com/%s' % self.room_id)


class AlermWindow(QtWidgets.QWidget):   # 提示窗口
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        '''窗口属性'''
        self.resize(465, 600-110)   # -110：治不了scrollarea只能治这个了
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)   # 无边框
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)  # 窗口置顶
        self.setWindowFlag(QtCore.Qt.Tool)                  # 不显示到任务栏
        self.setStyleSheet('background-color: rgb(45,45,48); color: white')
        
        '''窗口布局'''
        self.winTitle = QtWidgets.QLabel(self)   # 本窗口的标题
        self.winTitle.setText('您的单推列表中有人开播了！')
        self.winTitle.setStyleSheet('background-color: rgb(0,122,204); color: white; font-size: 20px')
        self.winTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.winTitle.setGeometry(0, 0, self.width(), 30)

        self.scroll = QtWidgets.QScrollArea(self)   # 滚动条区域
        self.scroll.move(0, self.winTitle.height())
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 关闭水平滚动条
        self.scroll.setStyleSheet('border: none;')

        self.button = QtWidgets.QPushButton('我知道了', self)
        self.button.setStyleSheet('background-color: rgb(33,121,129); color: lightgrey; border: none; font-size: 18px')
        self.button.setGeometry(self.width()/2 - 100, 410, 200, 50)
        self.button.clicked.connect(self.neoHide)

        '''更新直播提示卡片的线程'''
        self.initScroll()   # 初始化滚动条区域，主要是为了布局考虑，不然会根据初次获取开播量自动生成，按钮的位置可能会很奇怪
        self.refreshThread = AlermThread()
        self.refreshThread.liveRooms.connect(self.refreshScroll)
        self.refreshThread.ifError.connect(self.errorMessage)
        self.refreshThread.start()

    def neoHide(self):
        self.hide()
        self.refreshThread.ifCheck = True  # 窗口隐藏时才允许下次检测

    def errorMessage(self, ifError: bool):
        if ifError:
            QtWidgets.QApplication.setQuitOnLastWindowClosed(False)
            msgBox = QtWidgets.QMessageBox.warning(self, '肥肠抱歉',
                                                   '由于频繁访问B站API，您已被暂时封禁\n本次启动将失去开播提醒功能！\n建议您暂时亲自去您的单推对象直播间蹲点。')

    def initScroll(self):
        n = 6   # 以此数量初始化
        topFiller = QtWidgets.QWidget()    # 开播列表区域
        topFiller.setMinimumSize(self.width(), 165*int((n-1)/2+1)+50)
        topFiller.setStyleSheet('background-color: rgb(30,30,30);')
        self.scroll.setWidget(topFiller)

        self.covers = []
        self.unames = []
        self.titles = []
        for i in range(n):
            coverLabel = QtWidgets.QLabel(topFiller)
            coverLabel.setText('coverLabel')
            coverLabel.setStyleSheet('color: white;')
            #coverLabel.resize(200, 125)
            coverLabel.move((i%2+1) * 15 + i%2 * 200,
                            15 + self.winTitle.height() + int(i/2)*(125+2*20))
            self.covers.append(coverLabel)
        
            unameLabel = QtWidgets.QLabel(topFiller) # 昵称
            unameLabel.setText('unameLabel')
            unameLabel.setStyleSheet('color: rgb(73,193,173);')
            unameLabel.setGeometry((i%2+1) * 15 + i%2 * 200,
                                   15+self.winTitle.height()+int(i/2)*(125+2*20)+125,
                                   200, 20)
            self.unames.append(unameLabel)

            titleLabel = QtWidgets.QLabel(topFiller) # 标题
            titleLabel.setText('titleLabel')
            titleLabel.setStyleSheet('color: rgb(214,157,133);')
            titleLabel.setGeometry((i%2+1) * 15 + i%2 * 200,
                                   15+self.winTitle.height()+int(i/2)*(125+2*20)+125+20,
                                   200, 20)
            self.titles.append(titleLabel)

    def refreshScroll(self, liveRooms: list):   # 刷新滚动区域
        topFiller = QtWidgets.QWidget()    # 开播列表区域
        topFiller.setMinimumSize(self.width(), 165*int((len(liveRooms)-1)/2+1)+50)
        topFiller.setStyleSheet('background-color: rgb(30,30,30);')
        self.scroll.setWidget(topFiller)

        self.covers = []
        self.unames = []
        self.titles = []
        i = 0   # 非常重要，因为用的是绝对定位，这个计数器是计算位置时的重要&唯一参数
        for room in liveRooms:
            try:    # 存在无封面的可能性
                r = requests.get(room.cover)    # 封面
                coverImg = QtGui.QImage.fromData(r.content)
                coverLabel = CoverLabel(topFiller, room.room_id)
                coverImg = coverImg.scaled(200, 125,
                                           QtCore.Qt.IgnoreAspectRatio,
                                           QtCore.Qt.SmoothTransformation)
                coverLabel.setPixmap(QtGui.QPixmap.fromImage(coverImg))
                coverLabel.resize(200, 125)
                coverLabel.move((i%2+1) * 15 + i%2 * 200,
                                15 + self.winTitle.height() + int(i/2)*(125+2*20))
                # 点击访问直播间功能通过类的继承来实现
                self.covers.append(coverLabel)
            except: # 若无封面则用头像代替
                print(room.uname, '由于迷之原因未能找到封面，用头像替代了，可能原因如下：\n[1]主播未设置封面[2]网络原因[3]阿B限流[4]我也猜不透了这')
                r = requests.get(room.face)    # 头像
                coverImg = QtGui.QImage.fromData(r.content)
                coverLabel = CoverLabel(topFiller, room.room_id)
                coverImg = coverImg.scaled(200, 200,
                                           QtCore.Qt.IgnoreAspectRatio,
                                           QtCore.Qt.SmoothTransformation)
                coverLabel.setPixmap(QtGui.QPixmap.fromImage(coverImg))
                coverLabel.resize(200, 125) # 通过这个，做到完美缩放和分割!
                coverLabel.move((i%2+1) * 15 + i%2 * 200,
                                15 + self.winTitle.height() + int(i/2)*(125+2*20))
                self.covers.append(coverLabel)
        
            unameLabel = QtWidgets.QLabel(topFiller) # 昵称
            unameLabel.setText(room.uname)
            unameLabel.setStyleSheet('color: rgb(73,193,173);')
            unameLabel.setGeometry((i%2+1) * 15 + i%2 * 200,
                                   15+self.winTitle.height()+int(i/2)*(125+2*20)+125,
                                   200, 20)
            self.unames.append(unameLabel)

            titleLabel = QtWidgets.QLabel(topFiller) # 标题
            titleLabel.setText(room.title)
            titleLabel.setStyleSheet('color: rgb(214,157,133);')
            titleLabel.setGeometry((i%2+1) * 15 + i%2 * 200,
                                   15+self.winTitle.height()+int(i/2)*(125+2*20)+125+20,
                                   200, 20)
            self.titles.append(titleLabel)
            i += 1
        voicePlayer.play_music(r'source\RemindStandard.wav')
        self.show() # 更新完毕，显示窗口
        self.refreshThread.ifCheck = False  # 窗口未隐藏，不允许下次检测
        '''遗漏问题：若长期闲置不点【我知道了】，将一直不会开始下一次刷新，这不太好解决，建议记得点'''

    def mousePressEvent(self, QEvent):  # 记录按下位置
        self.mousePos = QEvent.pos()

    def mouseMoveEvent(self, QEvent):   # 鼠标拖动窗口
        goal = self.pos() + QEvent.pos() - self.mousePos
        deskSize = QtWidgets.QDesktopWidget().availableGeometry()
        if 0 < goal.x() < deskSize.width()-self.width() and 0 < goal.y() < deskSize.height() - self.height():
            self.move(goal) # 仅当不会移动到屏幕外时允许拖动


class AlermThread(QtCore.QThread):  # 提示线程
    liveRooms = QtCore.pyqtSignal(list)
    ifError = QtCore.pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.ifCheck = True # 是否允许检测
        self.rooms = []
        file = open(r'source\TanoshiList.txt', encoding='utf-8')
        i = 0
        for line in file:
            room = Room(int(line.split()[0]))   # 这样就可以允许在文件中使用注释
            self.rooms.append(room) # 文件读取到单推列表
            i += 1
            print('初始化第', i, '个主播')
        '''推测是由于在init未完成时使用emit的缘故，初次show窗口时内部无填充物，故放弃开幕雷击'''

    def run(self):
        while True:
            #（避免与init时的爬取发生冲突，sleep放最前）
            time.sleep(30)   # 隔一段时间后再检测，避免B站限流或主播网络波动引发的问题
            try:
                if self.ifCheck:
                    print(time.strftime("[%Y-%m-%d %H:%M:%S]开始检测", time.localtime()))
                    liveRooms = []  # 开播列表
                    for room in self.rooms:
                        if room.check():
                            liveRooms.append(room)
                    if len(liveRooms) > 0:  # 检测并打开提醒窗口
                        self.liveRooms.emit(liveRooms)
                    else:
                        print('没有新开播')
            except:
                self.ifError.emit(True)   # 发射错误信息
                print('查询开播线程-退出')
                break   # 结束线程
