from . import homeData
from . import query
import pandas as ps

df = ps.DataFrame(homeData.getAllData(), columns=[
    'id',
    'directors',
    'rate',
    'title',
    'casts',
    'cover',
    'year',
    'types',
    'country',
    'lang',
    'time',
    'movieTime',
    'comment_len',
    'starts',
    'summary',
    'comments',
    'imgList',
    'detailLink'
])


def deleteTableId(id):
    sql = f'''DELETE FROM movies WHERE id = "{id}"'''
    query.querys(sql, [])
    return 'success'
