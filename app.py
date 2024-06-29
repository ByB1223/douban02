import sys
import pymysql  # mysql
from pyecharts.charts import Bar, Timeline, Grid, Liquid, Pie, MapGlobe, Line  # flask
from flask import Flask, request, render_template, session, redirect, url_for  # PyECharts
from pyecharts import options as opts
import pandas as pd
from pythonProject.utils.word_cloud import getCommentsImg
from pythonProject.utils.word_cloud import getTitleImg
from pythonProject.utils.word_cloud import getCastsImg
from pythonProject.utils.homeData import *  # 工具
from pythonProject.utils.timeData import *
from pythonProject.utils.rateData import *
from pythonProject.utils.addressData import *
from pythonProject.utils.typeData import *
from pythonProject.utils.tablesData import *
from pythonProject.utils.actor import *

sys.path.append(r'E:\shixun\pythonProject\utils')
app = Flask(__name__, static_folder='static')
app.secret_key = "ywqq"

# 数据库连接
def get_conn():
    conn = pymysql.connect(host='localhost', user='root', password='123456', database='douban02', port=3306)
    cursor = conn.cursor()
    return conn, cursor

@app.route('/')
def rootRoute():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['passwordCheked']:
            return '两次密码不一致!'
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return redirect(url_for('register'))
        conn, cursor = get_conn()
        cursor.execute("SELECT username FROM users")
        data = cursor.fetchall()
        usernames = [user[0] for user in data]
        if username in usernames:  # 判断是否有相同的数据
            return '用户名已经存在！！'
        cursor.execute("INSERT INTO users(username,password) VALUES (%s,%s)", (username, password))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']  # 获取用户和密码
        password = request.form['password']
        if not username or not password:
            return redirect(url_for('login'))
        conn, cursor = get_conn()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

# 验证用户是否登录的装饰器
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # 如果未登录，则重定向到登录页面，并将原始URL作为next参数传递给登录页面
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function

#实现退出登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 实现首页
@app.route('/home')
@login_required
def home():
    username = session['username']  # 获取session的值
    allData = getAllData()  # 获取所有的电影数据
    maxRate = getMaxRate()  # 获取评分最高的值
    maxCast = getMaxCast()  # 获取出场最多的演员
    typesAll = getTypesAll()  # 获取电影种类
    maxLang = getMaxLang()  # 获取最多语言
    types = getType_t()  # 获取电影种类饼状图数据
    row, column = getRate_t()  # 电影评分折线图数据
    return render_template("home.html", username=username,
                           dataLen=len(allData), maxRate=maxRate,
                           maxCast=maxCast, typeLen=len(typesAll),
                           maxLang=maxLang, types=types,
                           row=list(row), column=list(column))


# 实现搜索
@app.route('/search/<int:searchId>', methods=["GET", "POST"])
@login_required
def search(searchId):
    username = session['username']
    allData = getAllData()  # 获取所有的电影数据
    data = []
    if request.method == 'GET':  # GET请求
        # 如果searchId为0，则渲染搜索页面，不进行搜索
        if searchId == 0:
            return render_template('search.html', username=username)
        # 遍历所有的数据 ，找到匹配的数据
        for i in allData:
            if i[0] == searchId:
                data.append(i)
        return render_template('search.html', data=data, username=username)
    else:  # POST请求
        searchWord = request.form['searchIpt'].strip()
        # 如果搜索词为空，则重定向回搜索页面
        if not searchWord:
            return redirect(url_for('search', searchId=searchId))

        # 定义过滤函数，用于过滤数据
        def filter_fn(item):
            if item[3].find(searchWord) == -1:
                return False
            else:
                return True

        # 使用过滤函数过滤数据
        data = list(filter(filter_fn, allData))
        return render_template('search.html', data=data, username=username)


# 实现时间分析表
@app.route('/time_t', methods=["GET", "POST"])
@login_required
def time_t():
    username = session['username']
    x, y = getTimeList()  # 历年产量统计
    movieTimeData = getMovieTimeList()  # 电影数据时长分布占比
    return render_template('time_t.html', username=username, x=list(x), y=list(y), movieTimeData=movieTimeData)

# 实现评分分析表
@app.route('/rate_t/<type>', methods=["GET", "POST"])
@login_required
def rate_t(type):
    username = session['username']
    typeAll = getTypesAll()  # 获取所有电影的类型
    rows, columns = getMean()
    x, y, y1 = getCountryRating()
    if type == 'all':
        row, column = getRate_t()
    else:
        row, column = getRate_tType(type)
    if request.method == 'GET':
        starts, movieName = getStart("长津湖")
    else:
        searchWord = request.form['searchIpt'].strip()
        if not searchWord:
            return redirect(url_for('rate_t'))
        starts, movieName = getStart(searchWord)
    return render_template('rate_t.html', username=username,
                           typeAll=typeAll, type=type, row=list(row), column=list(column),
                           starts=starts, movieName=movieName, rows=rows, columns=columns,
                           x=x, y=y, y1=y1)

