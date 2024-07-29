"use strict";

const TEXT_SZ = 35; // size for all elements 
let WIN_CHARS = 10; // how many chars fit in browser window line

function sleepFunc(ms) {
    if (!Number.isFinite(ms) || ms < 0) ms = 1_000;
    return new Promise((r) => {setTimeout(r, ms)});
}


function setStyle() {
    const body_style = document.body.style;
    body_style['font-size'] = "35px";
    body_style['font-weight'] = "bolder";
    body_style['font-family'] = "monospace";
    
    body_style.margin = "0px";
    body_style.color = "rgb(200, 200, 200)";
    body_style.backgroundColor = "rgb(30, 30, 30)";
    body_style.textAlign = "center";
}

// make html showing progress line, char. X - position of max. length loop
function getHeaderHtml (header, l1, l2, max_chars) {
    const BW_S = '<span style="color: black; background-color: rgb(200, 200, 200)";>';
    const WY_S = '<span style="background-color: yellow";>';
    const END_S = '</span>'

    function decorateOneChar(s, pos) {
        if (pos < 0 || pos >= s.length) return s;
        return s.slice(0, pos) + WY_S + s.slice(pos, pos+1) + END_S + s.slice(pos+1);
    }
    
    [l1, l2] = [l1 * max_chars, l2 * max_chars];
    let missing = max_chars - header.length;
    let s = '.'.repeat(missing / 2) + header + '.'.repeat(missing / 2);
    let s1, s2;
    [s1, s2] = [s.slice(0, l1), s.slice(l1)];
    [s1, s2] = [decorateOneChar(s1, l2), decorateOneChar(s2, l2 - l1)];
    return '<p>' + BW_S + s1 + END_S + s2 + '</p>';
};

// decorate string with color based on 1st char
function getContentHtml(content, is_rec) {
    const RED_P = '<p style="color: rgb(250, 30, 30);">';
    const GREEN_P = '<p style="color: rgb(30, 250, 30);">';
    const YELLOW_P = '<p style="color: yellow;">';
    
    let s = "", result = "";
    for (s of content.split("\n")) {
        if (s[0] === '*') {
            result += (is_rec ? RED_P : GREEN_P) + s + '</p>';
        } else if (s[0] === '~') {
            result += YELLOW_P + s + '</p>';
        } else {
            result += '<p>' + s + '</p>';
        }
    }
    return result;
};


function recalcWidth() {
    WIN_CHARS = Math.floor(window.innerWidth / (TEXT_SZ * 0.63));
};

window.onresize = recalcWidth;


async function fetchTest(url) {
    await sleepFunc(10_000);
    let data = {"sleep_tm":0.5, "header":"---", "description": "---", "content":"---",
        "pos":0, "delta":0.1, "max_loop_pos":0, "max_loop_delta":0.05};
    let blob = new Blob([JSON.stringify(data, null, 2)], {type : 'application/json'});
    let init = { "status" : 200 , "statusText" : "OK" };
    let resp = new Response(blob, init);
    return resp;
}

window.onload = () => {

    setStyle()
    const URL = '/update';
    let DATA = {};

    const HEADER = document.getElementById('header');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    recalcWidth();

    Promise.race([fetchData(), redrawData()])
    .then((x) => console.log("Resolved:", x))  
    .catch((x) => console.log("Rejected:", x))


    async function fetchData() {
        function processData(x) {
            if (x.update_tm <= DATA.update_tm) return;
            DATA = x;
            DESCRIPTION.textContent = DATA.description;
            CONTENT.innerHTML = getContentHtml(DATA.content, DATA.is_rec);
        }
     
        while(true) {
            try {
                let resp = await fetch(URL);
                let data = await resp.json();
                processData(data);
            } catch(err) {
                console.error(err)
            }
        };
    };

    async function redrawData() {
        while(true) {
            try {
                await sleepFunc(DATA.sleep_tm * 1000);
                DATA.pos += DATA.delta // position in the song part
                DATA.pos %= 1;
                if (DATA.max_loop_delta > 0) {
                    DATA.max_loop_pos += DATA.max_loop_delta // position in the max loop
                    DATA.max_loop_pos %= 1;
                };
                HEADER.innerHTML = getHeaderHtml(DATA.header, DATA.pos, DATA.max_loop_pos, WIN_CHARS);                        
            } catch(err) {
                console.error(err);
            }            
        };
    };
};


