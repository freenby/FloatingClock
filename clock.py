import tkinter as tk
from tkinter import colorchooser
from datetime import datetime
import pyttsx3
import threading
import time
import sys

class FloatingClock:
    def __init__(self):
        try:
            self.root = tk.Tk()
            # 设置初始位置在屏幕中央
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 200) // 2
            y = (screen_height - 50) // 2
            
            self.root.overrideredirect(True)
            self.root.attributes('-topmost', True)
            
            # 设置窗口大小和位置
            self.root.configure(bg='blue')
            self.root.geometry(f'200x50+{x}+{y}')
            
            # 创建时间标签
            self.time_label = tk.Label(
                self.root,
                font=('Arial', 20),
                bg='blue',
                fg='white',
                text="初始化中..."  # 添加初始文本
            )
            self.time_label.pack(expand=True)
            
            # 绑定鼠标事件
            self.root.bind('<Button-1>', self.save_click_pos)
            self.root.bind('<B1-Motion>', self.drag_window)
            self.root.bind('<Button-3>', self.show_menu)
            self.root.bind('<Escape>', lambda e: self.root.quit())  # 添加ESC键退出
            
            # 创建右键菜单
            self.menu = tk.Menu(self.root, tearoff=0)
            
            # 创建语音报时子菜单
            self.voice_menu = tk.Menu(self.menu, tearoff=0)
            self.menu.add_cascade(label='语音报时', menu=self.voice_menu)
            
            # 添加语音报时选项
            self.voice_mode = tk.StringVar(value='work')  # 修改默认值为 'work'
            self.voice_menu.add_radiobutton(
                label='关闭报时',
                variable=self.voice_mode,
                value='off',
                command=self.update_voice_mode
            )
            self.voice_menu.add_radiobutton(
                label='工作时间报时(9:00-15:00)',
                variable=self.voice_mode,
                value='work',
                command=self.update_voice_mode
            )
            self.voice_menu.add_radiobutton(
                label='全天报时',
                variable=self.voice_mode,
                value='all',
                command=self.update_voice_mode
            )
            
            # 添加颜色选择菜单项
            self.menu.add_command(label='更改背景颜色', command=self.choose_bg_color)
            self.menu.add_command(label='更改数字颜色', command=self.choose_text_color)
            
            # 创建字体亮度子菜单
            self.brightness_menu = tk.Menu(self.menu, tearoff=0)
            self.menu.add_cascade(label='字体亮度', menu=self.brightness_menu)
            
            # 添加字体亮度选项
            brightness_options = {
                '超亮': '#FFFFFF',  # 纯白色
                '明亮': '#E0E0E0',  # 亮灰色
                '适中': '#C0C0C0',  # 中灰色
                '柔和': '#A0A0A0',  # 暗灰色
                '暗淡': '#808080'   # 灰色
            }
            for label, color in brightness_options.items():
                self.brightness_menu.add_command(
                    label=label,
                    command=lambda c=color: self.set_font_brightness(c)
                )
            
            # 创建透明度子菜单
            self.transparency_menu = tk.Menu(self.menu, tearoff=0)
            self.menu.add_cascade(label='透明度', menu=self.transparency_menu)
            
            # 添加透明度选项
            transparencies = {
                '不透明': 1.0,
                '90%': 0.9,
                '75%': 0.75,
                '50%': 0.5,
                '25%': 0.25
            }
            for label, alpha in transparencies.items():
                self.transparency_menu.add_command(
                    label=label,
                    command=lambda a=alpha: self.set_transparency(a)
                )
            
            # 添加分隔线和退出选项
            self.menu.add_separator()
            self.menu.add_command(label='退出', command=self.root.quit)
            
            # 保存当前的背景色和文字色
            self.bg_color = 'blue'
            self.fg_color = '#FFFFFF'  # 默认使用最亮的白色
            
            # 初始化语音引擎
            self.engine = pyttsx3.init()
            
            # 启动语音报时线程
            self.voice_thread = threading.Thread(target=self.voice_time_check, daemon=True)
            self.voice_thread.start()
            
            # 启动时钟更新
            self.update_clock()
            
            print("时钟初始化完成")
            
        except Exception as e:
            print(f"初始化错误: {e}")
            sys.exit(1)

    def save_click_pos(self, event):
        self.x = event.x
        self.y = event.y

    def drag_window(self, event):
        x = self.root.winfo_x() + event.x - self.x
        y = self.root.winfo_y() + event.y - self.y
        self.root.geometry(f'+{x}+{y}')

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def update_clock(self):
        try:
            current_time = datetime.now()
            # 将秒和毫秒分开显示，中间添加空格，毫秒只保留2位
            time_str = current_time.strftime('%H:%M:%S')  # 时分秒
            ms_str = current_time.strftime('%f')[:2]      # 毫秒（只取前2位）
            display_time = f"{time_str}    {ms_str}"      # 使用4个空格分隔
            
            self.time_label.configure(text=display_time)
            self.root.after(1, self.update_clock)
        except Exception as e:
            print(f"更新时钟错误: {e}")

    def update_voice_mode(self):
        """更新语音报时模式"""
        print(f"语音报时模式已更改为: {self.voice_mode.get()}")
    
    def voice_time_check(self):
        """语音报时检查线程"""
        last_announce = None  # 记录上次报时的时间
        
        while True:
            try:
                now = datetime.now()
                current_mode = self.voice_mode.get()
                
                # 只在分钟为0或30时报时
                if now.minute in [0, 30]:
                    # 生成当前时间的唯一标识
                    current_time_id = f"{now.hour}:{now.minute}"
                    
                    # 避免重复报时
                    if current_time_id != last_announce:
                        should_announce = False
                        
                        if current_mode == 'work':
                            # 工作时间模式：9:00-15:00
                            # 修改判断条件，15点后不再报时
                            if 9 <= now.hour < 15 or (now.hour == 15 and now.minute == 0):
                                should_announce = True
                        elif current_mode == 'all':
                            # 全天模式：0:00-24:00
                            should_announce = True
                            
                        if should_announce:
                            time_str = now.strftime('%H:%M')
                            self.engine.say(f'现在时间是{time_str}')
                            self.engine.runAndWait()
                            last_announce = current_time_id
                            
                time.sleep(1)  # 每秒检查一次
                
            except Exception as e:
                print(f"语音报时错误: {e}")
                time.sleep(5)  # 发生错误时等待5秒再重试

    def set_transparency(self, alpha):
        """设置窗口透明度"""
        try:
            self.root.attributes('-alpha', alpha)
        except Exception as e:
            print(f"设置透明度错误: {e}")

    def set_font_brightness(self, color):
        """设置字体亮度"""
        try:
            self.fg_color = color
            self.time_label.configure(fg=self.fg_color)
        except Exception as e:
            print(f"设置字体亮度错误: {e}")

    def choose_bg_color(self):
        """选择背景颜色"""
        try:
            color = colorchooser.askcolor(
                title='选择背景颜色',
                color=self.bg_color
            )
            
            if color[1]:
                self.bg_color = color[1]
                # 更新窗口和标签的背景色
                self.root.configure(bg=self.bg_color)
                self.time_label.configure(bg=self.bg_color)
                
        except Exception as e:
            print(f"选择背景颜色错误: {e}")

    def choose_text_color(self):
        """选择数字颜色"""
        try:
            color = colorchooser.askcolor(
                title='选择数字颜色',
                color=self.fg_color
            )
            
            if color[1]:
                self.fg_color = color[1]
                self.time_label.configure(fg=self.fg_color)
                
        except Exception as e:
            print(f"选择数字颜色错误: {e}")

    def run(self):
        try:
            print("开始运行时钟...")
            self.root.mainloop()
        except Exception as e:
            print(f"运行错误: {e}")

if __name__ == '__main__':
    try:
        print("正在启动时钟程序...")
        clock = FloatingClock()
        clock.run()
    except Exception as e:
        print(f"程序启动失败: {e}") 