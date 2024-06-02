import time
import datetime
import psutil
from pynput import mouse, keyboard
import tkinter.ttk as ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import os
from PIL import Image, ImageDraw, ImageFont
import cal
import hashlib
import random
import requests
import time
########################################################################################


# 日志变量s
diary = "日志.txt"
def log_event(event):
    with open(diary, "a") as f:
        f.write(f"{event} at {datetime.datetime.now()}\n")

def record_login():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    log_event(f"System booted up")

def record_logout():
    log_event(f"System shutting down")

def on_active():
    global last_active
    last_active = time.time()

def on_free():
    log_event(f"System free at {datetime.datetime.now()}")

def on_move(x, y):
    on_active()

def on_click(x, y, button, pressed):
    on_active()

def on_scroll(x, y, dx, dy):
    on_active()

def on_press(key):
    on_active()

def on_release(key):
    on_active()


##############################################################################################################


# 日志生成主函数
def diary_main():
    last_active = time.time()
    # 鼠标监听启动
    mouse_listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll)
    mouse_listener.start()
    # 键盘监听启动
    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    keyboard_listener.start()

    try:
        record_login()
        while True:
            time.sleep(60)  # 每隔60秒检查一次
            if time.time() - last_active > 300:  # 5分钟无活动
                on_free()
                last_active = time.time()  # 重新记录活跃时间
    except KeyboardInterrupt:
        record_logout()
        mouse_listener.stop()
        keyboard_listener.stop()

# 分析日志内容并给出 字典数据
def parse_log(log_file):
    database = {}
    with open(log_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.split("at")
        event = parts[0].strip()
        timestamp = parts[1].strip()

        # 考虑秒的小数部分
        datetime_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

        date = timestamp.split()[0]
        time = timestamp.split()[1]

        if date not in database:
            database[date] = {'boot': [], 'free': [], 'shutdown': []}

        if "booted up" in event:
            database[date]['boot'].append(datetime_obj)
        elif "free" in event:
            database[date]['free'].append(datetime_obj)
        elif "shutting down" in event:
            database[date]['shutdown'].append(datetime_obj)

    return database

# 分析字典数据
def analyze_database(usage):
    for date, events in usage.items():
        print(f"使用日期: {date}")

        boot_time = events['boot'][0] if events['boot'] else None
        shutdown_time = events['shutdown'][-1] if events['shutdown'] else None

        if boot_time:
            print(f"  启动时间: {boot_time.time()}")
        if shutdown_time:
            print(f"  关闭时间: {shutdown_time.time()}")

        total_free_time = 0
        if events['free']:
            total_free_time = sum(
                [(events['free'][i] - events['free'][i - 1]).total_seconds() for i in range(1, len(events['free']))])
            print(f"  闲暇总时间: {total_free_time // 60} minutes")

        if boot_time and shutdown_time:
            total_active_time = (shutdown_time - boot_time).total_seconds() - total_free_time
            print(f"  活跃总时间: {total_active_time // 60} minutes")
        print()
    with open("分析结果.txt", "w") as file:
        for date, events in usage.items():
            file.write(f"使用日期: {date}\n")

            boot_time = events['boot'][0] if events['boot'] else None
            shutdown_time = events['shutdown'][-1] if events['shutdown'] else None

            if boot_time:
                file.write(f"  启动时间: {boot_time.time()}\n")
            if shutdown_time:
                file.write(f"  关闭时间: {shutdown_time.time()}\n")

            total_free_time = 0
            if events['free']:
                total_free_time = sum(
                    [(events['free'][i] - events['free'][i - 1]).total_seconds() for i in
                     range(1, len(events['free']))])
                file.write(f"  闲暇总时间: {total_free_time // 60} 分钟 / {cal.m_to_h(total_free_time // 60)} 小时\n")

            if boot_time and shutdown_time:
                total_active_time = (shutdown_time - boot_time).total_seconds() - total_free_time
                file.write(f"  活跃总时间: {total_active_time // 60} 分钟 / {cal.m_to_h(total_active_time//60)} 小时\n")
            file.write("\n")

# 分析主函数
def analyz_main():
    diary = "日志.txt"
    database = parse_log(diary)
    analyze_database(database)
    show_text_file_content('分析结果')

# 日志显示
def diary_show():
    show_text_file_content('日志')


##############################################################################################################


# 批量修改扩展名
def rename_file_extensions(directory, old_extension, new_extension):
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(old_extension):
                old_file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, file[:-len(old_extension)] + new_extension)
                try:
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed: {old_file_path} -> {new_file_path}")
                except Exception as e:
                    print(f"Error renaming file {old_file_path}: {e}")

