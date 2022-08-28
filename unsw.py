#-*- coding:utf-8 -*-
"""
----------
# create of datetime:2022/6/6 21:13
----------
# create of software: PyCharm
"""
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from lxml import etree


def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    }
    res = requests.get(url,headers=headers).content.decode()
    return etree.HTML(res)

def xpath_html(html,pattern,list1):
    divs = html.xpath(pattern)
    for div in divs:
        content = ''.join(div.xpath(".//text()")).replace("\n", '').strip().replace("   ", '').replace("Learn more.",'').replace("Year one",'\n1.').replace("Year two",'\n2.').replace("Year three",'\n3.').replace("Year four",'\n4.').replace("Year five",'\n5.').replace("Year six",'\n6.').replace("Year seven",'\n7.')
        if content != '':
            list1.append(content)

def parse1(i):
    list1 = {}
    href1 = i['displayUrl']
    html = get_html(href1)
    list1['href'] = href1
    list1['course_name'] = html.xpath("//h1/text()")[0]
    list1['desc'] = ''.join(html.xpath("//h1/following-sibling::p/text()"))
    name_divs = html.xpath(
        "//div[contains(@class,'propertytiles property-tiles-bg-colour--light-grey section')]/div[contains(@class,'property-tiles')]/div")
    for name_div in name_divs:
        name = ''.join(name_div.xpath("./div[1]//text()")).replace("\n", '').strip()
        value = ''.join(name_div.xpath("./div[2]//text()")).replace("\n", '').strip()
        list1[name] = value
    name_divs1 = html.xpath("//li[@tabindex='0']/span/@data-click_name")
    j = 1
    for name_div1 in name_divs1:
        name_div1 = name_div1.replace("&", '').replace("  ", '_').replace(" ", '_').replace("?", '').lower()
        if 'fees' in name_div1:
            list1['domestic_full'] = ''.join(html.xpath("//div[contains(text(),'Indicative First Year Full Fee')]/following-sibling::div/text()")).replace("\n",'').strip()
            list1['domestic_full_fee_to_complete_degree'] = ''.join(html.xpath("//div[contains(text(),'Indicative Full Fee to Complete Degree')]/following-sibling::div/text()")).replace("\n",'').strip()
            list1['international_full'] = ''.join(html.xpath("//div[contains(text(),'Indicative First Year Fee')]/following-sibling::div/text()")).replace("\n",'').strip()
            list1['international_fee_to_complete_degree'] = ''.join(html.xpath("//div[contains(text(),'Indicative Fee to Complete Degree')]/following-sibling::div/text()")).replace("\n",'').strip()
        else:
            content = html.xpath(f"//div[@role='tabpanel'][position()={j}]//text()")
            content = [c.strip() for c in content if c.strip()!='']
            content = '\t'.join(content).replace("\n",'').strip().replace("   ", '').replace("Learn more.", '').replace("Year one", '\n1.').replace("Year two", '\n2.').replace("Year three", '\n3.').replace("Year four", '\n4.').replace("Year five", '\n5.').replace("Year six",'\n6.').replace("Year seven", '\n7.')
            list1[name_div1] = content.replace("Ready to start your application?Apply nowFor most international students, applications are submitted via\xa0ourApply Onlineservice. We encourage you to submit your completed application as early as possible to ensure it will be processed in time for your preferred term.Some high-demand programs with limited places, may have an earlier application deadline or may have an earlier commencement\xa0date. For\xa0more information visit\xa0ourinternational applicant information page.*If you are an international student studying an Australian qualification, go to theUniversities Admission Centre (UAC)for application and UAC key dates. Note: If you are under 18 years of age, you need to make special arrangements.Read more.Ready to start your application?Apply now",'')
        j = j + 1
    print(list1)
    datas.append(list1)


def parse(url):
    lis = get_html(url).xpath("//div[@class='responsivegrid aem-GridColumn--default--none aem-GridColumn aem-GridColumn--default--4 aem-GridColumn--medium--12 aem-GridColumn--small--12 aem-GridColumn--offset--default--0']//ul/li")
    for li in lis[:10]:
        title = li.xpath("./a/@title")[0].replace(" ","+")
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
        }
        href = f'https://search.unsw.edu.au/s/search.html?form=json&collection=unsw~unsw-search&profile=degrees&query=!padrenull&start_rank=1&num_ranks=1000&f.Area+of+Study%7CdegreeAreaOfStudy={title}&gscope1=degree&cool.4=0.3'
        r = requests.get(href,headers=headers).json()['response']['resultPacket']['results']
        with ThreadPoolExecutor() as pool:
            pool.map(parse1,r)
    df = pd.DataFrame(datas)
    df.to_excel("unsw.xlsx",index=False)


if __name__ == '__main__':
    datas = []
    url = 'https://www.unsw.edu.au/study/find-a-degree-or-course'
    parse(url)
