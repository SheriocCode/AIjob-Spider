import requests
import time #用于sleep
import random #生成随机数，防止检测每次sleep时间相同
import jsonpath #解析接口返回的json数据
import json #处理json数据
import csv

HEADERS = {
    "Cookie": "lastCity=101200100; wd_guid=3023dd62-12a8-45f2-905f-c0e1a07aab94; historyState=state; _bl_uid=n3l7no4dfk4sFggIjmqjfjb4eLCq; wt2=DnW8QqNIffH4RCML-PPJKeuocA-8aHji6rSR_NoBybaz6V3Oa1cvNniSFXjvvDkeP_HG8nqwMNcwc3nuQPWnoRQ~~; wbg=0; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1699153045,1699166625,1699343331,1699447684; __g=-; __c=1699502863; __l=l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjob%3Fquery%3D%25E4%25BA%25BA%25E5%25B7%25A5%25E6%2599%25BA%25E8%2583%25BD%26city%3D101040100&r=&g=&s=3&friend_source=0&s=3&friend_source=0; __a=61957306.1698845011.1699447685.1699502863.291.21.55.73; geek_zp_token=V1R9gjGeL02l9qVtRvxhQdKS217DrUzSs~; __zp_stoken__=8209eaXNuB2R5VEhFJDYsbAtvU3lra11ZT3YARSBpf3YOXFw5bzJuWhI2AERofDw6QUdfcTE9Zn5tKBQVO146ZRA5BT97RU8pAAJvWhk5OxUPIBtSExUPO25NPy9IFwlxA35tDjVDZ3RRbEY%3D",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
}

#所有城市信息
CITY_SITE_URL = 'https://www.zhipin.com/wapi/zpgeek/common/data/city/site.json' 

DATA_CITY_SITE = 'spider/data/city.json'  

#返回json数据的接口
BASE_URL = 'https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&city={city}&page={page}&pageSize=30'

DATA_PATH ='spider/data/semi/data.csv'


def get_cities()->list:
    '''
    爬取所有城市代码信息
    选取热门城市
    :return: list 热门城市 
    '''
    # 保存所有城市对应json数据到city_urls.json中
    print('调用城市json接口')
    try:
        json_response = requests.get(url=CITY_SITE_URL,headers=HEADERS).text
        with open(DATA_CITY_SITE,'w',encoding='utf-8')as f:
            f.write(json_response)
            print('写入城市json数据到city.json')
    except:
        print('获取城市数据失败， 直接读取city.json')

    city_site = json.load(open(DATA_CITY_SITE,'r',encoding='utf-8'))
    cities_list = jsonpath.jsonpath(city_site, '$.zpData.hotCitySites') #选取热门城市
    return cities_list


def rotate_urls_crawl():
    '''
    循环爬取每个城市
    :return: None
    '''
    #获取所需城市
    code_list = get_cities() 

    with open(DATA_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['job','city','company','people','salary','experience','education','skill'])

        headers = HEADERS
        for city in code_list[0]:
            print('爬取城市信息： ',end='');print(city)
            for url in [BASE_URL.format(city = city['code'],page =i) for i in range(1,11)]:
                print('start crawling {url}'.format(url=url))
                #设置随机等待时间，降低爬取频率
                time.sleep(3+random.randint(1,3))     
                response = requests.get(url=url,headers=headers)
                job_json = response.json()
                #被反爬检测会返回 37 错误码，需要重置cookie
                while job_json['code'] == 37:
                    headers['Cookie'] = input('行为受限, 需要重置cookie:')
                    time.sleep(5+random.randint(1,5))
                    response = requests.get(url=url,headers=headers)
                    job_json = response.json()

                print(job_json)

                job_list = job_json['zpData']['jobList'] #成功爬取
                #数据处理与写入
                for job in job_list:
                    jobName = job['jobName']
                    city = job['cityName']
                    company = job['brandName']
                    people = job['brandScaleName']
                    salary = job['salaryDesc']
                    experience = job['jobLabels'][0]
                    education = job['jobDegree']
                    skill = job['skills']
                    try:
                        writer.writerow([jobName,city,company,people,salary,experience,education,skill])
                    except:
                        print('文件写入错误')
                print('success crawl\n')
            print('成功爬取城市!');

        print('Program Success!')

if __name__ == '__main__':
    rotate_urls_crawl()
