
import os
import pickle
import pandas as pd
from flask import Flask


RESOURCE_DIR = '/home/cfan/web_server/resources'
DATA_DIR = '/home/cfan/notebooks/data'

# RESOURCE_DIR = '/home/fan/code/py/web_server/resources'
# DATA_DIR = '/home/fan/code/py/notebooks/data'


FAVICON_FILE = os.path.join(RESOURCE_DIR, 'favicon.ico')
AVATAR_FILE = os.path.join(RESOURCE_DIR, 'avatar.png')
LOGO_FILE = os.path.join(RESOURCE_DIR, 'logo.jpg')


DATA_FILE = os.path.join(DATA_DIR, 'infect.pickle')
DEBUG_FILE = os.path.join(DATA_DIR, 'grab_infect_data.html')


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
        <input id="address" name="address" required autocomplete="address" autofocus type="text" placeholder="例：山阴路" style="outline: none !important;box-shadow: 0 0 0.3rem black;"/>
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
}};

const enable_query = () => {{
    allow_query = true
    button.disabled = false;
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
            this.dispatchEvent(event)
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

TABLE_HEADER = '''
<style type="text/css">
    body {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 1rem;
    }

    table {
        border-collapse: collapse;
        border: solid 0.2rem;
    }

    thead {
        background-color: #efefef
    }

    th {
        padding: 0.1rem 0.2rem;
        border: solid 0.1rem;
        font-size: 1rem;
    }

    thead tr:nth-child(1) {
        background-color: white;
    }

    thead tr:nth-child(1) th {
        border: hidden;
        border-bottom: solid 0.1rem;
    }

    thead tr th:nth-last-child(1) {
        white-space: nowrap;
    }
</style>'''


DIST_TABLE_HEADER = '''
<style type="text/css">
    body {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 1rem;
    }

    table {
        border-collapse: collapse;
        border: solid 0.2rem;
        background-color: honeydew;
    }

    td, th {
        padding: 0.1rem 0.2rem;
        border-top: solid 0.1rem;
        font-size: 1rem;
    }

    tr th:nth-child(1) {
        border-right: solid 0.1rem;
    }
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
<div style="overflow-y:auto;overflow-x: hidden;">{{}}</div>
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
            ['Dist', 'Community', 'Date']).sort_index(ascending=[True, True, False])
    else:
        df = data.set_index(['Dist', 'Community', 'Date']).sort_index(ascending=[True, True, False])
    df.index.names = ['区', '地址', '感染报告日期']
    return df


def init_all_data():
    with open(DATA_FILE, 'rb') as f:
        all_data = pickle.load(f)
    update_date = all_data.Date.max().strftime('%Y-%m-%d')
    return all_data, update_date


def get_result_data(place, all_data):
    place = place.strip()
    if place[-1] == '弄' or place[-1] == '号':
        place = place[:-1]
    data = vague_search_print(place, all_data)
    return data


def get_result_html(place, all_data):
    data = get_result_data(place, all_data)
    if data.shape[0] == 0:
        content = '<span>(无感染记录或未收录地址。注意，输入地址请勿包含行政区。)</span>'
    else:
        content = data.to_html()
    return content


def init_dist_data(all_data):
    dist_summary = all_data[
        all_data.Date.isin(sorted(all_data.Date.unique())[-5:])
    ].groupby(['Dist', 'Date']).size().rename('Counts').sort_index(
    ).reset_index().set_index(['Dist', 'Date']).unstack()
    dist_summary.columns = [d[1].strftime('%Y-%m-%d') for d in dist_summary.columns]
    dist_summary.index.name = None
    dist_summary = dist_summary.style.background_gradient(axis=None, cmap='YlOrRd')

    return MAIN_PAGE_TEMPLATE.format(
        header=DIST_TABLE_HEADER,
        content='''
        <a href="/"><img src="/img/logo.jpg" alt="logo" style="height: 4rem;"></a>
        <h1 style="margin: 0">各行政区感染小区总数</h1>
        <div style="font-size: 0.75em; font-style: italic">
            <div>*使用前请仔细阅读<a href="/inst.html">本站使用说明</a></div>
        </div>
        <div style="overflow-y: auto;overflow-x: hidden;flex: 1 1 auto;height: 0;align-items: center;display: flex;flex-direction: column;margin-top: 1rem">\n{}</div>'''.format(
            dist_summary.to_html()))


ALL_DATA, UPDATE_DATE = init_all_data()
ROOT_PAGE = DEFAULT_PAGE.format(UPDATE_DATE)
DIST_SUMMARY_PAGE = init_dist_data(ALL_DATA)


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
    <div style="overflow-y: auto;overflow-x: hidden;">
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
    return SEARCH_PAGE.format(title=place, content=get_result_html(place, ALL_DATA))


EMPTY_PAGE = '<html><body style="text-align: center;font-size: 1rem"><h3>错误查询，请先输入地址。</h3></body></html>'
@app.route('/iframe_search/')
def iframe_wrong_search():
    return EMPTY_PAGE


@app.route('/iframe_search/<place>')
def ifram_search(place):
    return IFRAME_PAGE_TEMPLATE.format(get_result_html(place, ALL_DATA))


@app.route('/img/logo.jpg')
def logo_img():
    return LOGO_DATA;


@app.after_request
def add_header(response):
    response.cache_control.max_age = 900
    return response
