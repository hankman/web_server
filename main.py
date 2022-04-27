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

REDIS = redis.Redis(host='localhost', port=6379, db=0)


template_loader = FileSystemLoader(searchpath='./templates/')
template_env =Environment(loader=template_loader)


app = Flask(__name__)


def get_updated_date():
    return REDIS.get('updated_date').decode('utf8')


def init_cnt_data():
    return REDIS.get('cnt_summary').decode('utf8')


def init_dist_data():
    return REDIS.get('dist_summary').decode('utf8')


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


def search_data(place):
    places = [i.strip() for i in place.split('|')]
    places = [place[:-1] if place[-1] == '弄' or place[-1] == '号' else place for place in places]
    return b''.join(chain.from_iterable([REDIS.mget(REDIS.keys('*{}*'.format(j))) for j in places]))


def get_result_html(place):
    data = search_data(place)

    if len(data) == 0:
        return ''

    data = pd.read_csv(
        io.BytesIO(data),
        names=['Dist', 'Community', 'Date'])
    data['Date_obj'] = pd.to_datetime(data['Date'])
    data = data.sort_values(
        ['Dist', 'Community', 'Date_obj'], ascending=[True, True, False]
        )[['Dist', 'Community', 'Date']]

    ret = data.to_csv(index=False, header=False)
    return ret


CNT_DATA = init_cnt_data()
DIST_DATA = init_dist_data()
RESOURCES_DATA = init_file_data(RESOURCES_DIR)


@app.route('/old/')
def old_root():
    return old_root.PAGE

old_root.PAGE = template_env.get_template('main.html').render(
    search=True, logo_sameline=True, url_prefix='', relative_to_root='.',
    switch_notice='。 如网页显示太慢，可以切换至<a href="/">新网页</a>')


@app.route('/')
def root():
    return root.PAGE

root.PAGE = template_env.get_template('main.html').render(
    search=True, logo_sameline=True,
    url_prefix='https://hankman.github.io/chenfan_info_web_resources',
    relative_to_root='.',
    switch_notice='。 如网页显示不正常，可以切换回<a href="/old/">旧版网页</a>')


@app.route('/old/dist/')
def old_dist_summary():
    return old_dist_summary.PAGE

old_dist_summary.PAGE = template_env.get_template('main.html').render(
        dist=True, infect_table=DIST_DATA, cnt_table=CNT_DATA, url_prefix='',
        relative_to_root='..'
    ).replace('{title}', '各行政区感染数据统计')


@app.route('/dist/')
def dist_summary():
    return dist_summary.PAGE

dist_summary.PAGE = template_env.get_template('main.html').render(
        dist=True, infect_table=DIST_DATA,
        cnt_table=CNT_DATA,
        url_prefix='https://hankman.github.io/chenfan_info_web_resources',
        relative_to_root='..'
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


@app.route('/data_processing')
def debug_page():
    with open(DEBUG_FILE, 'rb') as f:
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


@app.route('/search/<place>')
def search_page(place):
    return search_page.PAGE_TEMPLATE

search_page.PAGE_TEMPLATE = template_env.get_template('main.html').render(
    long_search=True, extra_notice="，将本页发送到桌面以快速查询",
    url_prefix='https://hankman.github.io/chenfan_info_web_resources',
    relative_to_root='..')


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
def lagacy_query1(place):
    return '服务器已升级，请重新加载页面'


@app.route('/update_date/')
@app.route('/old/update_date/')
def update_date():
    return get_updated_date()


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response
