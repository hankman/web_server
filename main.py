
from flask import Flask
import pickle


DATA_FILE = '/home/cfan/notebooks/infect.pickle'
PAGE_TEMPLATE = '<html><body>{} <div style="left: 0; right: 0; bottom: 30px; position: absolute; text-align: center"><a href="https://beian.miit.gov.cn/" target="_blank">沪ICP备2022007631号-1|©2022 chenfan.info 版权所有</a></div></body></html>'
app = Flask(__name__)


def trans_data(all_data):
    community_data = {}
    for d, inf in all_data.items():
        for dist, coms in inf.items():
            for com in coms:
                if com in community_data:
                    community_data[com][1].append(d)
                else:
                    community_data[com] = (dist, [d])
    return community_data


def vague_search_print(dist, community_data):
    ret = []
    for key in community_data:
        if dist in key:
            ret.append((key, *community_data[key]))
    return ret


@app.route('/')
def root():
    return PAGE_TEMPLATE.format('use "chenfan.info/<地址>" to find infected history')


@app.route('/<place>')
def query_place(place):
    place = place.strip()
    if place == 'debug':
        with open('/home/cfan/notebooks/grab_infect_data.html', 'rb') as f:
            return f.read()

    with open(DATA_FILE, 'rb') as f:
        all_data = pickle.load(f)
    community_data = trans_data(all_data)
    data = vague_search_print(place, community_data)
    content = ''
    for community, dist, dates in data:
        content += f'<span>{community}({dist}): </span><span>{[d.strftime("%Y-%m-%d") for d in sorted(dates)]}</span><br/>'
    if not len(data):
        content = '<span>(无感染记录)</span>'
    ret = PAGE_TEMPLATE.format(content)
    return ret
