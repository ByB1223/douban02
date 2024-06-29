# 爬取豆瓣电影的评论内容
import re
import requests
from lxml import etree
from pymysql import *

# 连接MySQL数据库
conn = connect(host='localhost', user='root', password='123456', database='douban02', port=3306)
cursor = conn.cursor()

def querys(sql, params, type='no_select'):
    params = tuple(params)
    cursor.execute(sql, params)
    if type != 'no_select':
        data_list = cursor.fetchall()
        conn.commit()
        return data_list
    else:
        conn.commit()
        return '数据库语句执行成功'

# 爬取数据函数
def spider_main():
    with open('dataurl.csv', 'r') as f:
        for i in f.readlines():
            mId = re.findall(r'\d+', i)[0]
            for j in range(5):
                base_url = "https://movie.douban.com/subject/{}/reviews?start={}".format(mId, j * 20)
                print(base_url)
                headers = {
                    "User-Agent":
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
                }
                response = requests.get(base_url, headers=headers)
                xpathHtml = etree.HTML(response.text)  #
                movieName = xpathHtml.xpath('//div[@class="subject-title"]/a/text()')[0][2:]  # 电影名字
                divs = xpathHtml.xpath('//div[@class="review-list  "]/div')
                for div in divs:
                    content = div.xpath('.//div[@class="short-content"]/text()')
                    if content and content[0].strip():  # 检测content是否存在且非空
                        querys('insert into comments(movieName,commentContent) values(%s,%s)', [movieName, content[0]])

# 主入口
if __name__ == '__main__':
    spider_main()