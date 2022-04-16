function getElementByXpath(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

function add_color_sec(color, curr_bg, curr_p) {
    curr_bg += "white " + curr_p + "%, ";
    curr_bg += color + " " + curr_p + "%, ";
    curr_p += 6;
    curr_bg += color + " " + curr_p + "%, ";
    curr_bg += "white " + curr_p + "%, ";
    curr_p += 1;
    return [curr_bg, curr_p];
}

function color_sec_community(th, d, color) {
    curr_p = (14 - d) * 7;
    curr_bg = "linear-gradient(90deg, ";
    for(let rnd = 0; rnd < d; ++rnd) {
        [curr_bg, curr_p] = add_color_sec(color, curr_bg, curr_p);
    }
    curr_bg += "white " + curr_p + "%)"
    th.style.background = curr_bg
}

function insert_community_status(th, name, color) {
    let div_node = document.createElement("div")
    div_node.textContent = "当前："
    div_node.className = "curr_status"
    let span_node = document.createElement("span")
    span_node.textContent = name
    span_node.style.color = color
    div_node.appendChild(span_node)
    th.appendChild(div_node)
}


function processing_row(tr) {
    let ind = 0;
    let level_index = -1;
    for (; ind < tr.childElementCount; ++ind)
    {
        level_index = tr.children[ind].id.indexOf("_level1_")
        if (level_index != -1) {
            break;
        }
    }

    if (level_index == -1) {
        return;
    }

    remain = parseInt(tr.children[ind+1].textContent)
    let fg_color = "black";
    let bg_color = "white";
    let name = "";
    if (remain == 0)
    {
        fg_color = "#4adc4a";
        bg_color = "#c0ffc0";
        tr.children[ind].style.background = bg_color
        name = "防范区"
    }
    else {
        if (remain <= 7)
        {
            fg_color = "#eeab65";
            bg_color = "#ffdfbd";
            name = "管控区"
        }
        else
        {
            fg_color = "#ff8d8d";
            bg_color = "#ffdddd";
            name = "封控区"
        }
        color_sec_community(tr.children[ind], remain, bg_color)
    }
    insert_community_status(tr.children[ind+1], name, fg_color)
}

tbody = getElementByXpath(document.currentScript.getAttribute("table-body-path"))

for(let ind = 0; ind < tbody.childElementCount; ++ind)
{
    processing_row(tbody.children[ind])
}

