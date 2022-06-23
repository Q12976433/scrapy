#-*- coding:utf-8 -*-
"""
----------
# create of software: PyCharm
"""
import requests
import threading
import pandas as pd
from lxml import etree


def parse(tr,type):
    i = 1
    list = {}
    for th in ths:
        name = '_'.join(th.xpath(".//text()")[0].split(" "))
        list['student_type'] = type[1]
        list[f'{name}'] = ''.join(tr.xpath(f"./td[{i}]//text()")).strip()
        i = i + 1
    href = ''.join(tr.xpath("./td[1]/a/@href"))
    if href != '':
        try:
            res = requests.get(href).text
            html = etree.HTML(res)
            list['location'] = ''.join(html.xpath("//em[contains(text(),'Location')]//text()")).replace("Location:",'').strip()
            list['load_credit_points'] = ''.join(html.xpath("//em[contains(text(),'Load credit points')]//text()")).replace("Load credit points:", '')
            list['url']=href
            list['overview'] = ' '.join(html.xpath("//h2[2]/preceding-sibling::p[position()<last()]//text()")).strip()
            print(list['location'])
        except Exception as e:
            with open("log.txt",'a',encoding='utf-8') as f:
                f.write(f'{type[1]}{list["Course_Code"]}link:{href}has error\r:{e}\n')
    else:
        list['location'] = ''
        list['load_credit_points'] = ''
        list['overview'] = ''
    list1.append(list)
    print(list)
    print("*" * 50)

if __name__ == '__main__':
    print("begin")
    url = 'https://cis.uts.edu.au/fees/course-fees.cfm'
    headers = {
        'Host': 'cis.uts.edu.au',
        'Origin': 'https://cis.uts.edu.au',
        'Referer': 'https://cis.uts.edu.au/fees/course-fees.cfm',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
    }
    datas = [['HL', 'Commonwealth Supported Place'], ['DF', 'Postgraduate Domestic Coursework'],
             ['DFRT', 'Postgraduate Domestic Research'], ['IFUG', 'lnternational Undergraduate'],
             ['IF', 'International Postgraduate Coursework'], ['IFRT', 'International Postgraduate Research']]
    list1 = []
    for type in datas:
        data = {
            'fee_type': type[0],
            'fee_year': 2022,
            'cohort_year': 2022,
            'course_area': 'All',
            'Search':'',
            'op': 'Search'
        }
        res = requests.post(url,headers=headers,data=data).text
        html = etree.HTML(res)
        ths = html.xpath("//tr[@valign='top'][1]/th")
        trs = html.xpath("//tr[@valign='top'][position()>1]")
        a = []
        for tr in trs:
            t = threading.Thread(target=parse,args=(tr,type))
            t.start()
            a.append(t)
        [i.join() for i in a]
        print(len(list1))
    print("saving")
    df = pd.DataFrame(list1)
    df.to_excel("uts.xlsx",index=False)
    print("over")
