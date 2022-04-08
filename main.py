
import os
import pickle
import pandas as pd
from flask import Flask


FAVICON_FILE = '/home/cfan/web_server/resources/favicon.ico'
AVATAR_FILE = '/home/cfan/web_server/resources/avatar.png'


DATA_DIR = '/home/cfan/notebooks/data'
DATA_FILE = os.path.join(DATA_DIR, 'infect.pickle')
DEBUG_FILE = os.path.join(DATA_DIR, 'grab_infect_data.html')

ICP_DIV = ''

SEARCH_PAGE_TEMPLATE = '<html style="overflow: hidden"><body><div style="overflow-y:auto; height: calc(100% - 20px)">{}</div><div style="left: 0; right: 0; text-align: center"><a href="https://beian.miit.gov.cn/" target="_blank">沪ICP备2022007631号-1|©2022 chenfan.info 版权所有</a></div></body></html>'


MAIN_PAGE_TEMPLATE = '<html style="overflow: hidden">{header}<body><div style="height: calc(100% - 50px); text-align: center;">{content}</div><div style="left: 0; right: 0; text-align: center"><div><a href="https://beian.miit.gov.cn/" target="_blank">沪ICP备2022007631号-1|©2022 chenfan.info 版权所有</a></div></div></body></html>'


DEFAULT_PAGE = MAIN_PAGE_TEMPLATE.format(
    header='',
    content='''<h1>查询感染记录</h1><div style="font-size: 10px; font-style: italic">
    <div>*本站非官方网站,仅用于交流和学习。本站数据均抓取自
    <b>上海发布公众号</b>和<a href="https://wsjkw.sh.gov.cn/xwfb/index.html">上海卫健委网站</a>。
    </div><div>*本站不保证数据的正确性或完整性。
    如有任何问题或异议请联系<a href="mailto:c-fan@outlook.com">开发者</a>。
    </div><div style="color: red">*“查询日期加14天就可解封”为谣言，具体解封政策请咨询当地防疫机构。</div>
    </div><br/>
<div>
<label type="text" for="address">输入查询地址：</label>
<input id="address" name="address" required autocomplete="address" autofocus type="text" placeholder="龙阳路"/>
<p>数据更新到：{}</p>
<button id='search'>查询</button>
<div>
<iframe id="result" src="about:blank" style="height: 100%; width: 100%; border: none"></iframe>
</div>
</div>

<script>

var allow_query = true

const button = document.getElementById("search");

const disable_query = () => {{
    allow_query = false
    button.disabled = true;
}};

const enable_query = () => {{
    allow_query = true
    button.disabled = false;
}};

function search_address()
{{
    if (!allow_query) return;
    var addr = document.getElementById("address").value
    document.getElementById("result").src = "/iframe_search/" + addr
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

</script>
''')


TEST_PAGE_TEMPLATE = MAIN_PAGE_TEMPLATE


IFRAME_PAGE_TEMPLATE = '''
<html>
<head>
    <style type="text/css">
    table {{
        border-collapse: collapse;
        border: solid 4px;
    }}

    thead {{
        background-color: #efefef
    }}

    th {{
        padding: 4px 8px;
        border: solid 2px
    }}

    thead tr:nth-child(1) {{
        background-color: white;
    }}

    thead tr:nth-child(1) th {{
        border: hidden;
        border-bottom: solid 2px;
    }}
</style>
</head>
<body style="display: flex;flex-direction: column;align-items: center;">
<div style="overflow-y:auto; height: calc(100% - 250px); overflow-x: hidden;">{}</div>
</body>
</html>'''


TEST_PAGE = TEST_PAGE_TEMPLATE.format(
    header='',
    content='''<h1>查询感染记录</h1>
<div>
<label type="text" for="address">输入查询地址：</label>
<input id="address" name="address" required autocomplete="address" autofocus type="text" placeholder="龙阳路"/>
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


UPDATE_DATE = ''
ALL_DATA = None


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
    dist_summary.index.name = '行政区'
    dist_summary = dist_summary.reset_index().set_index(
        [dist_summary.index.name] + dist_summary.columns.tolist())
    return MAIN_PAGE_TEMPLATE.format(
        header='''<head>
    <style type="text/css">
    table {{
        border-collapse: collapse;
        border: solid 4px;
    }}

    thead {{
        background-color: #efefef
    }}

    th {{
        padding: 4px 8px;
        border: solid 2px
    }}

    thead tr:nth-child(1) {{
        background-color: white;
    }}

    thead tr:nth-child(1) th {{
        border: hidden;
        border-bottom: solid 2px;
    }}
    </style>
    </head>'''.format(),
        content='<h1>各行政区感染小区总数</h1><div style="font-size: 10px; font-style: italic"><div>*该数据准确率较低，请以官方数据为准</div></div><div style="display: flex;flex-direction: column;align-items: center;">\n{}</div>'.format(
            dist_summary.to_html()))


ALL_DATA, UPDATE_DATE = init_all_data()
ROOT_PAGE = DEFAULT_PAGE.format(UPDATE_DATE)
DIST_SUMMARY_PAGE = init_dist_data(ALL_DATA)


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


def processing_avatar():
    return AVATAR_DATA


def processing_backend():
    with open(__file__, 'r') as f:
        return SEARCH_PAGE_TEMPLATE.format(''.join(['<pre>{}</pre>'.format(line.replace(
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
    return SEARCH_PAGE_TEMPLATE.format(get_result_html(place, ALL_DATA))


EMPTY_PAGE = '<html><body style="text-align: center"><h3>错误查询，请先输入地址。</h3></body></html>'
@app.route('/iframe_search/')
def iframe_wrong_search():
    return EMPTY_PAGE


@app.route('/iframe_search/<place>')
def ifram_search(place):
    return IFRAME_PAGE_TEMPLATE.format(get_result_html(place, ALL_DATA))


@app.after_request
def add_header(response):
    response.cache_control.max_age = 900
    return response
