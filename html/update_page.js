"use strict";

// calculate 2 stringhs showing 2 progerss lines 
function getStr (l1, l2, max_chars) {
    [l1, l2] = [l1 * max_chars, l2 * max_chars]
    const chr1 = '\u2588';
    let s1 = '<span style="color: blue;">' + chr1.repeat(l1) + ' '.repeat(max_chars - l1) + "<br/></span>";
    let s2 = '<span style="color: cyan;">' + chr1.repeat(l2) + ' '.repeat(max_chars - l2) + "<br/></span>";
    return  (l2 > 0) ? s1 + s2 : s1 + s1
};

// decorate string with color based on 1st char
function getContentHtml(str, is_rec) {
    let tmp = ''
    for (const s of str.split("\n")) {
        if (s[0] === '*') {
            tmp += (is_rec ? '<p style="color: brown;">' : '<p style="color: green;">') + s + '</p>'
        } else if (s[0] === '~') {
            tmp += '<p style="color: yellow;">' + s + '</p>'
        } else {
            tmp += '<p>' + s + '</p>'
        }
    }
    return tmp
};


let WIN_CHARS = 10;
const recalcWidth = () => {
    WIN_CHARS = Math.floor(window.innerWidth / (25 * 0.63));
};

window.onresize = recalcWidth;

window.onload = () => {
    const URL = '/update';
    let DATA = {"sleep_tm":0.5, "header":"Not started yet","description":"content",
        "pos":0,"delta":0.1,"max_loop_pos":0,"max_loop_delta":0.05};

    const HEADER = document.getElementById('header');
    const PROGRESS = document.getElementById('progress');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    recalcWidth();

    console.log(">>>>", DATA)
    Promise.all([fetchData(), redrawData()])
    .then((values) => console.log("Resolved:\n", values))  
    .catch((values) => console.log("Rejected:\n", values))


    async function fetchData() {
        
        async function getUpdate() {
            try {
                let res = await fetch(URL);
                DATA = await res.json();
                HEADER.textContent = DATA.header
                DESCRIPTION.textContent = DATA.description
                CONTENT.innerHTML = getContentHtml(DATA.content, DATA.is_rec)    
            } catch {
                console.log("Failed to fetch and parse: " + URL + " sleep 3 seconds and retry");
                await new Promise(r => setTimeout(r, 3000));
            }                
        };

        while(true) {
            await getUpdate()
        }
    };

    async function redrawData() {        
        while(true) {
            DATA.pos = (DATA.pos + DATA.delta) % 1; // position in the song part
            if (DATA.max_loop_delta > 0) {
                DATA.max_loop_pos = (DATA.max_loop_pos + DATA.max_loop_delta) % 1 // position in the max loop
            };
            PROGRESS.innerHTML = getStr(DATA.pos, DATA.max_loop_pos, WIN_CHARS);
            await new Promise(r => setTimeout(r, DATA.sleep_tm * 1000));
        };
    };
};


