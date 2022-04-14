
import os
import pickle
import pandas as pd
import datetime as dt
from math import log
from flask import Flask


RESOURCE_DIR = '/home/cfan/web_server/resources'
DATA_DIR = '/home/cfan/notebooks/data'

# RESOURCE_DIR = '/home/fan/code/py/web_server/resources'
# DATA_DIR = '/home/fan/code/py/notebooks/data'


FAVICON_FILE = os.path.join(RESOURCE_DIR, 'favicon.ico')
AVATAR_FILE = os.path.join(RESOURCE_DIR, 'avatar.png')
LOGO_FILE = os.path.join(RESOURCE_DIR, 'logo.jpg')


DATA_FILE = os.path.join(DATA_DIR, 'infect.pickle')
CNT_FILE = os.path.join(DATA_DIR, 'cnt.pickle')
DEBUG_FILE = os.path.join(DATA_DIR, 'grab_infect_data.html')


W, R, O, G = 'white', '#ffdddd', '#ffdfbd', '#c0ffc0'
FR, FO, FG = '#ff8d8d', '#eeab65', '#4adc4a'


MAIN_PAGE_TEMPLATE = '''
<html style="overflow: hidden">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        {header}</head>
    <body style="height: 100%;display: flex;flex-direction: column;font-size: 1rem;margin: 1rem;">
        <div style="text-align: center;flex: 1 1 auto;margin-bottom: 0.75rem;display: flex;flex-direction: column;width: 100%;">{content}</div>
        <div style="text-align: center;margin-bottom: 1.5rem;font-size: 0.75rem;border-top: solid 0.1rem;width: 100%;">
            <div><a href="https://beian.miit.gov.cn/" target="_blank">沪ICP备2022007631号-1|©2022 chenfan.info 版权所有</a>
            </div>
        </div>
    </body>
</html>'''


DEFAULT_PAGE = MAIN_PAGE_TEMPLATE.format(
    header='',
    content='''
<div style="border-bottom: solid 0.1rem;padding: 0.3rem">
    <div style="text-align: center;">
        <h1 style="display: inline-block;position: relative;margin: 0.8rem">
            <a href="/" style="position: absolute;top: -1rem;left: -5rem">
                <img src="/img/logo.jpg" alt="logo" style="height: 4rem;">
            </a>查询感染记录
        </h1>
    </div>
    <div style="font-size: 0.75em; font-style: italic">
        <div>*使用前请仔细阅读<a href="/inst.html">本站使用说明</a></div>
    </div>
    <div style="margin-top: 0.5rem">
        <label type="text" for="address">输入查询地址：</label>
        <input id="address" name="address" required autocomplete="address" autofocus type="text" placeholder="例：山阴路" style="outline: none !important;"/>
        <div>
            <div style="margin: 0.5rem">数据更新到：<a href="/dist">{}</a></div>
        </div>
        <div style="display: inline-block;position: relative">
            <button id="search" style="height: 2rem;background-color: white;border-radius: 0.8rem;border: solid 0.3rem;position: absolute;left: 50%;transform: translateX(-50%);width: 8rem;color: black">查询</button>
            <button id="long_search" style="height: 2rem;background-color: white;border-radius: 0.8rem;border: solid 0.3rem;position: relative;left: 8rem;color: black">收藏页</button>
        </div>
    </div>
</div>
<div style="flex: 1 1 auto;display: flex;margin-top: 0.5rem">
    <iframe id="result" src="about:blank" style="flex: 1 1 auto; border: none"></iframe>
</div>

<script>

var allow_query = true

const button = document.getElementById("search");
const long_search_button = document.getElementById("long_search");
const addr_input = document.getElementById("address")

const disable_query = () => {{
    allow_query = false
    button.disabled = true;
    button.style.backgroundColor = "#cfcfcf"
}};

const enable_query = () => {{
    allow_query = true
    button.disabled = false;
    button.style.backgroundColor = "white"
}};

var flash_cnt = 0;
var curr_timer = null;

const change_input_bg = () => {{
    if (flash_cnt === 0) {{
        curr_timer = null;
        return
    }}
    if (flash_cnt % 2 === 0) {{
        addr_input.style.backgroundColor = "red"
    }}
    else {{
        addr_input.style.backgroundColor = "white"
    }}
    flash_cnt -= 1;
    curr_timer = setTimeout(change_input_bg, 100)
}}

const flash_input = () => {{
    if (curr_timer != null) {{
        return
    }}
    flash_cnt = 6;
    change_input_bg();
}}


function search_address()
{{
    if (!allow_query) return;
    if (addr_input.value == null || addr_input.value == "") {{
        flash_input();
        return;
    }}
    document.getElementById("result").src = "/iframe_search/" + addr_input.value
    disable_query()
    setTimeout(enable_query, 3000)
}}

document.getElementById("address").addEventListener(
    "keyup", function(event) {{
    	if (event.keyCode === 13 && allow_query) {{
            search_address();
        }}
    }})
button.addEventListener("click", search_address)

long_search_button.addEventListener("click", function() {{
        var addr = addr_input.value
        if (addr_input.value == null || addr_input.value == "") {{
            flash_input();
            return;
        }}
        window.location.pathname = ("/search/" + addr)
    }})

</script>
''')


