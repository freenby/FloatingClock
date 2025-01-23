import os
import subprocess
import PyInstaller.__main__
import time

def find_inno_setup():
    """查找 Inno Setup 编译器的路径"""
    # 使用确切的安装路径
    inno_path = r"d:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    if os.path.exists(inno_path):
        print(f"找到 Inno Setup 路径: {inno_path}")
        return inno_path
    
    return None

def check_environment():
    """检查环境和必要文件"""
    print("\n检查环境和必要文件...")
    
    # 检查目录结构
    directories = {
        'dist': os.path.exists('dist'),
        'output': os.path.exists('output')
    }
    
    for dir_name, exists in directories.items():
        print(f"目录 {dir_name}: {'✓' if exists else '✗'}")
        if not exists and dir_name == 'output':
            os.makedirs('output')
            print(f"已创建 {dir_name} 目录")
    
    # 检查必要文件
    required_files = {
        'clock.py': os.path.exists('clock.py'),
        'setup_script.iss': os.path.exists('setup_script.iss'),
        'clock_icon.ico': os.path.exists('clock_icon.ico'),
    }
    
    if os.path.exists('dist'):
        required_files['dist/FloatingClock.exe'] = os.path.exists('dist/FloatingClock.exe')
    
    for file_name, exists in required_files.items():
        print(f"文件 {file_name}: {'✓' if exists else '✗'}")
    
    return all(required_files.values()) and directories['dist']

def run_inno_setup(iscc_path, setup_script):
    """运行 Inno Setup 编译器"""
    try:
        # 使用 cmd.exe 运行命令
        cmd = f'cmd.exe /c """{iscc_path}""" """{setup_script}"""'
        print(f"执行命令: {cmd}")
        
        # 创建临时批处理文件
        batch_file = "compile_setup.bat"
        with open(batch_file, "w", encoding="utf-8") as f:
            f.write(f'@echo off\n')
            f.write(f'"{iscc_path}" "{setup_script}"\n')
            f.write('if errorlevel 1 exit /b %errorlevel%\n')
        
        print("运行编译脚本...")
        result = subprocess.run(
            batch_file,
            shell=True,
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )
        
        # 删除临时批处理文件
        try:
            os.remove(batch_file)
        except:
            pass
        
        # 检查返回码
        if result.returncode != 0:
            print("\nInno Setup 输出:")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
            raise Exception(f"Inno Setup 执行失败，返回码：{result.returncode}")
        
        return True
        
    except Exception as e:
        print(f"运行 Inno Setup 时出错: {e}")
        if hasattr(e, 'output'):
            print("输出:", e.output)
        return False

def build_exe():
    try:
        if not check_environment():
            print("环境检查失败，请确保所有必要文件都存在")
            return False
            
        print("\n第1步：创建图标...")
        if not os.path.exists('clock_icon.ico'):
            with open('create_icon.py', 'r', encoding='utf-8') as f:
                exec(f.read())
        
        time.sleep(1)
        
        if not os.path.exists('clock_icon.ico'):
            raise FileNotFoundError("图标文件创建失败！")
        else:
            print("图标文件创建成功：", os.path.abspath('clock_icon.ico'))
        
        print("\n第2步：打包应用...")
        icon_path = os.path.abspath('clock_icon.ico')
        
        PyInstaller.__main__.run([
            'clock.py',
            '--onefile',
            '--windowed',
            f'--icon={icon_path}',
            '--name=FloatingClock',
            f'--add-data={icon_path};.',
            '--noconsole'
        ])
        
        if not os.path.exists('dist/FloatingClock.exe'):
            raise FileNotFoundError("PyInstaller 打包失败，未生成 exe 文件")
        
        print("\n第3步：创建安装程序...")
        iscc_path = find_inno_setup()
        if not iscc_path:
            print("错误：未找到 Inno Setup，请先安装 Inno Setup！")
            print("您可以从这里下载：https://jrsoftware.org/isdl.php")
            return False
            
        print(f"找到 Inno Setup：{iscc_path}")
        
        try:
            setup_script = os.path.abspath("setup_script.iss")
            if not os.path.exists(setup_script):
                raise FileNotFoundError(f"找不到安装脚本文件：{setup_script}")
            
            # 确保所有必要文件存在
            required_files = {
                'dist/FloatingClock.exe': os.path.exists('dist/FloatingClock.exe'),
                'clock_icon.ico': os.path.exists('clock_icon.ico'),
                'setup_script.iss': os.path.exists('setup_script.iss')
            }
            
            missing_files = [f for f, exists in required_files.items() if not exists]
            if missing_files:
                raise FileNotFoundError(f"缺少必要文件: {', '.join(missing_files)}")
            
            # 创建输出目录
            output_dir = os.path.abspath('output')
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"运行 Inno Setup 编译器...")
            if not run_inno_setup(iscc_path, setup_script):
                return False
            
            expected_output = os.path.join(output_dir, 'FloatingClock_Setup.exe')
            if not os.path.exists(expected_output):
                raise FileNotFoundError(f"安装程序未生成：{expected_output}")
            
            print(f"\n成功生成安装程序：{expected_output}")
            return True
            
        except Exception as e:
            print(f"\n创建安装程序时出错: {e}")
            return False
            
    except Exception as e:
        print(f"\n错误：{str(e)}")
        return False

if __name__ == '__main__':
    print("开始打包过程...")
    print("当前工作目录：", os.getcwd())
    success = build_exe()
    
    if success:
        print("\n打包成功完成！")
    else:
        print("\n打包过程失败！")
        print("\n请确保已经安装了 Inno Setup：")
        print("1. 访问 https://jrsoftware.org/isdl.php")
        print("2. 下载并安装最新版本的 Inno Setup")
        print("3. 安装完成后重新运行此脚本") 