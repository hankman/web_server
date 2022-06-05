import os
import pandas as pd
import json
from itertools import chain
import io

from flask import Flask, Response
from jinja2 import FileSystemLoader, Environment
import redis


with open(os.path.expanduser('/etc/web_server/server.json')) as f:
    server_conf = json.load(f)


DATA_DIR = server_conf['DATA_DIR']
RESOURCES_DIR = server_conf['RESOURCES_DIR']

DATA_FILE = os.path.join(DATA_DIR, 'infect.pickle')
CNT_FILE = os.path.join(DATA_DIR, 'cnt.pickle')
DEBUG_FILE = os.path.join(DATA_DIR, 'grab_infect_data.html')
BJ_DEBUG_FILE = os.path.join(DATA_DIR, 'grab_beijing_data.html')


REDIS = redis.Redis(host='localhost', port=6379, db=0)
BJ_REDIS = redis.Redis(host='localhost', port=6379, db=1)


template_loader = FileSystemLoader(searchpath='./templates/')
template_env =Environment(loader=template_loader)


app = Flask(__name__)


def get_updated_date(data_server):
    return data_server.get('updated_date').decode('utf8')


def init_cnt_data():
    return REDIS.get('cnt_summary').decode('utf8')


def init_dist_data():
    return REDIS.get('dist_summary').decode('utf8')


def init_daily_data():
    return REDIS.get('daily_summary').decode('utf8')


def init_bj_dist_data():
    return BJ_REDIS.get('dist_summary').decode('utf8')


def init_bj_inf_data():
    return BJ_REDIS.get('daily_inf').decode('utf8')


def get_file_mime_type(file):
    mimetype = 'text/html'
    if file.endswith('.ico'):
        mimetype = 'image/x-icon'
    elif file.endswith('.js'):
        mimetype = 'text/javascript'
    elif file.endswith('.png'):
        mimetype = 'image/png'
    elif file.endswith('.jpg'):
        mimetype = 'image/jpg'
    elif file.endswith('.css'):
        mimetype = 'text/css'
    return mimetype


def init_file_data(directory):
    file_data = {}
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)

        if os.path.isfile(path):
            with open(path, 'rb') as f:
                file_data[filename] = (f.read(), get_file_mime_type(filename))
    return file_data


def search_data(place, data_server):
    places = [i.strip() for i in place.split('|')]
    places = [place[:-1] if place[-1] == '弄' or place[-1] == '号' else place for place in places]
    return b''.join(chain.from_iterable([data_server.mget(data_server.keys('*{}*'.format(j))) for j in places]))


def get_result_html_sorted(place, data_server, col_list):
    data = search_data(place, data_server)

    if len(data) == 0:
        return ''

    data = pd.read_csv(io.BytesIO(data), names=col_list)
    data['Date_obj'] = pd.to_datetime(data['Date'])
    data = data.sort_values(
        ['Dist', 'Community', 'Date_obj'], ascending=[True, True, False]
        )[col_list]

    ret = data.to_csv(index=False, header=False)
    return ret


def get_result_html(place):
    return get_result_html_sorted(place, REDIS, ['Dist', 'Community', 'Date'])


def bj_get_result_html(place):
    return get_result_html_sorted(place, BJ_REDIS, ['Dist', 'Community', 'Date', 'QZ', 'WZZ'])



CNT_DATA = init_cnt_data()
DIST_DATA = init_dist_data()
DAILY_DATA = init_daily_data()
RESOURCES_DATA = init_file_data(RESOURCES_DIR)
BJ_DIST_DATA = init_bj_dist_data()
BJ_INF_DATA = init_bj_inf_data()


@app.route('/old/')
def old_root():
    return old_root.PAGE

old_root.PAGE = template_env.get_template('main.html').render(
    search=True, logo_sameline=True, url_prefix='', relative_to_root='.',
    switch_notice='。 切换至<a href="../">新网页</a>')


@app.route('/bj/old/')
def old_bj_root():
    return old_bj_root.PAGE

old_bj_root.PAGE = template_env.get_template('main.html').render(
    search=True, logo_sameline=True, url_prefix='', relative_to_root='.',
    switch_notice='。 切换至<a href="../">新网页</a>', bj=True)


@app.route('/')
def root():
    return root.PAGE

root.PAGE = template_env.get_template('main.html').render(
    search=True, logo_sameline=True,
    url_prefix='https://hankman.github.io/chenfan_info_web_resources',
    relative_to_root='.',
    switch_notice='。 切换回<a href="./old/">旧版网页</a>')


@app.route('/bj/')
def bj_root():
    return bj_root.PAGE

bj_root.PAGE = template_env.get_template('main.html').render(
    search=True, logo_sameline=True,
    url_prefix='https://hankman.github.io/chenfan_info_web_resources',
    relative_to_root='.',
    switch_notice='。 切换回<a href="./old/">旧版网页</a>',
    bj=True)


@app.route('/old/dist/')
def old_dist_summary():
    return old_dist_summary.PAGE

