
import os
import pickle
import pandas as pd
from flask import Flask


FAVICON_FILE = '/home/cfan/web_server/resources/favicon.ico'

DATA_DIR = '/home/cfan/notebooks/data'
DATA_FILE = os.path.join(DATA_DIR, 'infect.pickle')
DEBUG_FILE = os.path.join(DATA_DIR, 'grab_infect_data.html')

ICP_DIV = ''

SEARCH_PAGE_TEMPLATE = '<html style="overflow: hidden"><body><div style="overflow-y:auto; height: calc(100% - 20px)">{}</div><div style="left: 0; right: 0; text-align: center"><a href="https://beian.miit.gov.cn/" target="_blank">沪ICP备2022007631号-1|©2022 chenfan.info 版权所有</a></div></body></html>'

MAIN_PAGE_TEMPLATE = '<html style="overflow: hidden"><body><div style="height: calc(100% - 20px)">{}</div><div style="left: 0; right: 0; text-align: center"><a href="https://beian.miit.gov.cn/" target="_blank">沪ICP备2022007631号-1|©2022 chenfan.info 版权所有</a></div></body></html>'

IFRAME_PAGE_TEMPLATE = '<html style="overflow: hidden"><body><div style="overflow-y:auto; height: calc(100% - 80px)">{}</div></body></html>'


DEFAULT_PAGE = MAIN_PAGE_TEMPLATE.format('''<h1>查询感染记录</h1>
<div>
<label type="text" for="address">输入查询地址：</label>
<input id="address" name="address" required autocomplete="address" autofocus type="text"/>
<button id="search" onclick="">查询</button>
<div>
<iframe id="result" src="about:blank" style="height: calc(100% - 50px); width: 100%; border: none"></iframe>
</div>
</div>

<script>
function search_address()
{
    var addr = document.getElementById("address").value
    document.getElementById("result").src = "/iframe_search/" + addr
}

document.getElementById("address").addEventListener(
    "keyup", function(event) {
    	if (event.keyCode === 13) {
            search_address();
            this.dispatchEvent(event)
        }
    })
document.getElementById("search").addEventListener(
	"click", search_address)
</script>''')


app = Flask(__name__)


def vague_search_print(comm, data):
    df = data[data.Community.str.contains(comm)].set_index(
        ['Dist', 'Community', 'Date']).sort_index(ascending=[True, True, False])
    df.index.names = ['区', '地址', '感染报告日期']
    return df


@app.route('/')
def root():
    return DEFAULT_PAGE


def processing_debug_request():
    with open(DEBUG_FILE, 'rb') as f:
        return f.read()


def processing_favicon():
    with open(FAVICON_FILE, 'rb') as f:
        return f.read()


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


@app.route('/favicon.ico')
def favicon():
    return processing_favicon()


@app.route('/backend')
def backend():
    return processing_backend()


def get_result_html(place):
    place = place.strip()
    with open(DATA_FILE, 'rb') as f:
        all_data = pickle.load(f)
    data = vague_search_print(place, all_data)
    if data.shape[0] == 0:
        content = '<span>(无感染记录)</span>'
    else:
        content = data.to_html()
    return content


@app.route('/search/<place>')
def query_place(place):
    return SEARCH_PAGE_TEMPLATE.format(get_result_html(place))


@app.route('/iframe_search/<place>')
def ifram_search(place):
    return IFRAME_PAGE_TEMPLATE.format(get_result_html(place))
