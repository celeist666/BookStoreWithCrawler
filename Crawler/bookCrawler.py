from selenium import webdriver
import pymysql
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

connect = pymysql.connect(host='localhost', user='root', password='4885', db='bookStore', charset='utf8')
cursor = connect.cursor(pymysql.cursors.DictCursor)

# sql = "select * from test"
#
# cursor.execute(sql)
# result = cursor.fetchall()
# print(result)

# 국내 도서의 카테고리들 (소설, 경제/경영, 정치/사회, 역사/문화)의 하위 카테고리들
category_list = list(range(101,118,2))
category_list.extend(list(range(1301,1316,2)))
category_list.extend(list(range(1701,1716,2)))
category_list.extend(list(range(1901,1718,2)))

path = "./chromedriver.exe"
browser = webdriver.Chrome(path)

addr = 'http://www.kyobobook.co.kr/categoryRenewal/categoryMain.laf?pageNumber=1&perPage=300&mallGb=KOR&linkClass='

for cat in category_list:
    if cat//1000<1:
        browser.get(addr+'0'+str(cat))
    else:
        browser.get(addr+str(cat))

    # 크롤링할 자료 로딩되었는지 확인
    try:
        graph = WebDriverWait(browser, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="prd_list_type1"]/li[1]/div/div[1]/div[2]/div[1]/a/strong')))
    except TimeoutException:
        print("Timed out")
        browser.quit()

    # 책이 몇개인지 알아내어 책의 개수만큼 반복
    end = len(browser.find_elements_by_xpath('//*[@id="prd_list_type1"]/li'))

    # 제목, 작가, 가격, 출판사, 썸네일
    title=[]; author=[]; price=[]; publisher=[]; thumb=[];

    # 제목, 작가, 가격, 출판사, 썸네일 크롤링
    for i in range(1,end//2,2):
        title.append(browser.find_element_by_xpath('//*[@id="prd_list_type1"]/li['+str(i)+']/div/div[1]/div[2]/div[1]/a/strong').text)
        author.append(browser.find_element_by_xpath('//*[@id="prd_list_type1"]/li['+str(i)+']/div/div[1]/div[2]/div[2]/span[1]').text)
        price.append(browser.find_element_by_xpath('//*[@id="prd_list_type1"]/li['+str(i)+']/div/div[1]/div[2]/div[3]/strong[1]').text[:-1])
        publisher.append(browser.find_element_by_xpath('//*[@id="prd_list_type1"]/li['+str(i)+']/div/div[1]/div[2]/div[2]/span[2]').text)
        temp = browser.find_element_by_xpath('//*[@id="prd_list_type1"]/li['+str(i)+']/div/div[1]/div[1]/div/a/span/img').get_attribute(('src'))
        thumb.append(temp[:41]+'x'+temp[41:51]+'x'+temp[52:])

    # DB에 넣기



