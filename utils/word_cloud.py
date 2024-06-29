import stylecloud
import pymysql


# 连接数据库
def get_conn():
    conn = pymysql.connect(host='localhost', user='root', password='123456', database='douban02', port=3306)
    cursor = conn.cursor()
    return conn, cursor


def getTitleImg(field, icon_name, output_name):
    sql = f"SELECT {field} FROM movies"
    conn, cursor = get_conn()
    cursor.execute(sql)
    data = cursor.fetchall()
    text1=' '.join([row[0] for row in data if row[0] is not None])
    stylecloud.gen_stylecloud(text=' '.join(text1),collocations=False,
                              font_path='C:/Windows/Fonts/simhei.ttf',
                              icon_name=icon_name,size=500,output_name=output_name)


def getCastsImg(field, icon_name, output_name):
    sql = f"SELECT {field} FROM movies"
    conn, cursor = get_conn()
    cursor.execute(sql)
    data = cursor.fetchall()
    text1 = ' '.join([row[0] for row in data if row[0] is not None])
    #text=' '.join(text1) OR  text=text1
    stylecloud.gen_stylecloud(text=text1, collocations=False,
                              font_path='C:/Windows/Fonts/simhei.ttf',
                              icon_name=icon_name, size=500, output_name=output_name)



def getCommentsImg(field, searchWord, icon_name, output_name):
    if not searchWord:
        raise AssertionError('出现异常啦！！！')
    sql = f"SELECT {field} FROM comments WHERE movieName='{searchWord}'"
    conn, cursor = get_conn()
    cursor.execute(sql)
    data = cursor.fetchall()
    text1 = ' '.join([row[0] for row in data if row[0] is not None])
    # text=' '.join(text1) OR  text=text1
    stylecloud.gen_stylecloud(text=' '.join(text1), collocations=False,
                              font_path='C:/Windows/Fonts/simhei.ttf',
                              icon_name=icon_name, size=500, output_name=output_name)