# 批量删除同一种扩展名文件
def delete_files(directory, file_type):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_type):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

# 为图片添加水印
def add_watermark(directory, watermark_text):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_path = os.path.join(root, file)
                try:
                    image = Image.open(file_path).convert("RGBA")
                    txt = Image.new("RGBA", image.size, (255, 255, 255, 0))

                    # 使用默认字体
                    # 使用指定字体和大小
                    font = ImageFont.truetype("arial.ttf", 200)  # "arial.ttf" 是字体文件在font里不支持中文 simhei.tff可以，200字体大小
                    d = ImageDraw.Draw(txt)

                    bbox = d.textbbox((0, 0), watermark_text, font=font)
                    textwidth, textheight = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    width, height = image.size
                    x, y = width - textwidth - 10, height - textheight - 10

                    d.text((x, y), watermark_text, fill=(255, 255, 255, 500), font=font)

                    watermarked = Image.alpha_composite(image, txt)
                    watermarked = watermarked.convert("RGB")  # 去掉 alpha 通道
                    watermarked.save(file_path)
                    print(f"Watermarked: {file_path}")
                except Exception as e:
                    print(f"Error adding watermark to {file_path}: {e}")

# 文件批处理命令
def file_batch_processing():
    # 创建弹窗
    popup = tk.Toplevel()
    popup.title("文件批处理")
    popup.geometry("400x300")

    # 选项框架
    option_frame = ttk.Frame(popup)
    option_frame.pack(pady=10)

    # 选择操作标签
    option_label = ttk.Label(option_frame, text="选择操作:")
    option_label.pack(side=tk.LEFT, padx=5)

    # 操作选项下拉菜单
    option_var = tk.StringVar()
    option_menu = ttk.Combobox(option_frame, textvariable=option_var, values=["修改扩展名", "删除文件", "添加水印"])
    option_menu.pack(side=tk.LEFT, padx=5)

    # 输入框架
    input_frame = ttk.Frame(popup)
    input_frame.pack(pady=10)

    # 输入标签和输入框
    label1 = ttk.Label(input_frame, text="参数1:")
    label1.grid(row=0, column=0, padx=5, pady=5)
    entry1 = ttk.Entry(input_frame)
    entry1.grid(row=0, column=1, padx=5, pady=5)

    label2 = ttk.Label(input_frame, text="参数2:")
    label2.grid(row=1, column=0, padx=5, pady=5)
    entry2 = ttk.Entry(input_frame)
    entry2.grid(row=1, column=1, padx=5, pady=5)

    # 确认按钮
    confirm_button = ttk.Button(popup, text="确认",
                                command=lambda: execute_batch_operation(option_var.get(), entry1.get(), entry2.get()))
    confirm_button.pack(pady=10)

    # 禁用主窗口
    disable_main_window(popup)


##############################################################################################################

#日志弹窗展示和分析结果弹窗展示
def execute_batch_operation(option, param1, param2):
    directory = "修改"  # 替换为实际目录

    if option == "修改扩展名":
        old_extension = param1
        new_extension = param2
        rename_file_extensions(directory, old_extension, new_extension)
    elif option == "删除文件":
        file_type_to_delete = param1
        delete_files(directory, file_type_to_delete)
    elif option == "添加水印":
        watermark_text = param1
        add_watermark(directory, watermark_text)
def show_text_file_content(file):
    # 创建弹窗
    popup = tk.Toplevel()
    popup.title(file)
    popup.geometry("400x300")

    # 滚动文本框
    text_area = ScrolledText(popup, wrap='word', width=40, height=15)
    text_area.pack(expand=True, fill='both')

    # 关闭按钮
    close_button = ttk.Button(popup, text="关闭", command=popup.destroy)
    close_button.pack(pady=10)

    # 禁用主窗口
    disable_main_window(popup)

    # 读取并显示文件内容
    file_path = f'{file}.txt'  # 请将此路径替换为您的txt文件路径
    try:
        with open(file_path, 'r', encoding='gbk') as file:
            content = file.read()
            text_area.insert(tk.END, content)
    except FileNotFoundError:
        tk.messagebox.showerror("错误", f"文件 {file_path} 未找到")
        popup.destroy()
        root.attributes('-disabled', False)
def disable_main_window(popup):
    root.attributes('-disabled', True)
    popup.protocol("WM_DELETE_WINDOW", lambda: enable_main_window(popup))
def enable_main_window(popup):
    root.attributes('-disabled', False)
    popup.destroy()


##############################################################################################################


