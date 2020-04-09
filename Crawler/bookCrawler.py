from selenium import webdriver
import pymysql
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# 국내도서 크롤링
def domestic(browser, category_list):
    for cat in category_list:
        if cat // 1000 < 1:
            browser.get(addr + '0' + str(cat))
        else:
            browser.get(addr + str(cat))

        # 크롤링할 자료 로딩되었는지 확인
        try:
            graph = WebDriverWait(browser, 10).until(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, '//*[@id="prd_list_type1"]/li[1]/div/div[1]/div[2]/div[1]/a/strong')))
        except TimeoutException:
            print("Timed out")
            browser.quit()

        # 책이 몇개인지 알아내어 책의 개수만큼 반복
        end = len(browser.find_elements_by_xpath('//*[@id="prd_list_type1"]/li'))

        # sql문 준비, 제목, 썸네일, 가격, 저자, 출판사, 1차카테고리, 2차카테고리, 3차카테고리
        sql = 'insert into book(title, thumb, price, author, publisher, cat1, cat2, cat3) values '

        cat1 = '국내도서'
        cat2 = browser.find_element_by_xpath('//*[@id="container"]/div[1]/div[3]/p/span/a').text
        cat3 = browser.find_element_by_xpath('//*[@id="container"]/div[1]/div[4]/p/span/a').text

        # 스크롤 이동을 위한 출발점 지정
        scrl = 500

        # 제목, 작가, 가격, 출판사, 썸네일 크롤링
        for i in range(1, end, 2):
            sql += '('
            title = browser.find_element_by_xpath(
                '//*[@id="prd_list_type1"]/li[' + str(i) + ']/div/div[1]/div[2]/div[1]/a/strong').text
            author = browser.find_element_by_xpath(
                '//*[@id="prd_list_type1"]/li[' + str(i) + ']/div/div[1]/div[2]/div[2]/span[1]').text
            price = browser.find_element_by_xpath(
                '//*[@id="prd_list_type1"]/li[' + str(i) + ']/div/div[1]/div[2]/div[3]/strong[1]').text[:-1]
            publisher = browser.find_element_by_xpath(
                '//*[@id="prd_list_type1"]/li[' + str(i) + ']/div/div[1]/div[2]/div[2]/span[2]').text
            temp = browser.find_element_by_xpath(
                '//*[@id="prd_list_type1"]/li[' + str(i) + ']/div/div[1]/div[1]/div/a/span/img').get_attribute(('src'))
            thumb = temp[:41] + 'x' + temp[41:51] + 'x' + temp[52:]
            sql += '"' + title.replace("'",'').replace('"','') + '"' + "," + '"' + thumb + '"' + "," + price.replace(",",
                                                                                     '') + "," + '"' + author + '"' + "," + '"' + publisher.replace("'",'') + '"' + "," + '"' + cat1 + '"' + "," + '"' + cat2 + '"' + "," + '"' + cat3 + '"' + '),'

            # 스크롤 이동
            scrl += 218
            browser.execute_script("window.scrollTo(0, " + str(scrl) + ")")

        print(cat1 + ' > ' + cat2 + ' > ' + cat3 + ' 크롤링 완료')
        cursor.execute(sql[:-1])
        connect.commit()