TEST_PAGE_TEMPLATE = MAIN_PAGE_TEMPLATE


TABLE_REMAIN_STYLE = f'''
    .curr_status {{
        font-size: 0.7rem;
        font-weight: 300;
    }}

    .fkq {{
        color: {FR}
    }}

    .gkq {{
        color: {FO}
    }}

    .ffq {{
        color: {FG}
    }}
'''


TABLE_HEADER = f'''
<style type="text/css">
    body {{
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 1rem;
    }}

    table {{
        border-collapse: collapse;
        border: solid 0.2rem;
        width: 100%;
        max-width: 35rem;
    }}

    thead {{
        background-color: #efefef
    }}

    th {{
        padding: 0.1rem 0.2rem;
        border: solid 0.1rem;
        font-size: 1rem;
    }}

    thead tr:nth-child(1) {{
        background-color: white;
    }}

    thead tr:nth-child(1) th {{
        border: hidden;
        border-bottom: solid 0.1rem;
    }}

    tbody tr th:nth-last-child(1) {{
        white-space: nowrap;
    }}

    tbody tr th:nth-last-child(2) {{
        white-space: nowrap;
    }}

    {TABLE_REMAIN_STYLE}
</style>'''


DIST_TABLE_HEADER = f'''
<style type="text/css">
    body {{
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 1rem;
    }}

    table {{
        border-collapse: collapse;
        border: solid 0.2rem;
        background-color: honeydew;
    }}

    td, th {{
        padding: 0.1rem 0.2rem;
        border: solid 0.1rem;
        font-size: 0.9rem;
        white-space: nowrap;
    }}

    tr th:nth-child(1) {{
        white-space: normal;
    }}

    {TABLE_REMAIN_STYLE}
</style>'''


TABLE_HEADER_TEMP_STR = TABLE_HEADER.replace('{', '{{').replace('}', '}}')


IFRAME_PAGE_TEMPLATE = '''
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
{}
</head>
<body style="font-size: 1rem">
<div style="overflow-y:auto;overflow-x: hidden;width: 100%;display: flex;flex-direction: column;align-items: center">{{}}</div>
</body>
</html>'''.format(TABLE_HEADER_TEMP_STR)


TEST_PAGE = TEST_PAGE_TEMPLATE.format(
    header=TABLE_HEADER,
    content='''<h1>查询感染记录</h1>
<div>
<label type="text" for="address">输入查询地址：</label>
<input id="address" name="address" required autocomplete="address" autofocus type="text" placeholder="例:山阴路"/>
<p>数据更新到：{}</p>
<button id='search'>查询</button>
<div>
<iframe id="result" src="about:blank" style="height: 100%; width: 100%; border: none"></iframe>
</div>
</div>

<script>
function search_address()
{{
    var addr = document.getElementById("address").value
    document.getElementById("result").src = "/iframe_search/" + addr
}}

document.getElementById("address").addEventListener(
    "keyup", function(event) {{
    	if (event.keyCode === 13) {{
            search_address();
            this.dispatchEvent(event)
        }}
    }})
document.getElementById("search").addEventListener(
	"click", search_address)
</script>
''')


app = Flask(__name__)


def vague_search_print(comm, data):
    if comm != '*':
        df = data[data.Community.str.contains(comm)].set_index(
            ['Dist', 'Community', 'Remain', 'Date']).sort_index(
                ascending=[True, True, True, False])
    else:
        df = data.set_index(
            ['Dist', 'Community', 'Remain', 'Date']).sort_index(
                ascending=[True, True, True, False])
    df.index.names = ['区', '地址', '解封剩余', '报告日期']
    return df


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


def get_result_data(place, all_data):
    place = place.strip()
    if place[-1] == '弄' or place[-1] == '号':
        place = place[:-1]
    data = vague_search_print(place, all_data)
    return data


def get_format(d):
    if d >= 14:
        return f'background-color: {G}'

    color_band = [f'{W} 0%']
    curr_p = d * 7

    def append_cell(color_band, color, curr_p):
        color_band.append(f'{W} {curr_p}%')
        color_band.append(f'{color} {curr_p}%')
        curr_p += 6
        color_band.append(f'{color} {curr_p}%')
        color_band.append(f'{W} {curr_p}%')
        return curr_p + 1

    color = R if d < 7 else O

    for i in range(14 - d):
        curr_p = append_cell(color_band, color, curr_p)

    color_band.append(f'{W} {curr_p}%')

    return f"background: linear-gradient(90deg, {','.join(color_band)});"


