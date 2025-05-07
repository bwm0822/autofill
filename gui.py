import autofill as au
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import json
import os
import webbrowser

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    else:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def center_win(win, root):
    # ======= 視窗置中於主視窗 =======
    win.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    win_w = win.winfo_width()
    win_h = win.winfo_height()
    pos_x = root_x + (root_w - win_w) // 2
    pos_y = root_y + (root_h - win_h) // 2
    win.geometry(f"+{pos_x}+{pos_y}")

def center(root):
    # 更新視窗狀態，讓 Tkinter 計算完大小
    root.update_idletasks()

    # 取得實際寬高
    win_width = root.winfo_width()
    win_height = root.winfo_height()

    # 螢幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 計算置中位置
    x = int((screen_width - win_width) / 2)
    y = int((screen_height - win_height) / 2)

    # 設定位置但不改變大小
    root.geometry(f"+{x}+{y}")

    root.deiconify()  # 💋 再優雅地秀出視窗

def dict_sort(data):
    data_sorted = {'': ''}  # 保留空 key 在最前面
    data_sorted.update(dict(sorted(
        ((k, v) for k, v in data.items() if k),
        key=lambda item: item[0]
    )))
    return data_sorted

def gui():
    ph_birth = 'YYMMDD'
    ph_date = 'YYYY/MM/DD'
    ph_time = 'hh:mm:ss'
    key = ''
    tbl_user = {'':''}
    tbl_doctor = au.tbl_doc
    file_doctor = 'doctor.json'
    file_user = 'user.json'
    file_token = 'line.token'

    def open_win_user():
        win = tk.Toplevel(root)
        win.title("輸入資料")
        win.resizable(False, False)  # 不可調整大小
        win.transient()
        win.grab_set()

        # ======= 建立標籤與輸入框 =======
        tk.Label(win, text="姓　　名", anchor="e").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = tk.Entry(win)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, user_var.get())

        tk.Label(win, text="身分證號", anchor="e").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        id_entry = tk.Entry(win)
        id_entry.grid(row=1, column=1, padx=10, pady=5)
        id_entry.insert(0, id_var.get())

        tk.Label(win, text="生　　日", anchor="e").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        birth_entry = tk.Entry(win)
        birth_entry.grid(row=2, column=1, padx=10, pady=5)
        birth_entry.insert(0, birth_var.get() if birth_var.get() != ph_birth else '' )

        # ======= 建立按鈕區 =======
        def confirm():
            if name_entry.get():
                tbl_user[name_entry.get()] ={'身分證號':id_entry.get(),'生日':birth_entry.get()}
                comb_user.config(value=list(tbl_user.keys()))
                save_json(tbl_user, file_user)
                log('[新增]')
                log(f'姓　　名 : {name_entry.get()}')
                log(f'身分證號 : {id_entry.get()}')
                log(f'生　　日 : {birth_entry.get()}')
                win.destroy()
            else:
                log('[姓名]不可為空!!!')

        # 使用 Frame 包裹按鈕，並靠右排列
        tk.Button(win, text="確認", width=10, command=confirm).grid(row=3, column=1, pady=10, padx=10, sticky='e')

        center_win(win, root)

    def open_win_doctor():
        win = tk.Toplevel(root)
        win.title("輸入資料")
        win.resizable(False, False)  # 不可調整大小
        win.transient()
        win.grab_set()

        # ======= 建立標籤與輸入框 =======
        tk.Label(win, text="醫師姓名", anchor="e").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = tk.Entry(win)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        name_entry.insert(0, doctor_var.get().split('-')[0])

        tk.Label(win, text="醫師代號", anchor="e").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        did_entry = tk.Entry(win)
        did_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        did_entry.insert(0, drcode_var.get())

        tk.Label(win, text="院　　區", anchor="e").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        comb_area = ttk.Combobox(win, values=list(au.tbl_area.keys()))
        comb_area.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        comb_area.set(area_var.get())

        # ======= 建立按鈕區 =======
        def confirm():
            if name_entry.get():
                id = f"{name_entry.get()}-{comb_area.get()}"
                nonlocal tbl_doctor
                tbl_doctor[id] = {'醫師代號':did_entry.get(),'院區':comb_area.get()}
                tbl_doctor = dict_sort(tbl_doctor)
                comb_doctor.config(value=list(tbl_doctor.keys()))
                save_json(tbl_doctor, file_doctor)
                log('[新增]')
                log(f'醫師姓名 : {name_entry.get()}')
                log(f'醫師代號 : {did_entry.get()}')
                log(f'院　　區 : {comb_area.get()}')
                win.destroy()
            else:
                log('[醫師姓名]不可為空!!!')

        # 使用 Frame 包裹按鈕，並靠右排列
        tk.Button(win, text="確認", width=10, command=confirm).grid(row=3, column=1, pady=10, padx=10, sticky='e')

        center_win(win, root)

    def show_help():
        help_win = tk.Toplevel()
        help_win.title("使用說明")
        # help_win.geometry("420x300")
        help_win.resizable(False, False)
        help_win.transient()
        help_win.grab_set()

        # 文字區塊容器
        content = tk.Frame(help_win, padx=20, pady=20)
        content.pack(fill="both", expand=True)

        # 一般說明
        tk.Label(content, text="""1. 如何取得[醫師代號]
    到馬偕醫院網站首頁，選[科別掛號]，選取科別，
    醫師姓名下面的號碼就是[醫師代號]""", anchor="w", justify="left").pack(anchor="w")
        tk.Label(content, text="""2. 如何啟用[LINE通知]的功能
    取得 LINE 的 Token，將 Token 存於 line.token，
    與執行檔置於同路徑，執行檔執行時會自動讀取""", anchor="w", justify="left").pack(anchor="w")
        
        # 超連結樣式
        default_font  = tkfont.nametofont("TkDefaultFont")
        df= default_font.actual()
        # print("預設字型設定：", df)
        link_font = tkfont.Font(underline=False,size=df['size'],family=df['family'])
        link_label = tk.Label(content, text="""     （如何取得 LINE 的 Token）""", fg="blue", cursor="hand2", font=link_font)
        link_label.pack(anchor="w")
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://bwm0822.github.io/doc/auto_registered.html#line"))

        tk.Label(content, text="""3. 新增的[用戶]、[醫師代號]等資訊會存於執行檔
    同路徑的 user.json、doctor.json""", anchor="w", justify="left").pack(anchor="w")
        tk.Label(content, text="""4. 如果[日期]空白，會尋找第一個可掛號的日期""", anchor="w", justify="left").pack(anchor="w")
        tk.Label(content, text="""5. 按[測試]可以用來驗證你的輸入是否正確，
    如果是正確無誤，就可以連上醫師掛號的頁面""", anchor="w", justify="left").pack(anchor="w")
        tk.Label(content, text="""6. [測試]會顯示網頁，[送出]不會顯示網頁""", anchor="w", justify="left").pack(anchor="w")

        # 空行
        tk.Label(content, text="").pack()

        

        center_win(help_win, root)

    def add_placeholder(entry, placeholder):
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='gray')

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
            entry.config(fg='black')

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg='gray')

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def on_user_change(event):
        val = tbl_user[comb_user.get()]
        if '身分證號' in val: id_var.set(val['身分證號'])
        else: id_var.set(value='')
        if '生日' in val: birth_var.set(val['生日']); birth_entry.config(fg='black')
        else: birth_var.set(value='')

    def on_doctor_change(event):
        val = tbl_doctor[comb_doctor.get()]
        if '醫師代號' in val: drcode_var.set(val['醫師代號'])
        else: drcode_var.set(value='')
        if '院區' in val: area_var.set(val['院區'])

    def submit_form(test=False):
        clear()
        form = {
            # "用戶": user_var.get(),
            "院區": area_var.get(),
            "醫師代號": drcode_var.get(),
            "身分證號": id_var.get(),
            "生日": birth_var.get() if birth_var.get() != ph_birth else '',
            "診別": visit_var.get(),
            "日期": date_var.get() if date_var.get() != ph_date else '',
            "時段": segment_var.get(),
            "提交時間": time_var.get() if time_var.get() != ph_time else '',
            "LINE通知": notify_var.get()
        }

        lut = {"院區":"院　　區","醫師代號":"醫師代號","身分證號":"身分證號","生日":"生　　日",
               "診別":"診　　別","日期":"日　　期","時段":"時　　段","提交時間":"提交時間",
               "LINE通知":"LINE通知","Token":"   Token"}

        # form['Token'] = '無' if token is None else '有'

        for key, value in form.items():
            if key in lut:
                log(f"{lut[key]} : {value}")
        
        au.add_url(form)
        au.gui_log = log
        au.gui_key = get_key
        set_key('')

        threading.Thread(target=au.registered, args=(form,token), kwargs={'test':test}).start()

        btn_submit.config(state="disabled")
        btn_test.config(state="disabled")
        btn_clear.config(state="disabled")
        btn_help.config(state="disabled")

    def log(*args, **kwargs):
        end = kwargs['end'] if 'end' in kwargs else None
        msg = " ".join(str(arg) for arg in args)

        if any(word in msg for word in ('[取消]', '[結束]','[測試結束]')): 
            btn_submit.config(state="normal")
            btn_test.config(state="normal")
            btn_clear.config(state="normal")
            btn_help.config(state="normal")

        if end != '\r':
            log_text.insert("end", f"{msg}\n")
            log_text.see("end")
        else:
            last_line = int(log_text.index("end-1c").split(".")[0]) # 取得最後一行行號
            log_text.delete(f"{last_line}.0", f"{last_line}.end")   # 刪除最後一行內容
            log_text.insert(f"{last_line}.0", msg)  # 插入新訊息
            # log_text.see("end")   # 自動捲動到底部
            
    def clear():
        log_text.delete("1.0", tk.END)

    def cancel():
        set_key('q')

    def get_key():
        return key
    
    def set_key(value):
        nonlocal key  # 這樣會修改外層的 key 變數
        key = value

    def del_user():
        sel = user_var.get()
        if sel == '': return
        if tbl_user.pop(sel, None): 
             comb_user.config(value=list(tbl_user.keys()))
             save_json(tbl_user, file_user)
        log(f'[刪除] {user_var.get()}')

    def del_doctor():
        sel = doctor_var.get()
        if sel == '': return
        if tbl_doctor.pop(sel, None): 
             comb_doctor.config(value=list(tbl_doctor.keys()))
             save_json(tbl_doctor, file_doctor)
        log(f'[刪除] {doctor_var.get()}') 

    root = tk.Tk()
    root.withdraw()  # 💄 先隱藏視窗
    root.title("馬偕醫院掛號小幫手(v1.2)")
    
    # 建立主要內容框，加上邊緣空間 padding
    frame = tk.Frame(root, padx=20, pady=20)  # ⬅ 四周邊距
    frame.pack(fill="both", expand=True)
    # frame.grid(row=0, column=0, sticky="nsew")

    # 欄位變數
    user_var = tk.StringVar()
    area_var = tk.StringVar(value="淡水")
    doctor_var = tk.StringVar()
    drcode_var = tk.StringVar()
    id_var = tk.StringVar()
    birth_var = tk.StringVar()
    visit_var = tk.StringVar(value="複診")
    date_var = tk.StringVar()
    segment_var = tk.StringVar(value="不限")
    time_var = tk.StringVar(value='00:00:01')
    notify_var = tk.StringVar(value="否")

    birth_entry = tk.Entry(frame, textvariable=birth_var)
    add_placeholder(birth_entry, ph_birth)
    date_entry = tk.Entry(frame, textvariable=date_var)
    add_placeholder(date_entry, ph_date)
    time_entry = tk.Entry(frame, textvariable=time_var)
    add_placeholder(time_entry, ph_time)

    # [用戶] 欄位
    frame_user_add = tk.Frame(frame)
    user_add = tk.Button(frame_user_add, text="新增", command=lambda: open_win_user())
    user_add.pack(side="left",pady=0, padx=20)
    user_del = tk.Button(frame_user_add, text="刪除", command=lambda: del_user())
    user_del.pack(side="right",pady=0, padx=20)
    comb_user = ttk.Combobox(frame, textvariable=user_var, values=list(tbl_user.keys()), state="readonly")
    comb_user.bind("<<ComboboxSelected>>", on_user_change)

    # [醫師] 欄位
    frame_doctor = tk.Frame(frame)
    tk.Entry(frame_doctor, textvariable=drcode_var, width=6).pack(side='left')
    comb_doctor = ttk.Combobox(frame_doctor, textvariable=doctor_var, width=14, values=list(tbl_doctor.keys()), state="readonly")
    comb_doctor.bind("<<ComboboxSelected>>", on_doctor_change)
    comb_doctor.pack(side='right')
    frame_doctor_add = tk.Frame(frame)
    doctor_add = tk.Button(frame_doctor_add, text="新增", command=lambda: open_win_doctor())
    doctor_add.pack(side="left",pady=0, padx=20)
    doctor_del = tk.Button(frame_doctor_add, text="刪除", command=lambda: del_doctor())
    doctor_del.pack(side="right",pady=0, padx=20)

    fields = [
        ("用　　戶", comb_user, frame_user_add),
        ("院　　區", ttk.Combobox(frame, textvariable=area_var, values=list(au.tbl_area.keys()), state="readonly"), ""),
        ("醫師代號", frame_doctor, frame_doctor_add),
        ("身分證號", tk.Entry(frame, textvariable=id_var), ""),
        ("生　　日", birth_entry, ""),
        ("診　　別", ttk.Combobox(frame, textvariable=visit_var, values=["初診", "複診"], state="readonly"), ""),
        ("日　　期", date_entry, "[空白]代表不限日期"),
        ("時　　段", ttk.Combobox(frame, textvariable=segment_var, values=list(au.tbl_segemnt.keys()), state="readonly"), ""),
        ("提交時間", time_entry, "[空白]代表立刻提交"),
        ("LINE通知", ttk.Combobox(frame, textvariable=notify_var, values=["是", "否"], state="readonly"), ""),
    ]

    # 排列欄位
    for i, (label, widget, comb) in enumerate(fields):
        tk.Label(frame, text=label, anchor="e", width=7).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        widget.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        if isinstance(comb, str):
            tk.Label(frame, text=comb, anchor="w", width=15).grid(row=i, column=2, padx=5, pady=5, sticky="w")
        else:
            comb.config(width=15)
            comb.grid(row=i, column=2, padx=5, pady=5, sticky="w")

    frame.grid_columnconfigure(1, weight=1) #當視窗寬度變大時，第 1 欄的 widgets 會根據這個設定「彈性地拉長」來填滿空間。

    # 提交按鈕
    btn_cancel = tk.Button(frame, text="取消", command=cancel)
    btn_cancel.grid(row=len(fields), column=0, pady=0, padx=0, sticky="")

    btn_frame = tk.Frame(frame)
    btn_frame.grid(row=len(fields), column=1, pady=0, padx=0, sticky="ew")
    btn_test = tk.Button(btn_frame, text="測試", command=lambda: submit_form(test=True))
    btn_test.pack(side='left',padx=10)
    btn_clear = tk.Button(btn_frame, text="清除 log", command=lambda: clear())
    btn_clear.pack(side='left',padx=10)
    btn_help = tk.Button(btn_frame, text="說明", command=lambda: show_help())
    btn_help.pack(side='left',padx=10)

    btn_submit = tk.Button(frame, text="送出", command=lambda: submit_form())
    btn_submit.grid(row=len(fields), column=2, pady=0, padx=0, sticky="")

    # log 區域
    frame_log = tk.Frame(frame)
    frame_log.grid(row=len(fields)+1, column=0, columnspan=3, sticky="ew", padx=0, pady=10)

    log_text = tk.Text(frame_log, height=8, wrap="word", width=10)
    log_text.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame_log, command=log_text.yview)
    scrollbar.pack(side="right", fill="y")

    log_text.config(yscrollcommand=scrollbar.set)

    center(root)

    data = load_json(file_user)
    if data is not None: 
        tbl_user = data; comb_user['value'] = list(tbl_user.keys())
        log(f'載入 [{file_user}]')
    else: log(f'沒找到 [{file_user}]')

    data = load_json(file_doctor)
    if data is not None: 
        tbl_doctor = data; comb_doctor['values'] = list(tbl_doctor.keys())
        log(f'載入 [{file_doctor}]')
    else: log(f'沒找到 [{file_doctor}]')

    token = au.file_to_str(file_token)
    if token is not None: log(f'載入 [{file_token}]')
    else: log(f'沒找到 [{file_token}]')

    root.mainloop()


if __name__ == "__main__":
    gui()