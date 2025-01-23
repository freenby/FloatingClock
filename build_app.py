import PyInstaller.__main__
import os

# 确保图标文件存在
if not os.path.exists('clock_icon.ico'):
    print("正在创建图标文件...")
    exec(open('create_icon.py').read())

print("开始打包应用...")

PyInstaller.__main__.run([
    'clock.py',
    '--onefile',
    '--windowed',
    '--icon=clock_icon.ico',
    '--name=FloatingClock',
    '--add-data=clock_icon.ico;.',
    '--noconsole'
])

print("打包完成！") 