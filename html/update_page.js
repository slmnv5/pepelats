"use strict";

const TEXT_SZ = 35; // size for all elements 
let WIN_CHARS = 10; // how many chars fit in browser window line

function setStyle() {
    const body_style = document.body.style
    body_style['font-size'] = "35px"
    body_style['font-weight'] = "bolder"
    body_style['font-family'] = "monospace"
    
    body_style.margin = "0px"
    body_style.color = "rgb(200, 200, 200)"
    body_style.backgroundColor = "rgb(30, 30, 30)"
    body_style.textAlign = "center"
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
    return '<p>' + BW_S + s1 + END_S + WB_S + s2 + END_S + '</p>';
};

// decorate string with color based on 1st char
function getContentHtml(content, is_rec) {
    const RED_P = '<p style="color: rgb(250, 30, 30);">';
    const GREEN_P = '<p style="color: rgb(30, 250, 30);">';
    const YELLOW_P = '<p style="color: yellow;">';
    
    let s = '';
    for (const s of content.split("\n")) {
        if (s[0] === '*') {
            s += (is_rec ? RED_P : GREEN_P) + s + '</p>';
        } else if (s[0] === '~') {
            s += YELLOW_P + s + '</p>';
        } else {
            s += '<p>' + s + '</p>';
        }
    }
    return s;
};


function recalcWidth() {
    WIN_CHARS = Math.floor(window.innerWidth / (TEXT_SZ * 0.63));
};

window.onresize = recalcWidth;

window.onload = () => {

    setStyle()
    const URL = '/update';
    let DATA = {"update_tm":0, "sleep_tm":0.5,"pos":0,"delta":0.1,"max_loop_pos":0,"max_loop_delta":0.05};

    const HEADER = document.getElementById('header');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    recalcWidth();

    Promise.race([fetchData(), redrawData()])
    .then((values) => console.log("Resolved:\n", values))  
    .catch((values) => console.log("Rejected:\n", values))


    async function fetchData() { 
        while(true) {
            let res = await fetch(URL);
            let tmp = await res.json();
            if (tmp.update_tm > DATA.update_tm) {
                DATA = tmp;
                DESCRIPTION.textContent = DATA.description;
                CONTENT.innerHTML = getContentHtml(DATA.content, DATA.is_rec);
            };
            await new Promise(r => setTimeout(r, 1000));    
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


