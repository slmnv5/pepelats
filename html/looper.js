"use strict";

let WIN_CHARS = 30; // how many chars fit in browser window line
// const TEXT_SZ = 35; // size for all elements
const BW_S = '<span style="color: black; background-color: rgb(200, 200, 200)";>'; // 1-st loop position
const WY_S = '<span style="background-color: yellow";>';  // max. length loop position
const END_S = '</span>'
const RED_P = '<p style="color: rgb(250, 30, 30);">';
const GREEN_P = '<p style="color: rgb(30, 250, 30);">';
const YELLOW_P = '<p style="color: yellow;">';


function sleepFunc(ms) {
    if (!Number.isFinite(ms) || ms < 0) ms = 1_000;
    return new Promise((r) => {setTimeout(r, ms)});
}


// make html showing progress line - position in 1-st loop and position in max. length loop
function getHeaderHtml (s, base_pos, long_pos) {
    let missing_len = Math.max(WIN_CHARS - s.length, 0);
    s = '.'.repeat(missing_len / 2) + s + '.'.repeat(missing_len / 2);

    function decorateOneChar(s, pos) {
        if (pos < 0 || pos >= s.length) return s;
        return s.slice(0, pos) + WY_S + s.slice(pos, pos+1) + END_S + s.slice(pos+1);
    }
    let s1, s2, l1, l2;
    [l1, l2] = [s.length * base_pos, s.length * long_pos];
    [s1, s2] = [s.slice(0, l1), s.slice(l1)];
    [s1, s2] = [decorateOneChar(s1, l2), decorateOneChar(s2, l2 - l1)];
    return '<p>' + BW_S + s1 + END_S + s2 + '</p>';
};

// decorate string with color based on 1st char. 
// Shows part that plays in green, next part in yellow,
// recorded part in red
function getContentHtml(content, is_rec) {
    let s = "", result = "";
    for (s of content.split("\n")) {
        if (s[0] === '*') {
            result += (is_rec > 0 ? RED_P : GREEN_P) + s + '</p>';
        } else if (s[0] === '~') {
            result += YELLOW_P + s + '</p>';
        } else {
            result += '<p>' + s + '</p>';
        }
    }
    return result;
};


function recalcWidth() {
    //WIN_CHARS = Math.floor(window.innerWidth / (TEXT_SZ * 0.63));
};

window.onresize = recalcWidth;



window.onload = () => {
    const URL = '/update';
    let DATA = {"sleep_tm":1, "header":"-", "description": "-", "content":"-", "is_rec":0,
            "base_pos":0, "long_pos":0, "base_delta":0.0625, "long_delta":0.0625};
    let RUN = true;
    const HEADER = document.getElementById('header');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    recalcWidth();

    
    Promise.race([fetchData(), redrawData()])
    .then((x) => console.log("Resolved:", x))  
    .catch((x) => console.log("Rejected:", x))


    async function fetchData() {
        while(RUN) {
            try {
                let resp = await fetch(URL);
                if (resp.status == 200) {
                    DATA = await resp.json();
                    DESCRIPTION.textContent = DATA.description;
                    CONTENT.innerHTML = getContentHtml(DATA.content, DATA.is_rec);
                }
            } catch(err) {
                console.error(err);
                RUN = false;
                return;
            }
        };
    };

    async function redrawData() {
        while(RUN) {
            try {
                await sleepFunc(DATA.sleep_tm * 1000);
                DATA.base_pos += DATA.base_delta // position in the 1-st loop
                DATA.base_pos %= 1;
                DATA.long_pos += DATA.long_delta // position in the max. length loop
                DATA.long_pos %= 1;
                HEADER.innerHTML = getHeaderHtml(DATA.header, DATA.base_pos, DATA.long_pos);
            } catch(err) {
                console.error(err);
                RUN = false;
                return;
            }
        };
    };
};


