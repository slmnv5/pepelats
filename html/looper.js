"use strict";


let WIN_CHARS = 30; // how many chars fit in browser window line
// const TEXT_SZ = 35; // size for all elements
const BW_S = '<span style="color: black; background-color: rgb(200, 200, 200)";>'; // 1-st loop position
const END_S = '</span>'

const RED_P = '<p style="color: rgb(250, 30, 30);">';
const GREEN_P = '<p style="color: rgb(30, 250, 30);">';
const YELLOW_P = '<p style="color: yellow;">';

// make html showing progress line - position in 1-st loop and position in max. length loop
function getHeaderHtml(s, first_pos, long_pos) {
    function decorateOneChar(s, pos) {
        return s.slice(0, pos) + "▒" + s.slice(pos + 1);
    }
    const l = s.length;
    s = decorateOneChar(s, l * long_pos);
    return '<p>' + BW_S + s.slice(0, l * first_pos) + END_S + s.slice(l * first_pos) + '</p>';
};

// decorate string with color based on 1st char. 
// Shows part that plays in green, next part in yellow,
// recorded part in red
function getContentHtml(content, is_rec) {
    let line, result = "";
    for (line of content.split("\n")) {
        if (line[0] === '*') {
            result += (is_rec > 0 ? RED_P : GREEN_P) + line + '</p>';
        } else if (line[0] === '>') {
            result += YELLOW_P + line + '</p>';
        } else {
            result += '<p>' + line + '</p>';
        }
    };
    return result;
};


document.addEventListener('DOMContentLoaded', () => {
    const HEADER = document.getElementById('header');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    const FETCH_SECONDS = 1;
    let HEADER_TEXT = "press button to start looper";
    let ERR_COUNT = 0;
    let SCR_INFO = {
        "first_pos": 0, "long_pos": 0, "first_delta": 0.2, "long_delta": 0.1, "is_rec": 0, "sleep_tm": 1
    }

    function drawPage() {
        SCR_INFO.first_pos += SCR_INFO.first_delta // position in the 1-st loop
        SCR_INFO.first_pos %= 1;
        SCR_INFO.long_pos += SCR_INFO.long_delta // position in the max. length loop
        SCR_INFO.long_pos %= 1;
        HEADER.innerHTML = getHeaderHtml(HEADER_TEXT, SCR_INFO.first_pos, SCR_INFO.long_pos);
        setTimeout(drawPage, SCR_INFO.sleep_tm * 1000);
    }

    async function fetchJsonData() {
        try {
            const response = await fetch("/update");
            if (!response.ok) {
                throw new Error("HTTP error, status: " + response.status);
            }
            if (response.status == 200) {
                SCR_INFO = await response.json();
                DESCRIPTION.textContent = SCR_INFO.description;
                CONTENT.innerHTML = getContentHtml(SCR_INFO.content, SCR_INFO.is_rec);
                const dot_len = Math.max(WIN_CHARS - SCR_INFO.header.length, 0) / 2;
                const dot_str = '.'.repeat(dot_len);
                HEADER_TEXT = dot_str + SCR_INFO.header + dot_str;
            }
        } catch (error) {
            console.error('Error fetching data:', error, ++ERR_COUNT);
            if (ERR_COUNT > 100) {
                return;
            }
        }
        fetchJsonData();
    }

    drawPage();
    fetchJsonData();
});



