import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets
from SoundEffect import voicePlayer


class TrayIcon(QtWidgets.QSystemTrayIcon):                      # 系统托盘
    def __init__(self, parent: 'HarukaPet.MainWindow'):
        super().__init__(parent)
        self.parent = parent                                    # 记录父窗口备用
        self.setIcon(QtGui.QIcon(QtGui.QPixmap(r'source\Icon.png')))
        self.icon = self.MessageIcon()
        self.setToolTip(
            'HarukaPet v1.0\n' +
            'vup白神遥的同人开源桌宠软件。\n' +
            '\n' +
            '她真可爱，我永远喜欢她。\n' +
            '　　　　——(作者)B站@坛黎斗'
        )
        self.activated.connect(self.activateEvent)

        self.aboutWindow = self.__init_about_window()

        self.menu = QtWidgets.QMenu()
        self.menuElems = []
        self.menuElems.append(QtWidgets.QAction('关于 HarukaPet', triggered=self.show_about))
        self.menu.addAction(self.menuElems[-1])
        self.menu.addSeparator()
        self.menuElems.append(QtWidgets.QAction('退出', triggered=self.appExit))
        self.menu.addAction(self.menuElems[-1])
        self.setContextMenu(self.menu)                          # 设置右键菜单
    
    def __init_about_window(self) -> QtWidgets.QWidget:
        """偷懒用面向过程实现的代价就是这个窗口不能拖动了，如果不是桌宠软件可以不加Qt.Tool就能拖了，或者面向对象重写鼠标事件"""
        about = QtWidgets.QWidget()
        about.resize(400, 250)
        about.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        about.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        about.setWindowFlag(QtCore.Qt.Tool)
        
        title = QtWidgets.QLabel('—— 关于 HarukaPet ——')
        title.setAlignment(QtCore.Qt.AlignCenter)
        text = QtWidgets.QTextBrowser()
        text.setReadOnly(True)
        text.append(    # 注意这鬼东西不支持html5，比如删除线用<del>是无效的
r'''
<p align="center" style="font-size: 20px;">HarukaPet v1.0</p>
<center style="font-size: 14px; color: grey;">psplive所属vup <a href="https://space.bilibili.com/477332594" title="Ta的个人空间" style="color: grey;">@白神遥Haruka</a> 的<strong>同人开源</strong>桌宠软件</center>
<hr>
<p style="font-size: 16px;">她真可爱，我永远喜欢她。</p>
<p align="right" style="font-size: 16px;">——(作者)B站<a href="https://message.bilibili.com/?spm_id_from=333.999.0.0#/whisper/mid142224411" title="给我提建议" style="color: black;">@坛黎斗</a></p>
<hr>
<p align="center" style="font-size: 18px;"><strong>鸣谢</strong></p>
<ul>
    <li><p style="font-size: 14px;">感谢<a href="https://github.com/zhimingshenjun/DD_Monitor" title="Github地址" style="color: black;">DD监控室</a>作者——B站<a href="https://space.bilibili.com/637783" title="Ta的个人空间" style="color: black;">@神君Channel</a>，是您开发的DD监控室带我入坑了PyQt5这个超好用的GUI库，我掌握的很多Python、PyQt5知识也是从您的项目中学到的。<span style="text-decoration: line-through;">DD监控室也给我摸鱼DD提供了巨大的帮助</span></p></li>
</ul>
'''
        )
        text.moveCursor(QtGui.QTextCursor.MoveOperation.Start)  # 就这一行破代码不知道浪费我多少时间……只能查到Qt有效资料，迁移到PyQt上太费劲
        text.setOpenLinks(False)
        text.anchorClicked.connect(self.about_link_clicked)
        hideBtn = QtWidgets.QPushButton('我知道了')
        hideBtn.clicked.connect(about.hide)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(hideBtn)
        about.setLayout(layout)

        return about
    
    def about_link_clicked(self, q_url: QtCore.QUrl):  # 在Qt里写html还真是一件麻烦的事情啊╮(╯▽╰)╭
        webbrowser.open(q_url.url())

    def show_about(self):
        voicePlayer.play_music(r'source\About.wav')
        self.aboutWindow.show()

    def activateEvent(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger and self.parent.isHidden():
            self.parent.show()
            voicePlayer.play_music(r'source\Hide.wav')

    def appExit(self):
        self.parent.hide()  # 这行别删，很重要，只有在所有人都hide的情况下close才能退出，别问为什么，我也不到

        voicePlayer.play_music(r'source\Exit.wav')
        self.aboutWindow.close()
        self.parent.noteWindow.close()
        self.parent.lifeWindow.close()
        self.parent.stalker.close()
        self.parent.close()

        # if voicePlayer.volume() != 0:  # 静音模式下就别浪费时间了——那是不行的，直接退出的话某几个线程来不及正常结束
        from time import sleep
        sleep(2)  # 只给两秒，放不完也不管了