# 创建容器们
def creat_frame(root):
    global input_var, translate_i, translate_i1
    # 装载按钮的容器
    frame = ttk.Frame(root)
    # 分析日志按钮
    analyz_button = ttk.Button(frame, text='分析日志', command=analyz_main)
    analyz_button.pack(side=tk.LEFT)
    # 日志显示按钮
    diary_button = ttk.Button(frame, text='日志显示', command=diary_show)
    diary_button.pack(side=tk.LEFT)
    # 计算器按钮
    caculator_button = ttk.Button(frame, text='计算器', command=cal.calculator_command)
    caculator_button.pack(side=tk.LEFT)
    # 自动化脚本按钮
    scipts_button = ttk.Button(frame, text='文件批处理', command=file_batch_processing)
    scipts_button.pack(side=tk.LEFT)
    frame.pack(fill=tk.X)
    fm3 = ttk.Frame(root)
    fm3.pack(fill=tk.BOTH)
    tr_lb1 = ttk.Label(fm3, text='计算器', font="Serif 18 bold")
    tr_lb1.pack()

    # 翻译容器
    frame1 = ttk.Frame(root)

    # 输入文本框

    translate_i1 = tk.StringVar()
    translate_i = tk.StringVar()
    input_var = tk.StringVar()
    input_var.set('')  # 设置初始值为空
    ttk.Entry(root, justify=tk.LEFT, textvariable=input_var, font="Serif 18 bold").pack(fill=tk.BOTH, padx=6, pady=6)
    ##############################################################################################################
    #计算器部分
    # 按钮框架
    fm1 = ttk.Frame(root)
    fm1.pack(fill=tk.BOTH)

    # 创建等号,清除按钮和退格键
    ttk.Button(fm1, text='=', width=11, command=calculate).grid(row=0, column=1, padx=2, pady=2)
    ttk.Button(fm1, text='清除', width=11, command=clear).grid(row=3, column=3, padx=2, pady=2)
    ttk.Button(fm1, text='退格', width=11, command=backspace).grid(row=4, column=3, padx=2, pady=2)
    # 创建数字按钮
    for i in range(3):
        for j in range(3):
            btn_id = str(1 + i * 3 + j)
            ttk.Button(fm1, text=btn_id, width=11, command=lambda s=btn_id: click(s)).grid(row=i + 1, column=j, padx=2,
                                                                                           pady=2)

    ttk.Button(fm1, text='^', width=11, command=lambda: click('**')).grid(row=4, column=0, padx=2, pady=2)
    ttk.Button(fm1, text=')', width=11, command=lambda: click(')')).grid(row=4, column=2, padx=2, pady=2)
    ttk.Button(fm1, text='(', width=11, command=lambda: click('(')).grid(row=4, column=1, padx=2, pady=2)
    ttk.Button(fm1, text='0', width=11, command=lambda: click('0')).grid(row=0, column=0, padx=2, pady=2)
    ttk.Button(fm1, text='+', width=11, command=lambda: click('+')).grid(row=0, column=2, padx=2, pady=2)
    ttk.Button(fm1, text='-', width=11, command=lambda: click('-')).grid(row=0, column=3, padx=2, pady=2)
    ttk.Button(fm1, text='x', width=11, command=lambda: click('*')).grid(row=1, column=3, padx=2, pady=2)
    ttk.Button(fm1, text='/', width=11, command=lambda: click('/')).grid(row=2, column=3, padx=2, pady=2)

    ##############################################################################################################

    fm2 = ttk.Frame(root)
    fm2.pack(fill=tk.BOTH)
    tr_lb = ttk.Label(fm2, text='---------Calcu/Tran--------------', font="Serif 18 bold")
    tr_lb.pack()
    frame1 = ttk.Frame(root)


    translate_i1 = tk.StringVar()
    translate_i = tk.StringVar()
    # input_var = tk.StringVar()
    # input_var.set('')  # 设置初始值为空
    # ttk.Entry(root, justify=tk.LEFT, textvariable=input_var, font="Serif 18 bold").pack(fill=tk.BOTH, padx=6, pady=6)

    fm2 = ttk.Frame(root)
    fm2.pack(fill=tk.BOTH)
    tr_lb = ttk.Label(fm2, text='翻译', font="Serif 18 bold")
    tr_lb.pack()
    frame1.pack(fill=tk.X)
    input_entry = ttk.Entry(frame1, width=110, textvariable=translate_i)
    input_entry.pack()

    frame_translate = ttk.Frame(root)
    frame_translate.pack(fill=tk.BOTH)
    translate_button = ttk.Button(frame_translate, text='英译汉', command=translate_button_command)
    translate_button.pack(side=tk.LEFT)
    translate_button1 = ttk.Button(frame_translate, text='汉译英', command=translate_button1_command)
    translate_button1.pack(side=tk.RIGHT)

    frame_translate_result = ttk.Frame(root)
    frame_translate_result.pack(fill=tk.BOTH)
    out_label = ttk.Label(frame_translate_result, text='结果', font="Serif 18 bold")
    out_label.pack()
    out_entry = ttk.Entry(frame_translate_result, width=110, textvariable=translate_i1)
    out_entry.pack()
