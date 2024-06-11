# cookie-fetcher

1. 环境准备

linux环境可以参考：https://www.geeksforgeeks.org/how-to-install-selenium-tools-on-linux/

windows环境安装好chrome浏览器即可

drive下载地址为：https://chromedriver.storage.googleapis.com/index.html?path=110.0.5481.30/
,请根据自己的chrome版本号查找driver的实际下载地址，chrome设置中可以查看版本号

python环境准备：
```
pip install -r requirements.txt
```

2. 获取cookie

3d66的cookie获取方式比较简单，简易登录后F12打开开发者工具查看，只需拿到PHPSESSID，![img](./docs/findcookie.jpg)

或者通过执行以下代码获取，需要手动登录验证：
```
cookies获取方式，首先通过执行以下两条语句：
driver=webdriver.Chrome()
driver.get(url='https://3d.3d66.com/model/_1_6_1.html')
然后，进入浏览器手动登录
最后，执行下述语句，得到cookie
cookies=driver.get_cookies()
```

3. 执行脚本

get3DDataUrl：获取所有相关模型链接与图片链接，需要先运行
download3DFiles：获取文件与图片，放在对应文件夹内，start和end控制下载文件的起始id

配置文件解析：
```
cookie: 'PHPSESSID=9j7m9itq9kchqts5vsfpke2paj;' # 填写cookie
savePath: '3dmodels' # 模型保存路径
headless: True # 是否headless运行
keyword: '工业' # 搜索关键词
url: 'https://3d.3d66.com/model/{keyword}_1_0_1.html' # url，可以与关键词配合拼接
resultCsvPath: 'result.csv' # get3DDataUrl结果文件保存地址
binaryLocation: 'driver/chromedriver' # 二进制文件地址
userAgent: # 浏览器相关配置
  - Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36
downloadInterval: 5 # 下载时间间隔，每10个等待 5 *60s时间
```


4. 其他网站

大概看了一下https://www.cgmodel.com/、https://www.qingmo.com/
，都是类似的网站，可以通过同样的方式获取cookie
网页爬取逻辑可能略作修改
