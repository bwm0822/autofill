from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import readchar
import time
import datetime
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import msvcrt  # Windows 專用
import json
import threading
import sys, os


''' 程式說明
功能    : 網頁自動填表格
參考文件 : https://steam.oxxostudio.tw/category/python/spider/selenium.html
'''

tbl_doc = {'':'',
            '丁瑋信-台北兒童':{'醫師代號':'55', '院區':'台北兒童'},
            '周宜德-淡水':{'醫師代號':'1072','院區':'淡水'}, 
            '張絜閔-淡水':{'醫師代號':'1114','院區':'淡水'},  
           }

tbl_area = {'台北':'tp', '台北兒童':'tp', '淡水':'ts', '新竹':'hc', '新竹兒童':'hc'}
tbl_segemnt = {'不限':0, '上午':1, '下午':2, '晚間':3}
gui_log = None
gui_key = None

if hasattr(sys, '_MEIPASS'): base_path = sys._MEIPASS
else: base_path = os.path.abspath(".")

def msg(*args, **kwargs):
    # print(args, kwargs)
    if gui_log: gui_log(*args, **kwargs)
    else: print(*args, **kwargs)

def key_pressed():
    if gui_key: return gui_key()
    elif msvcrt.kbhit(): return msvcrt.getwch()
    return None

def wait_schedule(target_time_str):
    # 設定目標時間（24小時制）
    target_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(target_time_str, "%H:%M:%S").time())

    # 如果現在時間超過了，那就等到隔天的同一時間
    now = datetime.datetime.now()
    if now >= target_time:
        target_time += datetime.timedelta(days=1)

    print(f"人家會等到 {target_time.strftime('%Y-%m-%d %H:%M:%S')} 再幫妳點唷♥")

    # Sexy 倒數～每秒秀出現在時間
    if gui_log: msg('提交時間:',target_time.strftime('%Y-%m-%d %H:%M:%S'))
    while datetime.datetime.now() < target_time:
        now = datetime.datetime.now()
        if gui_log: 
            msg('目前時間:',now.strftime('%Y-%m-%d %H:%M:%S'), end="\r", flush=True)
        else: 
            msg("按'q'離開，", '提交時間:', target_time.strftime('%Y-%m-%d %H:%M:%S'), '目前時間:', now.strftime("%Y-%m-%d %H:%M:%S"), end="\r", flush=True)

        key = key_pressed()
        if key == 'q':
            msg('\n[取消]')
            return False
        time.sleep(1)

    print("\n時間到囉～人家開始動作囉😍")
    return True

def push_line_message(token, message, user_id):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text","text": message}]
    }
    r = requests.post(url, headers=headers, json=data)
    print(r.status_code, r.text)

def broadcast_line_message(token, message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "messages": [{"type": "text","text": message}]
    }
    r = requests.post(url, headers=headers, json=data)
    print(r.status_code, r.text)

def multicast_line_message(token, message, user_ids):
    url = 'https://api.line.me/v2/bot/message/multicast'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        # 最多 500 個 userId
        "to": user_ids,
        "messages": [{"type": "text","text": message}]
    }
    r = requests.post(url, headers=headers, json=data)
    print(r.status_code, r.text)

def get_message(page):
    soup = BeautifulSoup(page, 'html.parser')
    # 提取所有 li 的文字
    items = [li.text.strip() for li in soup.select('ul.list li')]
    # 合併成一條性感的字串，用換行分隔
    message = '\n'.join(items)
    return message

def file_to_json(filenmae):
    with open(filenmae, "r", encoding="utf-8") as f:
        # 去除註解的行（以 # 開頭或在行內）
        cleaned_lines = []
        for line in f:
            # 移除行內註解
            if "#" in line:
                line = line.split("#")[0]
            line = line.strip()
            if line:
                cleaned_lines.append(line)

    # 拼回原本的 Python 結構字串，再 eval 成資料（⚠️ eval 有風險，只用在信任的內容上）
    data_str = "\n".join(cleaned_lines)
    print(data_str)
    return eval(data_str)

# def file_to_str(filename):
#     with open(filename, "r", encoding="utf-8") as f:
#         content = f.read()
#     return content

def file_to_str(filename):
    if os.path.exists(filename):
        with open(os.path.join(base_path, filename), "r") as f:
            content = f.read()
        return content
    else:
        return None

