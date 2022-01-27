chcp 65001
pyinstaller -D -w -i ./source/Icon.ico ./HarukaPet.py
xcopy .\source\* .\dist\HarukaPet\source /e /i
xcopy .\private\* .\dist\HarukaPet\private /e /i
xcopy .\MouseStalker\* .\dist\HarukaPet\MouseStalker /e /i
ren .\dist\HarukaPet\HarukaPet.exe 豹宝.exe
