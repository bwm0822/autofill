from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
#import os
import readchar

''' 程式說明
功能 : 網頁自動填表格
安裝套件 : pip install -r requirements.txt 
參考文件 : https://steam.oxxostudio.tw/category/python/spider/selenium.html
'''

url = 'https://www.mmh.org.tw/register_divide.php?depid=201&area=ts'    #掛號網址
id = 'A123456789'   #身分證號
birth = 'YYMMDD'    #生日

driver = webdriver.Chrome() # 初始化 Chrome 瀏覽器
driver.get( url )           # 開啟網址

while True:

    # 1. 手動操作瀏覽器到掛號頁面
    # 2. 按[任意鍵]預約

    #os.system('pause')
    #user_input = input("按下 Enter 鍵以退出程式...")
    print("按[任意鍵]預約，按[q鍵]離開...")
    k = readchar.readchar() #等待按鍵
    if(k == 'q'):
        print("[離開]") 
        break 

    txtID = driver.find_element(By.ID, 'txtID')             #取得 [身分證號] input元件，(根據網頁修改)
    txtBirth = driver.find_element(By.ID, 'txtBirth')       #取得 [生日] input元件，(根據網頁修改)
    button = driver.find_element(By.ID, 'search_button')    #取得 [送出] button元件，(根據網頁修改)

    txtID.send_keys( id )          #填入 [身分證號]
    txtBirth.send_keys( birth )    #填入 [生日]
    button.click()                 #點擊 [按鈕]

