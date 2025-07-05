"use strict";

let WIN_CHARS = 30; // how many chars fit in browser window line
// const TEXT_SZ = 35; // size for all elements
const BW_S = '<span style="color: black; background-color: rgb(200, 200, 200)";>'; // 1-st loop position
const END_S = '</span>'

const RED_P = '<p style="color: rgb(250, 30, 30);">';
const GREEN_P = '<p style="color: rgb(30, 250, 30);">';
const YELLOW_P = '<p style="color: yellow;">';


function getHeaderStr (s) {
    const missing_len = Math.max(WIN_CHARS - s.length, 0);
    return '.'.repeat(missing_len / 2) + s + '.'.repeat(missing_len / 2);
};

// make html showing progress line - position in 1-st loop and position in max. length loop
function getHeaderHtml (s, first_pos, long_pos) {
    function decorateOneChar(s, pos) {
        return s.slice(0, pos) + "▒" + s.slice(pos+1);
    }
    const l = s.length;
    s = decorateOneChar(s, l * long_pos);
    return '<p>' + BW_S + s.slice(0, l * first_pos) + END_S + s.slice(l * first_pos) + '</p>';
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
    };
    return result;
};

window.onload = () => {

    const HEADER = document.getElementById('header');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    const UPD_REQUEST = new XMLHttpRequest();

    let TIMEOUT = 0;

    function fetchData() {
        UPD_REQUEST.open("GET", '/update', true);
        UPD_REQUEST.send();
    };

    UPD_REQUEST.onloadend = () => {
        if (UPD_REQUEST.status == 204) {
            fetchData(); // no update, repeat again;
        } else if (UPD_REQUEST.status == 200) {
            const data = JSON.parse(UPD_REQUEST.responseText);
            DESCRIPTION.textContent = data.description;
            CONTENT.innerHTML = getContentHtml(data.content, data.is_rec);
            data.header = getHeaderStr(data.header);
            clearTimeout(TIMEOUT);
            redrawData(data);
            fetchData(data); // has updated, repeat again;
        } else {
            DESCRIPTION.textContent = "Incorrect server response: " + UPD_REQUEST.status;
            clearTimeout(TIMEOUT);
         };
    };

    function redrawData(data) {
        data.first_pos += data.base_delta // position in the 1-st loop
        data.first_pos %= 1;
        data.long_pos += data.long_delta // position in the max. length loop
        data.long_pos %= 1;
        HEADER.innerHTML = getHeaderHtml(data.header, data.first_pos, data.long_pos);
        TIMEOUT = setTimeout(()=>{redrawData(data)}, data.sleep_tm * 1000);
    };

    // only one call at the end
    fetchData();


};