class formatter:
    def __init__(self, passed_days):
        self.passed_days = passed_days
        self.app_cnt = 0
        self.Dist = []

    def __call__(self, s):
        self.app_cnt += 1
        if self.app_cnt == 2:
            ret = []
            for dist, community in zip(self.Dist, s):
                d = self.passed_days.loc[dist, community]
                ret.append(get_format(d))
            return pd.Series(ret, index=s.index)
        elif self.app_cnt == 1:
            self.Dist = s

        return pd.Series('', index=s.index)


def get_result_html(place, all_data, passed_days):
    data = get_result_data(place, all_data)
    if data.shape[0] == 0:
        content = '<span>(无感染记录或未收录地址。注意，输入地址请勿包含行政区。)</span>'
    else:
        fmt = formatter(passed_days)
        content = data.style.apply_index(fmt).format_index(
            formatter={
                '报告日期': lambda x: x.strftime('%-m月%-d日'),
                '解封剩余': lambda x: f'{x} 天 {"封控区" if x > 7 else ("管控区" if x > 0 else "防范区")}'
            }).to_html().replace(
                '封控区', '<div class="curr_status">当前：<span class="fkq">封控区</span></div>').replace(
                '管控区', '<div class="curr_status">当前：<span class="gkq">管控区</span></div>').replace(
                '防范区', '<div class="curr_status">当前：<span class="ffq">防范区</span></div>')
    return content


def init_dist_data(all_data, cnt_data):
    dist_summary = all_data[
        all_data.Date.isin(sorted(all_data.Date.unique())[-5:])
    ].groupby(['Dist', 'Date']).size().rename('Counts').sort_index(
    ).reset_index().set_index(['Dist', 'Date']).unstack()
    dist_summary.columns = [d[1].strftime('%-m月%-d日') for d in dist_summary.columns]
    dist_summary.index.name = None
    dist_summary = dist_summary.style.background_gradient(
        axis=None, cmap='YlOrRd', high=0.85)

    return MAIN_PAGE_TEMPLATE.format(
        header=DIST_TABLE_HEADER,
        content='''
        <a href="/"><img src="/img/logo.jpg" alt="logo" style="height: 4rem;"></a>
        <h1 style="margin: 0">各行政区感染数据统计</h1>
        <div style="font-size: 0.75em; font-style: italic">
            <div>*使用前请仔细阅读<a href="/inst.html">本站使用说明</a></div>
        </div>
            <div style="overflow-y: auto;overflow-x: hidden;flex: 1 1 auto;height: 0;align-items: center;display: flex;flex-direction: column;margin-top: 1rem">
            <div><h2>各区感染小区数统计（单位：小区）</h2></div>
            <div id="table1">
                \n{infect_table}
            </div>
            <div id="table2"><h2>各区确诊和无症状人数统计（单位：人）</h2></div>
            <div>
                \n{cnt_table}
            </div>
        </div>'''.format(infect_table=dist_summary.to_html(), cnt_table=cnt_data))


ALL_DATA, UPDATE_DATE, PASSED_DAYS = init_all_data()
CNT_DATA = init_cnt_data()
ROOT_PAGE = DEFAULT_PAGE.format(UPDATE_DATE)
DIST_SUMMARY_PAGE = init_dist_data(ALL_DATA, CNT_DATA)


SEARCH_PAGE = MAIN_PAGE_TEMPLATE.format(
    header=TABLE_HEADER_TEMP_STR,
    content='''
<div style="border-bottom: solid 0.1rem;padding: 0.3rem">
    <a href="/"><img src="/img/logo.jpg" alt="logo" style="height: 4rem;"></a>
    <h1 style="margin: 0">"{{title}}"的查询结果</h1>
    <div style="font-size: 0.75em; font-style: italic">
        <div>*使用前请仔细阅读<a href="/inst.html">本站使用说明</a></div>
    </div>
    <div style="margin: 0.8rem;">数据更新至：<a href="/dist">{}</a></div>
</div>
<div style="flex: 1 1 auto;margin-top: 0.5rem;display: flex;flex-direction: column;align-items:center;height: 0">
    <div style="overflow-y: auto;overflow-x: hidden;width: 100%;display: flex;flex-direction: column;align-items: center">
        {{content}}
    </div>
</div>
'''.format(UPDATE_DATE))


@app.route('/')
def root():
    return ROOT_PAGE


@app.route('/dist')
def dist_summary():
    return DIST_SUMMARY_PAGE


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
    return TEST_PAGE.format(UPDATE_DATE);


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
    return SEARCH_PAGE.format(
        title=place, content=get_result_html(place, ALL_DATA, PASSED_DAYS))


EMPTY_PAGE = '<html><body style="text-align: center;font-size: 1rem"><h3>错误查询，请先输入地址。</h3></body></html>'
@app.route('/iframe_search/')
def iframe_wrong_search():
    return EMPTY_PAGE


@app.route('/iframe_search/<place>')
def ifram_search(place):
    return IFRAME_PAGE_TEMPLATE.format(
        get_result_html(place, ALL_DATA, PASSED_DAYS))


@app.route('/img/logo.jpg')
def logo_img():
    return LOGO_DATA;


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response
