from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import datetime
import time
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='1111', db='moatoon', charset='utf8',autocommit=True)
curs = conn.cursor()
did = 'cookib'
dpwd = 'Raqzc!@ZDuy322'

option = webdriver.ChromeOptions()
option.add_argument("--incognito")

browser  = webdriver.Chrome(executable_path='./chromedriver', chrome_options=option)

browser.get("http://webtoon.daum.net/")
browser.find_element_by_xpath('//*[@id="btnMinidaumLogin"]').click()
time.sleep(1)
browser.find_element_by_xpath('//*[@id="id"]').send_keys(did)
browser.find_element_by_xpath('//*[@id="inputPwd"]').send_keys(dpwd)
browser.find_element_by_xpath('//*[@id="loginBtn"]').click()
time.sleep(1)

r = open('./daumtoonlinklist.txt', 'r', encoding='UTF-8')
ur = r.read()
urls = ur.split()
r.close()

file_path = "./daumtoonlist.txt"
file_path01 = "./daumtoonlist02.txt"
data = ''
f = open(file_path, 'w', encoding='utf-8')
t = open(file_path01, 'w', encoding='utf-8')

for i in range(0, len(urls)):
    browser.get(urls[i])
    print(urls[i])
    sql = '''select * from mainlist where main_link = "''' + urls[i] + '''"'''
    curs.execute(sql)
    rows = curs.fetchall()
    print(rows)

    # 페이지로딩 타임아웃
    timeout = 10
    try:
        graph = WebDriverWait(browser, timeout).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='episodeList']/div[3]")))
    except TimeoutException:
        print("Timed out")
        browser.quit()

    ddlc = len(browser.find_elements_by_xpath("//*[@id='episodeList']/div[3]/span/a"))
    print(ddlc)
    ccnt = 1
    listbtn = browser.find_element_by_xpath('//*[@id="episodeList"]/div[3]/span/em')
    listbtn_str = listbtn.text

    if ddlc == 0:
        WebDriverWait(browser, timeout).until(EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='episodeList']/ul")))
        dlc = len(browser.find_elements_by_xpath("//*[@id='episodeList']/ul/li"))
        cnt = 1
        while cnt <= dlc:
            try:
                thumb_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/a/span[1]/img'
                thumb = browser.find_element_by_xpath(thumb_path)
            except:
                thumb_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/a/img'
                thumb = browser.find_element_by_xpath(thumb_path)
            manga_title_path = '//*[@id="cSub"]/div[1]/div/div/h3'
            manga_title = browser.find_element_by_xpath(manga_title_path)
            title_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/a/strong'
            title = browser.find_element_by_xpath(title_path)
            link_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/a'
            link = browser.find_element_by_xpath(link_path)
            try:
                date_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/div/span[3]'
                date = browser.find_element_by_xpath(date_path)
            except:
                date_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/div/span'
                date = browser.find_element_by_xpath(date_path)
            date2 = date.text.split("일 후 무료")
            if len(date2) != 1:
                real_date = datetime.date.today() + datetime.timedelta(days=int(date2[0]))
                data = "[%4d번째 망가] 썸네일주소 : %s, 웹툰명 : %s, 제목 : %s, 날짜 : %s, 웹툰주소 : %s\n" % \
                       (i, thumb.get_attribute('src'), manga_title.text, title.text, real_date.strftime('%Y.%m.%d'),
                        link.get_attribute('href'))
                tlist = "%s\n" % (link.get_attribute('href'))
                sql = '''insert into toonlist(thumb,title,link,date) values("''' + thumb.get_attribute(
                    'src') + '''","''' + title.text.strip() + '''","''' + link.get_attribute(
                    'href') + '''","''' + real_date.strftime('%Y.%m.%d') + '''")'''
                curs.execute(sql)

                if cnt == 1:
                    print('---------------------------------------------------------------------------------------------------------------------')
                    sql = '''update mainlist set recent = "'''+ title.text + '''" where main_link = "'''+ urls[i] + '''"'''
                    curs.execute(sql)
                    print('---------------------------------------------------------------------------------------------------------------------')

                f.write(data)
                t.write(tlist)

                print(cnt, thumb.get_attribute('src'), title.text, link.get_attribute('href'),
                      real_date.strftime('%Y.%m.%d'))
                cnt += 1
            else:
                data = "[%4d번째 망가] 썸네일주소 : %s, 웹툰명 : %s, 제목 : %s, 날짜 : %s, 웹툰주소 : %s\n" % \
                       (i, thumb.get_attribute('src'), manga_title.text, title.text, date.text,
                        link.get_attribute('href'))
                tlist = "%s\n" % (link.get_attribute('href'))
                sql = '''insert into toonlist(thumb,title,link,date) values("''' + thumb.get_attribute(
                    'src') + '''","''' + title.text.strip() + '''","''' + link.get_attribute(
                    'href') + '''","''' + date.text + '''")'''
                curs.execute(sql)

                if cnt == 1:
                    print('---------------------------------------------------------------------------------------------------------------------')
                    sql = '''update mainlist set recent = "'''+ title.text + '''" where main_link = "'''+ urls[i] + '''"'''
                    curs.execute(sql)
                    print('---------------------------------------------------------------------------------------------------------------------')

                f.write(data)
                t.write(tlist)

                print(cnt, thumb.get_attribute('src'), title.text, link.get_attribute('href'), date.text)
                cnt += 1
    else:
        while ccnt <= ddlc+1:
            ddlcarray = browser.find_elements_by_xpath("//*[@id='episodeList']/div[3]/span/a")
            if ddlc == 5:
                if ddlcarray[-1].text == '다음':
                    if ccnt == 1 or ccnt == 5:
                        listbtn2 = browser.find_element_by_xpath('//*[@id="episodeList"]/div[3]/span/em')
                        listbtn2_str = listbtn2.text
                else:
                    if ccnt == 1:
                        listbtn2 = browser.find_element_by_xpath('//*[@id="episodeList"]/div[3]/span/em')
                        listbtn2_str = listbtn2.text
            else:
                if ccnt == 1 or ccnt == 6:
                    listbtn2 = browser.find_element_by_xpath('//*[@id="episodeList"]/div[3]/span/em')
                    listbtn2_str = listbtn2.text
            WebDriverWait(browser, timeout).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='episodeList']/ul")))
            dlc = len(browser.find_elements_by_xpath("//*[@id='episodeList']/ul/li"))
            cnt = 1
            while cnt <= dlc:
                if cnt == 1 and ccnt == 1 and urls[i]=='http://webtoon.daum.net/webtoon/view/operation':
                    cnt+=1
                    continue
                else:
                    try:
                        thumb_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/a/span[1]/img'
                        thumb = browser.find_element_by_xpath(thumb_path)
                    except:
                        thumb_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/a/img'
                        thumb = browser.find_element_by_xpath(thumb_path)
                    manga_title_path = '//*[@id="cSub"]/div[1]/div/div/h3'
                    manga_title = browser.find_element_by_xpath(manga_title_path)
                    title_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/a/strong'
                    title = browser.find_element_by_xpath(title_path)
                    link_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/a'
                    link = browser.find_element_by_xpath(link_path)
                    try:
                        date_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/div/span[3]'
                        date = browser.find_element_by_xpath(date_path)
                    except:
                        date_path = '//*[@id="episodeList"]/ul/li[' + str(cnt) + ']/div/span'
                        date = browser.find_element_by_xpath(date_path)
                    date2 = date.text.split("일 후 무료")
                    if len(date2) != 1:
                        real_date = datetime.date.today() + datetime.timedelta(days=int(date2[0]))
                        data = "[%4d번째 망가] 썸네일주소 : %s, 웹툰명 : %s, 제목 : %s, 날짜 : %s, 웹툰주소 : %s\n" % \
                               (i, thumb.get_attribute('src'), manga_title.text, title.text,
                                real_date.strftime('%Y.%m.%d'),
                                link.get_attribute('href'))
                        tlist = "%s\n" % (link.get_attribute('href'))
                        sql = '''insert into toonlist(thumb,title,link,date) values("''' + thumb.get_attribute(
                            'src') + '''","''' + title.text.strip() + '''","''' + link.get_attribute(
                            'href') + '''","''' + real_date.strftime('%Y.%m.%d') + '''")'''
                        curs.execute(sql)

                        if ccnt == 1 and cnt == 1:
                            print(
                                '---------------------------------------------------------------------------------------------------------------------')
                            sql = '''update mainlist set recent = "''' + title.text + '''" where main_link = "''' + \
                                  urls[i] + '''"'''
                            curs.execute(sql)
                            print(
                                '---------------------------------------------------------------------------------------------------------------------')
                        elif ccnt == ddlc+1 and cnt == dlc and urls[i] =='http://webtoon.daum.net/webtoon/view/operation':
                            print(
                                '---------------------------------------------------------------------------------------------------------------------')
                            sql = '''update mainlist set recent = "''' + title.text + '''" where main_link = "''' + \
                                  urls[i] + '''"'''
                            curs.execute(sql)
                            print(
                                '---------------------------------------------------------------------------------------------------------------------')

                        f.write(data)
                        t.write(tlist)

                        print(cnt, thumb.get_attribute('src'), title.text, link.get_attribute('href'),
                              real_date.strftime('%Y.%m.%d'))
                        cnt += 1
                    else:
                        data = "[%4d번째 망가] 썸네일주소 : %s, 웹툰명 : %s, 제목 : %s, 날짜 : %s, 웹툰주소 : %s\n" % \
                               (i, thumb.get_attribute('src'), manga_title.text, title.text, date.text,
                                link.get_attribute('href'))
                        tlist = "%s\n" % (link.get_attribute('href'))
                        sql = '''insert into toonlist(thumb,title,link,date) values("''' + thumb.get_attribute(
                            'src') + '''","''' + title.text.strip() + '''","''' + link.get_attribute(
                            'href') + '''","''' + date.text + '''")'''
                        curs.execute(sql)

                        if ccnt == 1 and cnt == 1:
                            print(
                                '---------------------------------------------------------------------------------------------------------------------')
                            sql = '''update mainlist set recent = "''' + title.text + '''" where main_link = "''' + \
                                  urls[i] + '''"'''
                            curs.execute(sql)
                            print(
                                '---------------------------------------------------------------------------------------------------------------------')

                        f.write(data)
                        t.write(tlist)

                        print(cnt, thumb.get_attribute('src'), title.text, link.get_attribute('href'), date.text)
                        cnt += 1
            if ccnt==ddlc+1:
                break
            else:
                brw_path = '//*[@id="episodeList"]/div[3]/span/a['+str(ccnt)+']'
                browser.find_element_by_xpath(brw_path).click()
                print(listbtn_str)
                print(listbtn2_str)
                print('ccnt : '+str(ccnt))
                time.sleep(1)
                if listbtn_str != listbtn2_str:
                    ddlcarray = browser.find_elements_by_xpath("//*[@id='episodeList']/div[3]/span/a")
                    ddlc = len(browser.find_elements_by_xpath("//*[@id='episodeList']/div[3]/span/a"))
                    ccnt = 1
                    listbtn = browser.find_element_by_xpath('//*[@id="episodeList"]/div[3]/span/em')
                    listbtn_str = listbtn.text
                    listbtn2 = browser.find_element_by_xpath('//*[@id="episodeList"]/div[3]/span/em')
                    listbtn2_str = listbtn2.text
                ccnt+=1

f.close()
t.close()
conn.close()