# 해외도서 크롤링용
def foreign(browser, category_list):
    for cat in category_list:
        if cat // 10 < 1:
            browser.get(addr + 'ENG' + addr1 + '0' + str(cat))
        else:
            if cat<16:
                browser.get(addr + 'ENG' + addr1 + str(cat))
            else:
                browser.get(addr + 'JAP' + addr1 + str(cat))

        # 크롤링할 자료 로딩되었는지 확인
        try:
            graph = WebDriverWait(browser, 10).until(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, '//*[@id="main_contents"]/ul/li[1]/div[2]/div[2]/a/strong')))
        except TimeoutException:
            print("Timed out")
            browser.quit()

        # 책이 몇개인지 알아내어 책의 개수만큼 반복
        end = len(browser.find_elements_by_xpath('//*[@id="main_contents"]/ul/li'))

        # sql문 준비
        sql = 'insert into book(title, thumb, price, author, publisher, cat1, cat2, cat3) values '

        cat1 = '외국도서'
        temp = browser.find_element_by_xpath('//*[@id="main_contents"]/div[3]/h4').text
        cat2 = temp[:4]
        cat3 = temp[6:(temp.find('(')-1)]

        # 스크롤 이동을 위한 출발점 지정
        scrl = 800

        # 제목, 작가, 가격, 출판사, 썸네일 크롤링
        for i in range(1, end + 1):
            sql += '('
            title = browser.find_element_by_xpath(
                '//*[@id="main_contents"]/ul/li[' + str(i) + ']/div[2]/div[2]/a/strong').text
            temp = browser.find_element_by_xpath(
                '//*[@id="main_contents"]/ul/li[' + str(i) + ']/div[2]/div[3]').text
            author = temp[:(temp.find('|')-1)]
            price = browser.find_element_by_xpath(
                '//*[@id="main_contents"]/ul/li[' + str(i) + ']/div[2]/div[5]/strong').text[:-1]
            publisher = temp[(temp.find('|')+2):(temp.rfind('|')-1)]
            thumb = browser.find_element_by_xpath(
                '//*[@id="main_contents"]/ul/li[' + str(i) + ']/div[1]/a/img').get_attribute(('src'))
            # 이미지 없는 책들 예외처리
            if thumb =="http://image.kyobobook.co.kr/newimages/apps/b2c/product/Noimage_l.gif":
                continue
            elif thumb =="http://image.kyobobook.co.kr/newimages/apps/b2c/product/19adult_m.gif":
                continue
            sql += '"' + title.replace("'",'').replace('"','') + '"' + "," + '"' + thumb + '"' + "," + price.replace(",",
                                                                                     '') + "," + '"' + author.replace("'",'').replace('"','') + '"' + "," + '"' + publisher.replace("'",'').replace('"','') + '"' + "," + '"' + cat1 + '"' + "," + '"' + cat2 + '"' + "," + '"' + cat3 + '"' + '),'

            # 스크롤 이동
            scrl += 291
            browser.execute_script("window.scrollTo(0, " + str(scrl) + ")")

        print(cat1 + ' > ' + cat2 + ' > ' + cat3 + ' 크롤링 완료')
        cursor.execute(sql[:-1])
        connect.commit()

# pymysql
connect = pymysql.connect(host='localhost', user='root', password='4885', db='bookstore', charset='utf8')
cursor = connect.cursor(pymysql.cursors.DictCursor)

# 국내 도서의 카테고리들 (소설, 경제/경영, 정치/사회, 역사/문화)의 하위 카테고리들
category_list = list(range(101, 112, 2))
category_list.extend(list(range(1301, 1316, 2)))
category_list.extend(list(range(1701, 1716, 2)))
category_list.extend(list(range(1901, 1718, 2)))

# 크롬드라이버 위치설정
path = "./chromedriver.exe"
browser = webdriver.Chrome(path)

# 국내도서 크롤링용 주소, 마지막 linkClass에 무슨 값을 넣어주느냐에 따라 카테고리가 다름
addr = 'http://www.kyobobook.co.kr/categoryRenewal/categoryMain.laf?pageNumber=1&perPage=300&mallGb=KOR&linkClass='

# 국내도서 크롤링 시작
domestic(browser, category_list)

# 국내도서 끝, 해외도서 시작

# 해외도서 카테고리
category_list = list(range(1, 16, 2))
category_list.extend(list(range(43, 64, 2)))

# 해외도서 주소, mallGb 값에 따라 어느나라 도서를 고를지 선택이 된다.
addr = 'http://www.kyobobook.co.kr/bestSellerNew/bestseller.laf?mallGb='
addr1 = '&range=0&kind=0&orderClick=DBf&perPage=300&linkClass='

# 해외도서 크롤링 시작
foreign(browser, category_list)

connect.close()