# 实现地图分析表
@app.route('/address_t', methods=["GET", "POST"])
@login_required
def address_t():
    username = session['username']
    row, column = getAddressData()  # 电影拍摄地统计图
    rows, columns = getLangData()  # 电影语言统计图
    return render_template('address_t.html', username=username,
                           row=row, column=column, rows=rows, columns=columns)

# 实现类型分析表
@app.route('/type_t', methods=["GET", "POST"])
@login_required
def type_t():
    username = session['username']
    result = getMovieTypeData()
    return render_template('type_t.html', username=username, result=result)

@app.route('/actor_t',methods=["GET", "POST"])
@login_required
def actor_t():
    username = session['username']
    x, y = getAllActorMovieNum()#获取所有导演的电影数据
    x1, y1 = getAllDirectorMovieNum()##获取所有演员的电影数据
    return render_template('actor_t.html', username=username, x=x, y=y, x1=x1, y1=y1)

#实现数据操作
@app.route('/tables/<int:id>')
@login_required
def tables(id):
    username = session['username']
    if id == 0:
        tablelist = getTableList()
    else:
        deleteTableId(id)
        tablelist = getTableList()
    return render_template('tables.html', tablelist=tablelist,username=username)



@app.route('/title_c',methods=["GET", "POST"])
@login_required
def title_c():
    username = session['username']
    #将绘制词云的操作封装成方法，在下面进行调用
    getTitleImg('title','fas fa-fish','./static/images/title.png')
    return render_template('title_c.html',username=username)


@app.route('/casts_c',methods=["GET", "POST"])
@login_required
def casts_c():
    username = session['username']
    getCastsImg('casts','fas fa-crow','./static/images/yanyuan.png')
    return render_template('casts_c.html', username=username)

@app.route('/comments_c', methods=["GET", "POST"])
@login_required
def comments_c():
    username = session['username']
    if request.method == 'GET':
        return render_template('comments_c.html', username=username)
    else:
        searchWord = request.form['searchIpt'].strip()
        if not searchWord or searchWord == "":
            return redirect(url_for('comments_c'))
        try:
            getCommentsImg('commentContent', searchWord, 'fab fa-qq', './static/images/ciyun.png')
        except AssertionError as e:
            return redirect(url_for('comments_c'))
    return render_template('comments_c.html', username=username)



@app.route('/analysis1', methods=["GET", "POST"])
@login_required
def index():  # 首页界面
    allData = getAllData()  # 获取所有的电影数据
    allData = len(allData)  # 长度
    maxRate = getMaxRate()  # 获取评分最高的值
    typesAll = getTypesAll()  # 获取电影种类
    typesAll = len(typesAll)  # 长度
    maxLang = getMaxLang()  # 获取最多语言
    maxLang = maxLang[:2]
    chart_html1 = typedata()
    chart_html2 = yeardata()
    chart_html3 = langdata()
    chart_html4 = commentsdata()
    worlddata()
    data = {
        "moviesNum": allData,
        "maxScore": maxRate,
        "moviesType": typesAll,
        "maxLang": maxLang}
    return render_template('analysis1.html',data=data,chart_html1=chart_html1,chart_html2=chart_html2,chart_html3=chart_html3,chart_html4=chart_html4)
def typedata():
    data = pd.read_csv("./tools/d1.csv", encoding='utf8')
    top_data = data.head()
    # 转换PyECharts饼状图需要的数据格式
    pie_data = list(zip(top_data['类型'], top_data['数量']))
    pie_chart = Pie(init_opts=opts.InitOpts(width="500px", height="400px"))
    # 添加数据和配置项
    pie_chart.add("", pie_data,
                  radius=["30%", "60%"],
                  center=["45%", "50%"],
                  label_opts=opts.LabelOpts(formatter="{b}:{c}({d}%)"))
    # 设置全局配置项，比如标题
    pie_chart.set_global_opts(
        title_opts=opts.TitleOpts(title="", pos_left="center", pos_top="5%"),
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(font_family="宋体")
        )
    )
    # 生成图表
    pie_chart.render("static/html/movietypes.html")
    chart_html = pie_chart.render_embed()
    return chart_html
# 实现年份电影数据量
def yeardata():
    data = pd.read_csv('./tools/d2.csv', encoding='utf8')
    # 提取年份和数量数据
    years = data['年份'].tolist()
    counts = data['数量'].tolist()
    # 创建Bar对象
    bar = Bar(init_opts=opts.InitOpts(width="500px", height="400px"))
    # 添加xy轴数据
    bar.add_xaxis(years)
    bar.add_yaxis('数量', counts)
    #设置全局配置项
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title=""),
        xaxis_opts=opts.AxisOpts(name="年份"),
        yaxis_opts=opts.AxisOpts(name="数量"))
    #设置系列配置项
    bar.set_series_opts(
        animation_opts=opts.AnimationOpts(animation_delay=5000,animation_duration=5000,animation_easing='bounceInOut')
    )
    # 生成图表
    bar.render("static/html/yeardata.html")
    chart_html = bar.render_embed()
    return chart_html

