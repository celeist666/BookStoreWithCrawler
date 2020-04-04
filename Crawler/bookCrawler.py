from selenium import webdriver
import pymysql

connect = pymysql.connect(host='localhost', user='root', password='4885', db='bookStore', charset='utf8')
cursor = connect.cursor(pymysql.cursors.DictCursor)

sql = "select * from test"

cursor.execute(sql)
result = cursor.fetchall()
print(result)

path = "./chromedriver.exe"
driver = webdriver.Chrome(path)
