import json
import re

import jsonpath
import random
import pymysql
import requests
from lxml import etree
from bs4 import BeautifulSoup


def get_conn():
    """数据库连接"""
    conn = pymysql.connect(host='localhost', user='root', password='123456', database='douban02', port=3306)
    cursor = conn.cursor()
    return conn, cursor


# 获取数据
def spider(spiderTarget, start):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }
    params = {"start": start}
    moviesAllRes = requests.get(spiderTarget, params=params, headers=headers)
    moviesAllRes = moviesAllRes.json()
    detailUrls = jsonpath.jsonpath(moviesAllRes, '$.data..url')
    moviesInfo = jsonpath.jsonpath(moviesAllRes, '$.data')
    if not moviesInfo or not detailUrls:
        print(f"No data found for start={start}")
        return []
    result = []
    moviesInfo = moviesInfo[0]
    for i, moviesInfo in enumerate(moviesInfo):
        if isinstance(moviesInfo, dict):
            resultData = {}
            # 详情URL
            resultData['detailLink'] = detailUrls[i]
            print(resultData)
            # 导演（数组）
            resultData['directors'] = ','.join(moviesInfo['directors'])
            # 评分
            resultData['rate'] = moviesInfo['rate']
            # 影片名
            resultData['title'] = moviesInfo['title']
            # 主演（数组）
            resultData['casts'] = ','.join(moviesInfo['casts'])
            # 封面
            resultData['cover'] = moviesInfo['cover']
            # 通过detailLink进入电影的详情页
            detailMovieRes = requests.get(detailUrls[i], headers=headers)
            xpathHtml = etree.HTML(detailMovieRes.text)  # xpath
            soup = BeautifulSoup(detailMovieRes.text, 'lxml')  # BeautifulSoup
            # 上映年份
            year = xpathHtml.xpath('//div[@id="content"]/h1/span[@class="year"]/text()')
            resultData['year'] = year[0].strip('()') if year else None
            # 影片类型（数组）
            types = xpathHtml.xpath('//div[@id="info"]/span[@property="v:genre"]/text()')
            resultData['types'] = ','.join(types)
            # 制作国家或地区（数组）
            country = soup.find_all('span', class_="pl")[4].next_sibling.strip().split(sep='/')
            for i, c in enumerate(country):
                country[i] = c.strip()
            resultData['country'] = ','.join(country)
            # 上映时间
            upTime = soup.find_all('span', property="v:initialReleaseDate")
            upTimeStr = ""
            for i in upTime:
                upTimeStr = i.get_text()
            upTime = re.findall(r'\d*-\d*-\d*', upTimeStr)
            resultData['time'] = upTime[0] if upTime else None
            # 影片语言（数组）
            lang = soup.find_all("span", class_="pl")[5].next_sibling.strip().split(sep='/')
            for i, l in enumerate(lang):
                lang[i] = l.strip()
            resultData['lang'] = ','.join(lang)
            # 时间长度
            if soup.find('span', property="v:runtime"):
                resultData['movieTime'] = re.findall(r"\d+", soup.find('span', property="v:runtime").get_text())[0]
            else:
                resultData['movieTime'] = random.randint(40, 81)
            # 评论个数
            comment_len = soup.find('span', property="v:votes")
            resultData['comment_len'] = comment_len.get_text() if comment_len else None
            # 星星比例（数组）
            starts = []
            startAll = soup.find_all('span', class_="rating_per")
            for i in startAll:
                starts.append(i.get_text())
            resultData['starts'] = ','.join(starts)
            # 影片简介
            summary = soup.find('span', property="v:summary")
            resultData['summary'] = summary.get_text().strip() if summary else None
            # 获取5条热评
            comments_info = soup.find_all('span', class_="comment-info")
            comments = [{} for x in range(5)]
            for i, comment in enumerate(comments_info):
                if not comment:
                    continue
                comments[i]['user'] = comment.contents[1].get_text()
                star_class = comment.contents[5].attrs['class'][0] if len(comment.contents) > 5 else None
                comments[i]['start'] = re.findall(r'(\d*)', star_class)[7]
                comments[i]['time'] = comment.contents[7].attrs.get('title', None) if len(
                    comment.contents) > 8 else None
            contents = soup.find_all('span', class_='short')
            for i in range(5):
                comments[i]['content'] = contents[i].get_text() if i < len(contents) else None
            resultData['comments'] = json.dumps(comments)
            # 获取五张详情图
            imgList = []
            list1 = soup.select('.related-pic-bd img')
            for i in list1:
                imgList.append(i['src'])
            resultData['imgList'] = ','.join(imgList)
            result.append(resultData)
    return result

# main函数
def main():
    conn, cursor = get_conn()
    for page in range(517,1500):
        spiderTarget = "https://movie.douban.com/j/new_search_subjects"
        data = spider(spiderTarget, page * 20)
        # 写入到数据库中
        sql_insert = '''
            INSERT INTO movies(
                directors,rate,title,casts,cover,year,types,country,lang,time,movietime,comment_len,start,summary,comments,imgList,detailLink
            ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        '''
        print(f"开始插入第{page + 1}页数据！")
        for movie in data:
            params = (
                movie['directors'],
                movie['rate'],
                movie['title'],
                movie['casts'],
                movie['cover'],
                movie['year'],
                movie['types'],
                movie['country'],
                movie['lang'],
                movie['time'],
                movie['movieTime'],
                movie['comment_len'],
                movie['starts'],
                movie['summary'],
                movie['comments'],
                movie['imgList'],
                movie['detailLink']
            )
            cursor.execute(sql_insert, params)
        conn.commit()
    conn.close()
    cursor.close()
if __name__ == '__main__':
    main()