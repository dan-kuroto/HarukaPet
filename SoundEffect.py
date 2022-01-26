import json
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer


class Sound(QMediaPlayer):
    def __init__(self, name: str):
        super(Sound, self).__init__()
        self.setObjectName(name)

    def play_music(self, path: str):
        file = open(r'source\UserData.json', encoding='utf-8')
        data = json.load(file)
        file.close()
        if data[self.objectName()]:
            # self.pause()  # 下面会自动pause
            # 手动pause已经播放完的反而会出问题（并且无法用try捕获）
            url = QUrl.fromLocalFile(path)
            content = QMediaContent(url)
            self.setMedia(content)
            self.play()


voicePlayer = Sound('voice')   # 人声音轨
soundPlayer = Sound('sound')   # 音效音轨
# bgmPlayer = Sound('bgm')     # BGM播放音轨，在该项目中不需要


if __name__ == '__main__':  # 这里是标准用法
# 别的信号槽之类的不可信，只有在主动操作时才会激发，唯一可信的只有主动.position()查询，.duration()都没用
    from time import sleep
    app = QApplication(sys.argv)
    sound = Sound('test')
    sound.play_music(r'source\Move.wav')
    sleep(3)
    sound.play_music(r'source\Note.wav')
    sleep(3)
    # sys.exit(app.exec_())  # 不能阻塞，否则无法退出