# 语言水球图
def langdata():
    # 读取数据
    data = pd.read_csv("./tools/d3.csv", encoding='utf8')
    # 提取语言和数量数据，并转换成元组列表
    result = [(row["语言"], row["数量"]) for index, row in data.iterrows()]
    # 计算最大值，用于确定水球图的范围
    max_value = result[0][1] + result[1][1]
    # 创建汉语普通话水球图
    liquid1 = Liquid(init_opts=opts.InitOpts(width="100px", height="100px"))
    liquid1.add(
        "",
        [result[0][1] / max_value],
        center=["14%", "35%"],
        is_outline_show=False,
        shape='pin',
        label_opts=opts.LabelOpts(font_size=20),
        tooltip_opts=opts.TooltipOpts(formatter="{a} <br/>{b}: {c}%"),
        color=["#FF6347"],  # 设置颜色
    )
    liquid1.set_global_opts(title_opts=opts.TitleOpts(title=result[0][0], pos_left="10%", pos_top="5%"))

    # 创建英语水球图
    liquid2 = Liquid(init_opts=opts.InitOpts(width="100px", height="100px"))
    liquid2.add(
        "",
        [result[1][1] / max_value],
        center=["35%", "35%"],
        is_outline_show=False,
        shape='pin',
        label_opts=opts.LabelOpts(font_size=20),
        tooltip_opts=opts.TooltipOpts(formatter="{a} <br/>{b}: {c}%"),
        color=["#4682B4"],  # 设置颜色
    )
    liquid2.set_global_opts(title_opts=opts.TitleOpts(title=result[1][0], pos_left="30%", pos_top="5%"))

    grid = (
        Grid()
        .add(liquid1, grid_opts=opts.GridOpts())
        .add(liquid2, grid_opts=opts.GridOpts())
    )
    # 渲染图表到HTML文件
    grid.render("static/html/liquid_chart.html")
    chart_html = grid.render_embed()
    return chart_html

# 电影评论折线图
def commentsdata():
    # 读取数据
    data = pd.read_csv("./tools/d4.csv", encoding='utf8')
    # 创建Timeline实例，并设置宽度和高度
    timeline = Timeline(init_opts=opts.InitOpts(width='520px', height='380px'))
    for i in range(len(data)):
        # 获取当前日期
        current_date = datetime.now().strftime('%Y-%m-%d')
        # 提取电影名和数量数据
        names = data["电影"][:i + 1].tolist()
        values = data["数量"][:i + 1].tolist()
        # 创建折线图实例
        line = Line()
        line.add_xaxis(names)
        line.add_yaxis("", values, is_smooth=True, symbol_size=10,
                       linestyle_opts=opts.LineStyleOpts(width=3, color="#FF5722"))
        line.set_global_opts(
            title_opts=opts.TitleOpts(title=""),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0, font_size=12),
                                     axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(width=2))),
            yaxis_opts=opts.AxisOpts(name="数量", min_=1000000, axislabel_opts=opts.LabelOpts(rotate=0, font_size=9),
                                     axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(width=2))),
        )
        # 添加折线图到Timeline中
        timeline.add(line, current_date)
    # 添加Timeline的选项，设置自动播放
    timeline.add_schema(is_auto_play=True, play_interval=2000)
    timeline.render("static/html/movie_duration.html")
    chart_html = timeline.render_embed()
    return chart_html

def worlddata():
    data = pd.read_csv("./tools/d5.csv", encoding='utf8')
    # 将DataFrame转换为列表
    data_list = data.values.tolist()
    # 转换成你期望的结构
    result = [(row[0], row[1]) for row in data_list]
    # 提供的数据
    top1 = ['China', 'Russia', 'Canada', 'United', 'States', 'Brazil', 'Australia', 'India', 'Argentina', 'Kazakhstan']
    # 将 top_data 中的国家名称替换为 top1中对应位置的国家名称
    replaced_top_data = []
    for i in range(len(result)):
        replaced_top_data.append((top1[i], result[i][1]))
    low, high = min([x[1] for x in replaced_top_data]), max([x[1] for x in replaced_top_data])
    map3d = MapGlobe(init_opts=opts.InitOpts(width="400px", height="400px"))
    map3d.add_schema().add(
        maptype="world",
        series_name="",
        data_pair=replaced_top_data,
        is_map_symbol_show=False,
        label_opts=opts.LabelOpts(is_show=False),
    ).set_series_opts(tooltip_opts=opts.TooltipOpts(formatter='{b}: {c}')).set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            min_=low,
            max_=high,
            range_text=["max", "min"],
            is_calculable=True,
            range_color=["#0000ff", "#00ff00"],
        )
    )
    map3d.render("static/html/map3d.html")

# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True, port=9089)