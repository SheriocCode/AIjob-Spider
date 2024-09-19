import csv
import time 
import random #生成随机数，防止检测每次sleep时间相同
from selenium import webdriver
import jsonpath #解析接口返回的json数据
import json 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from lxml import etree

BASE_URL = 'https://www.zhipin.com/web/geek/job?query=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&city={city}'
DATA_CITY_SITE = 'spider/data/city.json'  
 
DATA_PATH ='spider/data/auto/data.csv'

class spider_auto(object):
    def __init__(self) -> None:
        '''
        配置selenium降低自动化检测风险, 一些奇奇怪怪的配置。
        '''
        options = webdriver.ChromeOptions()
        #禁用Chrome的自动化控制特性，减少触发自动化检测反爬
        options.add_argument('--disable-blink-fetures=AutomationControlled')
        #排除enable-automation开关，降低检测风险
        options.add_experimental_option('excludeSwitches',['enable-automation'])
        self.driver = webdriver.Chrome(options=options)

    def __call__(self):
        self.get_crawl_cities()

    def get_crawl_cities(self):
        """
        获取所有城市, 并循环爬取城市
        :return: None
        """
        city_site = json.load(open(DATA_CITY_SITE,'r',encoding='utf-8'))

        #选取热门城市
        cities_list = jsonpath.jsonpath(city_site, '$.zpData.hotCitySites')

        with open(DATA_PATH,'a',encoding='utf-8')as self.f:
            self.writer = csv.writer(self.f)
            for city in cities_list[0]:
                print('start crawl: ',end=''); print(city)
                url = BASE_URL.format(city = city['code'])
                
                #使用selenium自动循环爬取每个城市
                self.driver.get(url)
                time.sleep(10)

                self.rotate_page()

                print('success crawl: ',end=''); print(city)
                time.sleep(random.randint(20,30)) #控制访问频率



    def rotate_page(self):
        """
        使用selenium操控页面
        :return: None
        """
        for page in range(1,11):
            time.sleep(random.randint(3,5)) #控制访问频率
            self.page = page
            try:
                if self.page != 1:
                    bts = self.driver.find_element(By.XPATH,'//div[@class="options-pages"]/a')
                    bt = self.driver.find_element(By.XPATH,'//div[@class="options-pages"]/a[@class="selected"]')
                    order = bts.index(bt) + 1
                    bts[order].click()
            except Exception as ex:
                Warning(f'failed to crawl page{self.page}!')
                Warning(ex)

            try:
                self.crawl_parse()
            except:
                print('该页面爬取异常')
                raise

            time.sleep(random.randint(3,5)) #控制访问频率


    def crawl_parse(self)->None:
        """
        爬取并解析页面元素
        :return: None
        """
        time.sleep(20)
        #等到元素加载出现
        try:
            WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.CLASS_NAME,'job-list-box')))
        except:
            print('页面加载出现问题')
            raise

        #解析页面数据
        html = etree.HTML(self.driver.page_source)
        details = html.xpath('//ul[@class = "job-list-box"]/li')
        for detail in details:
            job = detail.xpath('./div[1]//div[1]/span[1]/text()') #AI算法工程师
            city = detail.xpath('./div[1]//div[1]/span[2]//text()') #武汉·江夏区·光谷东
            company = detail.xpath('./div[1]/div[1]/div[2]/h3//text()') #华为技术武研所
            people = detail.xpath('./div[1]/div[1]/div[2]//li[last()]/text()') #10000人以上
            salary = detail.xpath('./div[1]//div[@class = "job-info clearfix"]/span[1]/text()') #15-30K·16薪
            experience = detail.xpath('./div[1]//div[@class = "job-info clearfix"]/ul/li[1]/text()') #5-10年
            education = detail.xpath('./div[1]//div[@class = "job-info clearfix"]/ul/li[last()]/text()') #本科
            skill = detail.xpath('./div[2]/ul/li/text()') #3ds MAX PS AI绘画

            #一条job的数据
            data = dict(job = job, city = city, company = company, people = people, salary = salary, experience = experience, education = education, skill = skill)
            print(data)
            try:
                #写入字段
                self.writer.writerow([
                    data['job'][0],
                    data['city'][0],
                    data['company'][0],
                    data['people'][0],
                    data['salary'][0],
                    data['experience'][0],
                    data['education'][0],
                    ', '.join(data['skill'])
                ])
            except:
                print('写入文件失败')
            

if __name__ == '__main__':
    spider = spider_auto()
    spider()