old_dist_summary.PAGE = template_env.get_template('main.html').render(
        dist=True, infect_table=DIST_DATA, cnt_table=CNT_DATA, daily_table=DAILY_DATA,
        url_prefix='', relative_to_root='..'
    ).replace('{title}', '各行政区感染数据统计')


@app.route('/dist/')
def dist_summary():
    return dist_summary.PAGE

dist_summary.PAGE = template_env.get_template('main.html').render(
        dist=True, infect_table=DIST_DATA,
        cnt_table=CNT_DATA,
        daily_table=DAILY_DATA,
        url_prefix='https://hankman.github.io/chenfan_info_web_resources',
        relative_to_root='..'
    ).replace('{title}', '各行政区感染数据统计')


@app.route('/bj/old/dist/')
def bj_old_dist_summary():
    return bj_old_dist_summary.PAGE

bj_old_dist_summary.PAGE = template_env.get_template('main.html').render(
        dist=True, dist_table=BJ_DIST_DATA, bj_daily_inf=BJ_INF_DATA,
        url_prefix='', relative_to_root='..', bj=True
    ).replace('{title}', '各行政区感染数据统计')


@app.route('/bj/dist/')
def bj_dist_summary():
    return bj_dist_summary.PAGE

bj_dist_summary.PAGE = template_env.get_template('main.html').render(
        dist=True,
        dist_table=BJ_DIST_DATA,
        bj_daily_inf=BJ_INF_DATA,
        url_prefix='https://hankman.github.io/chenfan_info_web_resources',
        relative_to_root='..',
        bj=True
    ).replace('{title}', '各行政区感染数据统计')


def processing_backend():
    with open(__file__, 'r') as f:
        return '<html><body>{}</body></html>'.format(
            ''.join(['<pre>{}</pre>'.format(line.replace(
                '&', '&#38;').replace(
                    '<', '&#60;').replace(
                        '>', '&#62;').replace(
                            '"', '&#34;').replace(
                                "'", '&#39;') if line.strip() else '<br/>'
            ) for line in f]))


@app.route('/search_data/<place>')
@app.route('/old/search_data/<place>')
def query_data(place):
    return get_result_html(place)


@app.route('/bj/search_data/<place>')
@app.route('/bj/old/search_data/<place>')
def bj_query_data(place):
    return bj_get_result_html(place)


@app.route('/data_processing')
def debug_page():
    with open(DEBUG_FILE, 'rb') as f:
        return f.read()


@app.route('/data_processing_beijing')
def beijing_debug_page():
    with open(BJ_DEBUG_FILE, 'rb') as f:
        return f.read()


@app.route('/backend')
def backend():
    return processing_backend()


@app.route('/old/search/<place>')
def old_search_page(place):
    return old_search_page.PAGE_TEMPLATE


old_search_page.PAGE_TEMPLATE = template_env.get_template('main.html').render(
    long_search=True, extra_notice="，将本页发送到桌面以快速查询",
    url_prefix='', relative_to_root='..')


@app.route('/bj/old/search/<place>')
def bj_old_search_page(place):
    return bj_old_search_page.PAGE_TEMPLATE


bj_old_search_page.PAGE_TEMPLATE = template_env.get_template('main.html').render(
    long_search=True, extra_notice="，将本页发送到桌面以快速查询",
    url_prefix='', relative_to_root='..', bj=True)


@app.route('/search/<place>')
def search_page(place):
    return search_page.PAGE_TEMPLATE

search_page.PAGE_TEMPLATE = template_env.get_template('main.html').render(
    long_search=True, extra_notice="，将本页发送到桌面以快速查询",
    url_prefix='https://hankman.github.io/chenfan_info_web_resources',
    relative_to_root='..')


@app.route('/bj/search/<place>')
def bj_search_page(place):
    return bj_search_page.PAGE_TEMPLATE

bj_search_page.PAGE_TEMPLATE = template_env.get_template('main.html').render(
    long_search=True, extra_notice="，将本页发送到桌面以快速查询",
    url_prefix='https://hankman.github.io/chenfan_info_web_resources',
    relative_to_root='..', bj=True)


@app.route('/resources/<file>')
def resource(file):
    res_data = RESOURCES_DATA[file]
    return Response(res_data[0], mimetype=res_data[1])


@app.route('/apple-touch-icon<size>')
def app_icons(size):
    res_data = RESOURCES_DATA['apple-touch-icon.png']
    return Response(res_data[0], mimetype=res_data[1])


@app.route('/favicon.ico')
def favicon():
    res_data = RESOURCES_DATA['favicon.ico']
    return Response(res_data[0], mimetype=res_data[1])


@app.route('/iframe_search/<place>')
@app.route('/old/iframe_search/<place>')
def legacy_query1(place):
    return '服务器已升级，请重新加载页面'


def get_update_date_resp(data_server):
    response = Response(get_updated_date(data_server))
    response.cache_control.no_cache = True;
    return response


@app.route('/update_date/')
@app.route('/old/update_date/')
def sh_update_date():
    return get_update_date_resp(REDIS)


@app.route('/bj/update_date/')
@app.route('/bj/old/update_date/')
def bj_update_date():
    return get_update_date_resp(BJ_REDIS)


@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.cache_control.max_age = 300
    return response
