"use strict";

const TEXT_SZ = 35; // size for all elements 
let WIN_CHARS = 10; // how many chars fit in browser window line
const RED_P = '<p style="color: rgb(250, 30, 30);">';
const GREEN_P = '<p style="color: rgb(30, 250, 30);">';
const YELLOW_P = '<p style="color: yellow;">';
const B_W_S = '<span style="color: black; background-color: rgb(200, 200, 200)";>';
const W_B_S = '<span style="color: rgb(200, 200, 200);">';

// make html showing progress line, char. X - position of max. length loop
function getHeaderHtml (header, l1, l2, max_chars) {
    [l1, l2] = [l1 * max_chars, l2 * max_chars];
    let missing = max_chars - header.length;
    let s = '.'.repeat(missing / 2) + header + '.'.repeat(missing / 2)
    if (l2 > 0) {
        s = s.substring(0, l2) + '\u2588' + s.substring(l2 + 1);
    };
    return '<p>' + B_W_S + s.slice(0, l1) + '</span>' + W_B_S + s.slice(l1) + '</span></p>';
};

// decorate string with color based on 1st char
function getContentHtml(content, is_rec) {
    let tmp = '';
    for (const s of content.split("\n")) {
        if (s[0] === '*') {
            tmp += (is_rec ? RED_P : GREEN_P) + s + '</p>';
        } else if (s[0] === '~') {
            tmp += YELLOW_P + s + '</p>';
        } else {
            tmp += '<p>' + s + '</p>';
        }
    }
    return tmp;
};


function recalcWidth() {
    WIN_CHARS = Math.floor(window.innerWidth / (TEXT_SZ * 0.63));
};

window.onresize = recalcWidth;

window.onload = () => {
    const URL = '/update';
    let DATA = {"sleep_tm":0.5, "header":"---","description":"content",
        "pos":0,"delta":0.1,"max_loop_pos":0,"max_loop_delta":0.05};

    const HEADER = document.getElementById('header');
    const PROGRESS = document.getElementById('progress');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    recalcWidth();

    Promise.race([fetchData(), redrawData()])
    .then((values) => console.log("Resolved:\n", values))  
    .catch((values) => console.log("Rejected:\n", values))


    async function fetchData() { 
        while(true) {
            try {
                let res = await fetch(URL);
                DATA = await res.json();
                if (DATA.header === "stop") break;
                DESCRIPTION.textContent = DATA.description
                CONTENT.innerHTML = getContentHtml(DATA.content, DATA.is_rec)
                console.log(">>>Fetched: " + URL);    
            } catch {
                await new Promise(r => setTimeout(r, DATA.sleep_tm * 3000));
            };                        
        };
    };

    async function redrawData() {        
        while(true) {
            DATA.pos = (DATA.pos + DATA.delta) % 1; // position in the song part
            if (DATA.max_loop_delta > 0) {
                DATA.max_loop_pos = (DATA.max_loop_pos + DATA.max_loop_delta) % 1 // position in the max loop
            };
            HEADER.innerHTML = getHeaderHtml(DATA.header, DATA.pos, DATA.max_loop_pos, WIN_CHARS);
            await new Promise(r => setTimeout(r, DATA.sleep_tm * 1000));
        };
    };
};


