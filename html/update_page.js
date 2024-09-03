"use strict";

const TEXT_SZ = 35; // size for all elements 
let WIN_CHARS = 10; // how many chars fit in browser window line
const UPDATE_ID = "update_id" // used in header and in request 
let ERR_COUNT = 0
const MAX_ERR_COUNT = 100 // stop updates when too many errors

function sleepFunc(ms) {
    if (!Number.isFinite(ms) || ms < 0) ms = 1_000;
    return new Promise((r) => {setTimeout(r, ms)});
}


// make html showing progress line - position in 1-st loop and position in max. length loop
function getHeaderHtml (header, l1, l2, max_chars) {
    const BW_S = '<span style="color: black; background-color: rgb(200, 200, 200)";>'; // 1st loop position
    const WY_S = '<span style="background-color: yellow";>';  // max. length loop position
    const END_S = '</span>'

   
    function decorateOneChar(s, pos) {
        if (pos < 0 || pos >= s.length) return s;
        return s.slice(0, pos) + WY_S + s.slice(pos, pos+1) + END_S + s.slice(pos+1);
    }
    
    [l1, l2] = [l1 * max_chars, l2 * max_chars];
    let missing_len = Math.max(max_chars - header.length, 0);
    let missing_str = '.'.repeat(missing_len / 2);
    let s = missing_str + header + missing_str;
    let s1, s2;
    [s1, s2] = [s.slice(0, l1), s.slice(l1)];
    [s1, s2] = [decorateOneChar(s1, l2), decorateOneChar(s2, l2 - l1)];
    return '<p>' + BW_S + s1 + END_S + s2 + '</p>';
};

// decorate string with color based on 1st char. 
// Shows part that plays in green, next part in yellow,
// recorded part in red
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

async function fetchTest(_) {
    await sleepFunc(10_000);
    let data = {"sleep_tm":1, "header":"-", "description": "-", "content":"-","base_loop_pos":0, "base_loop_delta":0.1, "max_loop_pos":0, "max_loop_delta":0.05};
    let blob = new Blob([JSON.stringify(data, null, 2)], {type : 'application/json'});
    let init = { "status" : 200, "statusText" : "OK" };
    let resp = new Response(blob, init);
    resp.headers.append(UPDATE_ID, "123")
    return resp;
}

window.onload = () => {
    const URL = '/update';
    let DATA = {"sleep_tm":1, "header":"-", "description": "-", "content":"-", "base_loop_pos":0, "base_loop_delta":0.1, "max_loop_pos":0, "max_loop_delta":0.05};
    const HEADER = document.getElementById('header');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    recalcWidth();

    
    Promise.race([fetchData(), redrawData()])
    .then((x) => console.log("Resolved:", x))  
    .catch((x) => console.log("Rejected:", x))


    async function fetchData() {
        let id = 0 // update id on client side
        while(ERR_COUNT < MAX_ERR_COUNT) {
            try {
                let resp = await fetch(URL + "?" + UPDATE_ID + "=" + id);
                let newest_id = resp.headers.get(UPDATE_ID) // newest id from server 
                id = Number(newest_id) // next time ask for this id
                if (resp.status != 200) {
                    console.log("status: " + resp.status); // too long, no fetch, no error
                    continue;
                }
                DATA = await resp.json(); // got update
                DESCRIPTION.textContent = DATA.description;
                CONTENT.innerHTML = getContentHtml(DATA.content, DATA.is_rec);
            } catch(err) {
                ERR_COUNT++;
                console.error(err)
            }
        };
    };

    async function redrawData() {
        while(ERR_COUNT < MAX_ERR_COUNT) {
            try {
                await sleepFunc(DATA.sleep_tm * 1000);
                DATA.base_loop_pos += DATA.base_loop_delta // position in the song part
                DATA.base_loop_pos %= 1;
                if (DATA.max_loop_delta > 0) {
                    DATA.max_loop_pos += DATA.max_loop_delta // position in the max loop
                    DATA.max_loop_pos %= 1;
                };
                HEADER.innerHTML = getHeaderHtml(DATA.header, DATA.base_loop_pos, DATA.max_loop_pos, WIN_CHARS);                        
            } catch(err) {
                ERR_COUNT++
                console.error(err);
            }            
        };
    };
};


