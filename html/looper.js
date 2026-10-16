"use strict";

const SCR_COLS = 30; 
const BW_S = '<span style="color: black; background-color: rgb(200, 200, 200)";>'; 
const END_S = '</span>'

const RED_P = '<p style="color: rgb(250, 30, 30);">';
const GREEN_P = '<p style="color: rgb(30, 250, 30);">';
const YELLOW_P = '<p style="color: yellow;">';
const EVENT_SRC = new EventSource('/update');
let ERR_COUNT = 0;
let SCR_INFO = {
   "first_pos": 0, "longest_pos": 0, "first_delta": 0.2,
   "longest_delta": 0.1, "is_rec": 0, "sleep_tm": 1
}

function getHeaderHtml(s, first_pos, longest_pos) {
    function decorateOneChar(s, pos) {
        return s.slice(0, pos) + "▒" + s.slice(pos + 1);
    }
    const p1 = Math.floor(SCR_COLS * first_pos);
    const p2 = Math.floor(SCR_COLS * longest_pos)	
    s = decorateOneChar(s, p2);
    return '<p>' + BW_S + s.slice(0, p1) + END_S + s.slice(p1) + '</p>';
}

function getContentHtml(content, is_rec) {
    if (!content) return "";
    let line, result = "";
    for (line of content.split("\n")) {
        if (line[0] === '*') {
            result += (is_rec > 0 ? RED_P : GREEN_P) + line + '</p>';
        } else if (line[0] === '>') {
            result += YELLOW_P + line + '</p>';
        } else {
            result += '<p>' + line + '</p>';
        }
    }
    return result;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

document.addEventListener('DOMContentLoaded', () => {
    const HEADER = document.getElementById('header');
    const DESCRIPTION = document.getElementById('description');
    const CONTENT = document.getElementById('content');
    let HEADER_TEXT = "press button to start looper";
    
    function drawPage() {
        SCR_INFO.first_pos += SCR_INFO.first_delta;
        SCR_INFO.first_pos %= 1;
        SCR_INFO.longest_pos += SCR_INFO.longest_delta;
        SCR_INFO.longest_pos %= 1;
        HEADER.innerHTML = getHeaderHtml(HEADER_TEXT, SCR_INFO.first_pos, SCR_INFO.longest_pos);
	if (ERR_COUNT > 10) {	
            console.log("Stopped page updates");
	    return;
	}
	setTimeout(drawPage, SCR_INFO.sleep_tm * 1000);
    }
    

    EVENT_SRC.onmessage = function(event) {

    let freshData;
    try {
        freshData = JSON.parse(event.data);
    } catch (error) {
        console.error("Skipping malformed event stream data:", error);
        ERR_COUNT++;
	    return; 
    }

    SCR_INFO.is_rec        = freshData.is_rec;
    SCR_INFO.sleep_tm      = freshData.sleep_tm;
    SCR_INFO.first_delta   = freshData.first_delta;
    SCR_INFO.longest_delta = freshData.longest_delta;
    SCR_INFO.first_pos   = freshData.first_pos;
    SCR_INFO.longest_pos = freshData.longest_pos;

    DESCRIPTION.textContent = freshData.description;
    CONTENT.innerHTML       = getContentHtml(freshData.content, SCR_INFO.is_rec);
    const targetHeader = freshData.header.substring(0, SCR_COLS);
    const dot_len      = (SCR_COLS - targetHeader.length) / 2;
    const dot_str      = '.'.repeat(Math.floor(dot_len));
    HEADER_TEXT        = dot_str + targetHeader + dot_str;
};

EVENT_SRC.onerror = function(error) {
    console.error("EventSource failed: ", error, ERR_COUNT++);
    if (ERR_COUNT > 10) {
        EVENT_SRC.close();
        console.log("Disconnected from the event source.");
    }
};

    drawPage();
  
});
