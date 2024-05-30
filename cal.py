import tkinter as tk
import tkinter.ttk as ttk
def calculator_command():

    global input_var
    windows_calculator = tk.Tk()
    windows_calculator.title('计算器')
    windows_calculator.geometry('400x300+200+200')

    # 初始化输入变量和输入框
    input_var = tk.StringVar()
    input_var.set('')  # 设置初始值为空
    ttk.Entry(windows_calculator, justify=tk.LEFT, textvariable=input_var, font="Serif 113 bold").pack(fill=tk.BOTH,
                                                                                                       padx=6, pady=6)

    # 按钮框架
    fm1 = ttk.Frame(windows_calculator)
    fm1.pack(fill=tk.BOTH)

    # 创建等号和清除按钮
    ttk.Button(fm1, text='=', width=13, command=calculate).grid(row=3, column=3, padx=2, pady=2)
    ttk.Button(fm1, text='清除', width=13, command=clear).grid(row=0, column=1, padx=2, pady=2)

    # 创建数字按钮
    for i in range(3):
        for j in range(3):
            btn_id = str(1 + i * 3 + j)
            ttk.Button(fm1, text=btn_id, width=13, command=lambda s=btn_id: click(s)).grid(row=i + 1, column=j, padx=2,
                                                                                          pady=2)

    ttk.Button(fm1, text='0', width=13, command=lambda: click('0')).grid(row=3, column=0, padx=2, pady=2)
    ttk.Button(fm1, text='+', width=13, command=lambda: click('+')).grid(row=0, column=2, padx=2, pady=2)
    ttk.Button(fm1, text='-', width=13, command=lambda: click('-')).grid(row=0, column=3, padx=2, pady=2)
    ttk.Button(fm1, text='*', width=13, command=lambda: click('*')).grid(row=1, column=3, padx=2, pady=2)
    ttk.Button(fm1, text='/', width=13, command=lambda: click('/')).grid(row=2, column=3, padx=2, pady=2)

    windows_calculator.mainloop()

def click(opcode):
    input_var.set(input_var.get() + opcode)

def calculate():
    global input_var
    try:
        result = str(eval(input_var.get()))
        input_var.set(result)
    except:
        input_var.set('ERROR')

def clear():
    global input_var
    input_var.set('')

def m_to_h(minutes):
    return minutes/60
print(m_to_h((300)))
