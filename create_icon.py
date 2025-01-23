from PIL import Image, ImageDraw
import os

# 创建一个 256x256 的图像
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# 绘制一个蓝色圆形作为时钟背景
circle_bbox = (20, 20, size-20, size-20)
draw.ellipse(circle_bbox, fill='blue')

# 绘制白色的时钟指针
center = size // 2
# 时针
draw.line([(center, center), (center, center-80)], fill='white', width=8)
# 分针
draw.line([(center, center), (center+60, center)], fill='white', width=6)

# 保存为 ICO 文件
image.save('clock_icon.ico', format='ICO') 