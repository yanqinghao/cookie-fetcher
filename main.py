import time
import yaml
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie
from selenium import webdriver
from selenium.webdriver.common.by import By


with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

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

if config['headless']:
    chrome_options.add_argument('headless')
    chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(
    executable_path=config['binaryLocation'], options=chrome_options
)

url = config['url'].format(**{'keyword': config['keyword']})

driver.get(url=url)

for k, v in cookie.items():
    driver.add_cookie({'name': k, 'value': v.value, 'domain': '.3d66.com'})

driver.refresh()

driver.maximize_window()
r = []

temp_height = 0
last_height = 0
while True:
    # 模拟滚动事件
    driver.execute_script('window.scrollBy(0,650)')
    # 休眠一段事件供浏览器加载
    time.sleep(0.5)
    check_height = driver.execute_script(
        'return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;'  # noqa
    )
    if check_height == temp_height:
        # 补充点击加载更多按钮
        if last_height == temp_height:
            break
        last_height = temp_height
        # print('点击加载更多按钮')
        tags = driver.find_elements(By.CLASS_NAME, 'list-flow-more')
        # print(tags)
        # time.sleep(0.2)
        if len(tags) > 0:
            try:
                tags[0].click()
                continue
            except:
                break
        break
    temp_height = check_height
    html = driver.page_source

    # 爬取数据的主逻辑
    soup = BeautifulSoup(html, 'html.parser')
    candidate = soup.find_all('a', class_='model-buried-point')
    for i in candidate:
        try:
            c = i.find('div').find('img')
            r.append([c['alt'], i.get('href', None), c['src']])
        except:
            pass

driver.quit()

data = pd.DataFrame(np.array(r))
data.columns = ['名字', '下载链接', '图片预览']
data = data.drop_duplicates().reset_index(drop=True)
data.to_csv(config['resultCsvPath'], encoding='utf-8')
