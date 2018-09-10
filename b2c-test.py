#coding:utf-8

# 基于浏览器的自动化测试技术
# 可以与requests api客户端结合，做数据结果断言
# 自动测试如果 运行时间慢，可以与(如果在服务机多机自动运行：phantomjs>chrome): 
#   1. celery库结合做分布式自动化测试
#   2. 使用远程driver(可能要运行senium-server) https://stackoverflow.com/questions/23700511/remotewebdriver-with-chrome

import splinter
from splinter import Browser

# 示例用法
with Browser('chrome', headless=False) as browser:
    url = "http://www.baidu.com"
    browser.visit(url)
    browser.fill('wd', 'hello')
    button = browser.find_by_id("su") #id不需要前面的 '#'
    button.click()
    if browser.is_text_present('百度翻译'):
        print("ok,出现了百度翻译")
    else:
        print("No,没有出现")