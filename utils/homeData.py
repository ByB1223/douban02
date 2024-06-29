from . import query
import json
import pandas as ps

def getAllData():
    def map_fn(item):
        item = list(item)
        if item[1] == None:
            item[1] = '无'
        else:
            item[1] = item[1].split(',')
        if item[4] == None:
            item[4] = '无'
        else:
            item[4] = item[4].split(',')
        item[7] = item[7].split(',')
        if item[8] == None:
            item[8] = '中国大陆'
        else:
            item[8] = item[8].split(',')
        if item[9] == None:
            item[9] = '汉语普通话'
        else:
            item[9] = item[9].split(',')
        item[13] = item[13].split(',')
        item[16] = item[16].split(',')
        item[15] = json.loads(item[15])
        return item
    allData = query.querys('select * from movies',[],'select')
    allData = list(map(map_fn,list(allData)))
    return allData


df = ps.DataFrame(getAllData(),columns=[
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

def getMaxRate():
    return df['rate'].astype(float).max()

def getMaxCast():
    allData = getAllData()
    casts = {}
    maxName = ''
    maxNum = 0
    for i in allData:
        for j in i[4]:
            if casts.get(j,-1) == -1:
                casts[j] = 1
            else:
                casts[j] = casts[j] + 1
    for k,v in casts.items():
        if int(v) > maxNum:
            maxNum = v
            maxName = k
    return maxName

def getMaxLang():
    allData = getAllData()
    langs = {}
    maxLang = ''
    maxNum = 0
    for i in allData:
        for j in i[9]:
            if langs.get(j, -1) == -1:
                langs[j] = 1
            else:
                langs[j] = langs[j] + 1
    for k, v in langs.items():
        if int(v) > maxNum:
            maxNum = v
            maxLang = k
    return maxLang

def getTypesAll():
    allData = getAllData()
    types = {}
    for i in allData:
        for j in i[7]:
            if types.get(j,-1) == -1:
                types[j] = 1
            else:
                types[j] = types[j] + 1
    return types.keys()

def getType_t():
    allData = getAllData()
    types = {}
    for i in allData:
        for j in i[7]:
            if types.get(j, -1) == -1:
                types[j] = 1
            else:
                types[j] = types[j] + 1
    data = []
    for k,v in types.items():
       data.append({
           'name':k,
           'value':v
       })
    return data

def getRate_t():
    allData = getAllData()
    rates = {}
    for i in allData:
        if rates.get(i[2], -1) == -1:
            rates[i[2]] = 1
        else:
            rates[i[2]] = rates[i[2]] + 1
    return rates.keys(),rates.values()

def getTableList():
    def map_fn(item):
        item[1] = '/'.join(item[1])
        item[4] = '/'.join(item[4])
        item[7] = '/'.join(item[7])
        item[8] = '/'.join(item[8])
        item[9] = '/'.join(item[9])
        return item
    allData = list(getAllData())
    allData = map(map_fn,allData)
    return list(allData)