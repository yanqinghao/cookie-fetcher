import os
import time
import yaml
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
from http.cookies import SimpleCookie
from selenium import webdriver
from selenium.webdriver.common.by import By


# 支持仅对指定行的数据下载,如果无end则end设为-1
start = 0
end = 20

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 设置保存的本地路径，按需修改
saveDir = config['savePath']
cookie = config['cookie']

data = pd.read_csv(config['resultCsvPath'])

rawcookie = config['cookie']
cookie = SimpleCookie()
cookie.load(rawcookie)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--incognito')  # 无痕模式
chrome_options.add_experimental_option(
    'excludeSwitches', ['enable-automation', 'enable-logging']
)
chrome_options.add_argument(f'user-agent={config["userAgent"]}')
prefs = {'download.default_directory': saveDir}
chrome_options.add_experimental_option('prefs', prefs)

if config['headless']:
    chrome_options.add_argument('headless')
    chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(
    executable_path=config['binaryLocation'], options=chrome_options
)

error_indexes = []

data = data[start:].reset_index(drop=True)
for i, row in data.iterrows():
    if i >= end - start:
        break

    name = f'{row["名字"]}_{i}'
    url = row['下载链接']
    imgurl = row['图片预览']

    itemSaveDir = os.path.join(saveDir, name)

    os.makedirs(itemSaveDir, exist_ok=True)
    itemId = url.split('?')[0].split(r'/')[-1].split('.')[0]
    try:
        driver.get(url=url)
        for k, v in cookie.items():
            driver.add_cookie(
                {'name': k, 'value': v.value, 'domain': '.3d66.com'}
            )
        driver.refresh()
        driver.maximize_window()
        driver.find_elements(By.CLASS_NAME, 'download-now')[0].click()
        time.sleep(1)
        driver.switch_to.frame('layui-layer-iframe100001')
        driver.find_elements(By.CLASS_NAME, 'openrecharge')[0].click()
        # 需要等待下载成功，否则会报错
        while True:
            time.sleep(2)
            files = [
                os.path.join(saveDir, f) for f in os.listdir(saveDir)
            ]  # add path to each file
            files.sort(key=lambda x: os.path.getmtime(x))
            newest_file = files[-1]

            if newest_file.endswith('rar'):
                break
            else:
                print('仍未下载完,继续等待')
                continue
        # 病毒扫描等待时间
        time.sleep(1.5)
        print(f'模型：{name}，id：{itemId}下载成功')
        os.rename(
            newest_file, os.path.join(itemSaveDir, f'{name}_{itemId}.rar')
        )
        time.sleep(1)

        r = requests.get(imgurl)
        img = Image.open(BytesIO(r.content)).convert('RGB')
        img.save(os.path.join(itemSaveDir, f'{name}_preview.png'))
    except Exception as e:
        print(str(e))
        print(f'解析异常，index={i},name={name},itemId={itemId}')
        error_indexes.append([i, f'{name}_{itemId}.rar'])
        pass
    if i % 10 != 0 or i == 0:
        print(f'等待{config["downloadInterval"]}秒后继续下载')
        time.sleep(config['downloadInterval'])
    else:
        time.sleep(config['downloadInterval'] * 60)

if len(error_indexes):
    print(f'下载异常模型为：{";".join(error_indexes)}')
driver.quit()
