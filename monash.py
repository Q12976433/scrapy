#-*- coding:utf-8 -*-
"""
# create of datetime:2022/6/15 1:00
----------
# create of software: PyCharm
"""
import requests
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
from threading import Thread
import pandas as pd


def get_html(url):
    proxies = {
        'http':'http://127.0.0.1:7890',
        'https':'http://127.0.0.1:7890',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers)
    except:
        try:
            res = requests.get(url, headers=headers)
        except:
            try:
                res = requests.get(url, headers=headers)
            except:
                res = requests.get(url, headers=headers)

    html = etree.HTML(res.content.decode())
    return html


def parse(url):
    html = get_html(url)
    labels = html.xpath("//ul[contains(@class,'tabs__tab-list content-center')]/li/a/text()")
    uls = html.xpath("//ul[contains(@class,'cards__card-list')]")
    i = 0
    for ul in uls:
        lis = ul.xpath("./li")
        threads = []
        for li in lis:
            t = Thread(target=parse1,args=(li,i,labels))
            t.start()
            threads.append(t)
        [thread.join() for thread in threads]
        i = i+1

def parse1(li,i,labels):
    list1 = {}
    list1['degrees'] = labels[i]
    list1['href'] = li.xpath("./a/@href")[0]
    list1['course_name'] = li.xpath(".//h3/text()")[0]
    list1['code'] = li.xpath(".//p/text()")[0].split(":")[1].strip()
    html = get_html(list1['href'])
    list1['desc'] = ''.join(html.xpath("//div[contains(@class,'course-page__summary-text')]//text()")).strip().replace(
        "\r\n", '').replace("   ", '')
    list1['location'] = ''.join(
        html.xpath("//*[text()='Location']/../following-sibling::td[1]//text()")).strip().replace("\r\n", '').replace(
        "   ", '')
    list1['duration'] = ''.join(
        html.xpath("//*[text()='Duration']/../following-sibling::td[1]//text()")).strip().replace("\r\n", '').replace(
        "   ", '')
    list1['fees'] = ''.join(html.xpath("//h5[text()='Fees']/following-sibling::p/a/text()")).strip().replace("\r\n", '').replace("   ", '')
    list1['qualifications'] = ''.join(
        html.xpath("//*[@id='min-entry-requirements']/*[text()='Qualifications']/following-sibling::p[position()<=count(//*[@id='min-entry-requirements']/*[text()='Qualifications']/following-sibling::p)-count(//*[@id='min-entry-requirements']/h3/following-sibling::p)]//text()")).strip().replace("\r\n", '').replace(
        "   ", '')
    list1['course_structure'] = ''.join(html.xpath('//*[@data-name="Course structure"]//text()')).strip().replace(
        "\r\n", '').replace("   ", '')
    domestic_csp = html.xpath("//*[text()='Full fee']/following-sibling::p/strong/text()")
    if len(domestic_csp) == 2 or len(domestic_csp) == 1:
        list1['domestic_csp'] = domestic_csp[0]
    else:
        list1['domestic_csp'] = ''
    international_csp = get_html(list1['href'] + '?international=true').xpath(
        "//*[text()='International fee']/following-sibling::p/strong/text()")
    if len(international_csp) == 2 or len(international_csp) == 1:
        list1['international_fee'] = international_csp[0]
    else:
        list1['international_fee'] = ''
    list1['careers'] = ''.join(
        html.xpath("//*[contains(text(),'Careers')]/../preceding-sibling::p[1]/following-sibling::p//text()")).replace(
        'Careers', '')

    datas.append(list1)
    print(list1['course_name'])
    print("*" * 50)

if __name__ == '__main__':
    url = 'https://www.monash.edu/study/courses#tabs__2943928-02'
    hrefs = get_html(url).xpath('//div[@data-test-group="Tile Block - Faculty"]/div[position()<last()]//a/@href')
    datas = []
    with ThreadPoolExecutor() as pool:
        pool.map(parse,hrefs)
    df = pd.DataFrame(datas)
    df.to_excel("monash2.xlsx",index=False)

