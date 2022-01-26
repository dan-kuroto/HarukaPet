"""用来把正方形的图片割成圆形带黑色边框有透明背景的图，省得一张一张搞PS"""
from os import system
from PIL import Image as Image


def transparent(img: Image, W: int, H: int, L: int):
    if W != H: raise Exception('这张图片不是正方形的！')
    R = W / 2
    for x in range(W):
        if x % 10 == 0: print('{0:.2f}%\r'.format((x + 1) / W * 100), end='')
        for y in range(H):
            if (x - R) ** 2 + (y - R) ** 2 > R ** 2:
                img.putpixel((x, y), (255, 255, 255, 0))
            elif (x - R) ** 2 + (y - R) ** 2 > (R - L * R) ** 2:
                img.putpixel((x, y), (0, 0, 0, 255))
    print('100.00%')


if __name__ == '__main__':
    src_path = './Haruka-3a.png'
    save_path = ['./Haruka-3', '.png']
    L = 0.02

    img = Image.open(src_path)
    img = img.convert('RGBA')
    W, H = img.size
    transparent(img, W, H, L)
    img.save(save_path[0] + save_path[1])
# 以下内容是为了把图变小但对png似乎反而会变大，算了，直接存吧
#    img.save(save_path[0] + '-tmp' + save_path[1])

#    system(f'ffmpeg -i "{save_path[0] + "-tmp" + save_path[1]}" -pred mixed "{save_path[0] + save_path[1]}"')  # 过一遍ffmpeg把图变小点
#    system(f'del "{save_path[0] + "-tmp" + save_path[1]}"')  # 删除临时文件