# 创建窗体
def creat_root(title):
    global root
    root = tk.Tk()
    root.title(title)
    root.geometry('350x500+700+300')
    creat_frame(root)
    root.mainloop()

#去计算器按钮命令
# 初始化输入变量
# def calculator_command():
#     global input_var
#     windows_calculator = tk.Tk()
#     windows_calculator.title('计算器')
#     windows_calculator.geometry('400x300+200+200')
#     # 初始化输入变量和输入框
#     input_var = tk.StringVar()
#     input_var.set('')  # 设置初始值为空
#     ttk.Entry(windows_calculator, justify=tk.LEFT, textvariable=input_var, font="Serif 18 bold").pack(fill=tk.BOTH, padx=6, pady=6)
#
#     # 按钮框架
#     fm1 = ttk.Frame(windows_calculator)
#     fm1.pack(fill=tk.BOTH)
#
#     # 创建等号和清除按钮
#     ttk.Button(fm1, text='=', width=8, command=calculate).grid(row=3, column=3, padx=2, pady=2)
#     ttk.Button(fm1, text='清除', width=8, command=clear).grid(row=0, column=1, padx=2, pady=2)
#
#     # 创建数字按钮
#     for i in range(3):
#         for j in range(3):
#             btn_id = str(1 + i * 3 + j)
#             ttk.Button(fm1, text=btn_id, width=8, command=lambda s=btn_id: click(s)).grid(row=i + 1, column=j, padx=2, pady=2)
#
#     ttk.Button(fm1, text='0', width=8, command=lambda: click('0')).grid(row=3, column=0, padx=2, pady=2)
#     ttk.Button(fm1, text='+', width=8, command=lambda: click('+')).grid(row=0, column=2, padx=2, pady=2)
#     ttk.Button(fm1, text='-', width=8, command=lambda: click('-')).grid(row=0, column=3, padx=2, pady=2)
#     ttk.Button(fm1, text='*', width=8, command=lambda: click('*')).grid(row=1, column=3, padx=2, pady=2)
#     ttk.Button(fm1, text='/', width=8, command=lambda: click('/')).grid(row=2, column=3, padx=2, pady=2)
#
#     windows_calculator.mainloop()

########################################################################################
print('^_^')#先保留上边代码防止出错


##############################################################################################################


# 计算器按钮点击功能函数# 点击增加字符
def click(opcode):
    global input_var
    input_var.set(input_var.get() + opcode)
# eval()计算总值=键
def calculate():
    global input_var
    try:
        result = str(eval(input_var.get()))
        input_var.set(result)
    except:
        input_var.set('ERROR')

# 清除键
def clear():
    global input_var
    input_var.set('')
# 退格键
def backspace():
    try:
        global input_var
        list_var = list(input_var.get())
        list_var.pop(len(list_var) - 1)
        input_var.set(''.join(list_var))
    except:
        input_var.set('别再按退格了')


##############################################################################################################
#翻译部分
# 翻译部分
def baidu_translate(query, from_lang='auto', to_lang='en', appid='your_appid', secret_key='your_secret_key'):
    api_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    salt = str(random.randint(32768, 65536))
    sign = appid + query + salt + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }

    response = requests.post(api_url, data=params, headers=headers)
    result = response.json()

    if 'trans_result' in result:
        return result['trans_result'][0]['dst']
    else:
        return result

def translate(x):
    global translate_i, translate_i1
    appid = '20240530002065825'  # App ID
    secret_key = 'nYGpoMhOYC_JerF9gYIJ'  # 密钥
    text_to_translate = translate_i.get()
    if x == 'zh':
        translated_text = baidu_translate(text_to_translate, from_lang='zh', to_lang='en', appid=appid, secret_key=secret_key)
    elif x == 'en':
        translated_text = baidu_translate(text_to_translate, from_lang='en', to_lang='zh', appid=appid, secret_key=secret_key)
    translate_i1.set(translated_text)
    print(f"Translated text: {translated_text}")

def translate_button_command():
    translate('en')

def translate_button1_command():
    translate('zh')

##############################################################################################################








# 主函数#
def main():
    creat_root('实用脚本v1.0---作者:徐学昊(19020232202429)')
    diary_main()
main()