def add_urls(forms):
    for form in forms:
        form['醫師代號']=tbl_doc[f"{form['醫師']}-{form['院區']}"]
        add_url(form)

def add_url(form):
    did = form['醫師代號']
    area = tbl_area[form['院區']]
    match form['院區']:
        case '台北' | '淡水':
            form['網址']=f"https://www.mmh.org.tw/register_single_doctor.php?did={did}&area={area}"
        case '台北兒童':
            form['網址']=f"https://www.mmh.org.tw/child/register_single_doctor.php?did={did}&area={area}"
        case '新竹':
            form['網址']=f"https://www.hc.mmh.org.tw/register_single_doctor.php?did={did}"
        case '新竹兒童':
            form['網址']=f"https://www.hc.mmh.org.tw/child/register_single_doctor.php?did={did}"

def registered(form, token, headless=True, retry=3, test=False):
    msg('\n[開始]' if not test else '\n[測試開始]')
    options = Options()
    if headless:
        options.add_argument('--headless')  # 啟用無頭模式
        # options.add_argument('--disable-gpu')  # 可選，避免某些平台錯誤，(打開此選項時，跑多個執行緒會有問題，只有其中一個執行緒能正常跑)
        options.add_argument('--no-sandbox')  # 避免沙盒問題（尤其在 Linux）
        options.add_argument('--disable-dev-shm-usage')  # 修復共享記憶體問題（Docker 常用）

    if not test: driver = webdriver.Chrome(options=options) # 初始化 Chrome 瀏覽器
    else: driver = webdriver.Chrome() # 初始化 Chrome 瀏覽器

    wait = WebDriverWait(driver, 1)
    driver.get( form['網址'] )           # 開啟網址

    if not test and form['提交時間'] != '': 
        if wait_schedule(form['提交時間']) == False: return

    # 重試 retry 次
    for i in range(1, retry+1):
        try:
            driver.refresh()
            msg(f"\n第 {i} 次嘗試中...")
            # time.sleep(1)

            segment = tbl_segemnt[form['時段']]

            if segment == 0:
                # 找到包含日期的 td，往 parent tr 走，然後在該列內尋找含有「複診(可掛)」的 a
                xpath = f"//td[contains(text(), '{form['日期']}')]/parent::tr//a[contains(text(), '{form['診別']}(可掛)')]"
            else:
                # xpath = f"//td[contains(text(), '{form['日期']}')]/following-sibling::td[{segment}]//a[contains(text(),'{form['診別']}(可掛)')]"
                xpath = f"//tr[td[contains(text(), '{form['日期']}')]]/td[position()={segment + 1}]/a[contains(text(), '{form['診別']}(可掛)')]"

            target_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            print("找到了♥ 開始點點囉～")
            target_button.click()
            
            # time.sleep(1)

            txtID = driver.find_element(By.ID, 'txtID')             #取得 [身分證號] input元件，(根據網頁修改)
            txtBirth = driver.find_element(By.ID, 'txtBirth')       #取得 [生日] input元件，(根據網頁修改)
            button = driver.find_element(By.ID, 'search_button')    #取得 [送出] button元件，(根據網頁修改)
            txtID.send_keys( form['身分證號'] )                     #填入 [身分證號]
            txtBirth.send_keys( form['生日'] )                      #填入 [生日]
            if not test: 
                button.click()                                      #點擊 [按鈕]
                time.sleep(1)
                message = get_message(driver.page_source)
                msg(message)
                if token and form['LINE通知']=='是': broadcast_line_message(token, message)
            else:
                message = get_message(driver.page_source)
                msg(message)
            break
        except Exception as e:
            print("人家找不到按鈕…嗚嗚～", e)
            msg('[失敗]')
            # time.sleep(10)

    msg('\n[結束]' if not test else '\n[測試結束]')




def unit_test():
    forms = file_to_json('forms.py')
    token = file_to_str('line.token')

    add_urls(forms)

    # 開始多執行緒✨
    registered_with_token = partial(registered, token=token)
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(registered_with_token, forms)

    while True:
        print("按'q'離開...")
        k = readchar.readchar() #等待按鍵
        if(k == 'q'):
            print("[離開]") 
            break 



if __name__ == "__main__":
    unit_test()
