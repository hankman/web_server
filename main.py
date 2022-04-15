
import os
import pickle
import pandas as pd
import datetime as dt
from math import log
from flask import Flask, render_template


WEB_SERVER_DIR = '/home/cfan/web_server'
DATA_DIR = '/home/cfan/notebooks/data'

# WEB_SERVER_DIR = '/home/fan/code/py/web_server'
# DATA_DIR = '/home/fan/code/py/notebooks/data'


RESOURCE_DIR = os.path.join(WEB_SERVER_DIR, 'resources')
FAVICON_FILE = os.path.join(RESOURCE_DIR, 'favicon.ico')
AVATAR_FILE = os.path.join(RESOURCE_DIR, 'avatar.png')
LOGO_FILE = os.path.join(RESOURCE_DIR, 'logo.jpg')

DATA_FILE = os.path.join(DATA_DIR, 'infect.pickle')
CNT_FILE = os.path.join(DATA_DIR, 'cnt.pickle')
DEBUG_FILE = os.path.join(DATA_DIR, 'grab_infect_data.html')

STATIC_FILE_PATH = os.path.join(WEB_SERVER_DIR, 'static')


W, R, O, G = 'white', '#ffdddd', '#ffdfbd', '#c0ffc0'

app = Flask(__name__)


def vague_search_print(comm, data):
    if comm != '*':
        return data[data.Community.str.contains(comm)]
    else:
        return data


def init_all_data():
    with open(DATA_FILE, 'rb') as f:
        all_data = pickle.load(f)
    update_date = all_data.Date.max().strftime('%Y-%m-%d')
    now = dt.datetime.combine(dt.date.today(), dt.time())
    passed_days = (now - all_data.groupby(['Dist', 'Community']).Date.max()).dt.days
    remaining_days = 14 - passed_days
    remaining_days.loc[remaining_days <= 0] = 0
    all_data = all_data.merge(
        remaining_days.rename('Remain').reset_index(), on=['Dist', 'Community'])
    all_data['Remain_str'] = all_data.Remain.astype(str) + ' 天'
    all_data['Date_str'] = pd.to_datetime(all_data.Date).dt.strftime('%-m月%-d日')
    return all_data, update_date, passed_days


def init_cnt_data():
    with open(CNT_FILE, 'rb') as f:
        cnt_data = pickle.load(f)
    df = cnt_data.loc[cnt_data.index.unique().sort_values(
        ascending=False)[:5]].reset_index().set_index(['Date', 'Kind']).unstack(
        ).T.fillna(0).astype(int)
    df.columns = [d.strftime('%-m月%-d日') for d in df.columns]
    df.index.names = (None, None)
    df_log = df.applymap(lambda x: log(x) if x != 0 else 0)
    styled_df = df.style.background_gradient(
        axis=None, cmap='Oranges',
        subset=([i for i in df.index if i[1] == 'BL'], df.columns),
        gmap=df_log, high=0.85).background_gradient(
            axis=None, cmap='Blues',
            subset=([i for i in df.index if i[1] == 'WZZ'], df.columns),
            gmap=df_log, high=0.85).format_index(
                formatter=lambda x: '确诊' if x == 'BL' else '无症状', level=1)
    return styled_df.to_html()


def init_static_data():
    static_data = {}
    for filename in os.listdir(STATIC_FILE_PATH):
        path = os.path.join(STATIC_FILE_PATH, filename)

        if os.path.isfile(path):
            with open(path, 'r') as f:
                static_data[filename] = f.read()
    return static_data


def get_result_data(place, all_data):
    place = place.strip()
    if place[-1] == '弄' or place[-1] == '号':
        place = place[:-1]
    data = vague_search_print(place, all_data)
    return data


def get_result_html(place, all_data):
    data = get_result_data(place, all_data)
    if data.shape[0] == 0:
        return '<span>(无感染记录或未收录地址。注意，输入地址请勿包含行政区。)</span>'
    else:
        data = data.sort_values(['Dist', 'Community', 'Date'], ascending=[True, True, False]).rename(
            columns={'Dist': '区', 'Community': '地址', 'Date_str': '报告日期', 'Remain_str': '解封剩余'})

        return data[['区', '地址', '解封剩余', '报告日期']].set_index(
            ['区', '地址', '解封剩余', '报告日期']).style.to_html()


def init_dist_data(all_data):
    dist_summary = all_data[
        all_data.Date.isin(sorted(all_data.Date.unique())[-5:])
    ].groupby(['Dist', 'Date']).size().rename('Counts').sort_index(
    ).reset_index().set_index(['Dist', 'Date']).unstack()
    dist_summary.columns = [d[1].strftime('%-m月%-d日') for d in dist_summary.columns]
    dist_summary.index.name = None
    dist_summary = dist_summary.style.background_gradient(
        axis=None, cmap='YlOrRd', high=0.85)
    return dist_summary.to_html()


ALL_DATA, UPDATE_DATE, PASSED_DAYS = init_all_data()
CNT_DATA = init_cnt_data()
DIST_DATA = init_dist_data(ALL_DATA)
STATIC_DATA = init_static_data()


@app.route('/')
def root():
    return render_template('main.html', search=True, logo_sameline=True, update_date=UPDATE_DATE)


@app.route('/dist')
def dist_summary():
    return render_template(
        'main.html', dist=True, title='各行政区感染数据统计', update_date=UPDATE_DATE,
        infect_table=DIST_DATA, cnt_table=CNT_DATA
    )


def processing_debug_request():
    with open(DEBUG_FILE, 'rb') as f:
        return f.read()


with open(FAVICON_FILE, 'rb') as f:
    FVC_DATA = f.read()


def processing_favicon():
    return FVC_DATA


with open(AVATAR_FILE, 'rb') as f:
    AVATAR_DATA = f.read()


with open(LOGO_FILE, 'rb') as f:
    LOGO_DATA = f.read()


def processing_avatar():
    return AVATAR_DATA


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


@app.route('/debug')
def debug_page():
    return processing_debug_request()


@app.route('/test')
def test_page():
    return render_template('main.html', search=True, logo_sameline=True, update_date=UPDATE_DATE)


@app.route('/favicon.ico')
def favicon():
    return processing_favicon()


@app.route('/apple-touch-icon.png')
def apple_icon():
    return processing_avatar()


@app.route('/backend')
def backend():
    return processing_backend()


@app.route('/search/<place>')
def query_place(place):
    return render_template(
        'main.html', long_search=True, title='"{}"的查询结果'.format(place),
        extra_notice="，将本页发送到桌面以快速查询",
        update_date=UPDATE_DATE,
        table_content=get_result_html(place, ALL_DATA))


EMPTY_PAGE = '<html><body style="text-align: center;font-size: 1rem"><h3>错误查询，请先输入地址。</h3></body></html>'
@app.route('/iframe_search/')
def iframe_wrong_search():
    return EMPTY_PAGE


@app.route('/iframe_search/<place>')
def ifram_search(place):
    return render_template('search-iframe.html', table_content=get_result_html(place, ALL_DATA))


@app.route('/img/logo.jpg')
def logo_img():
    return LOGO_DATA;


@app.route('/static/<file>')
def static_file(file):
    return STATIC_DATA[file]


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response
