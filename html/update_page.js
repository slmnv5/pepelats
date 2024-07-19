   "use strict";

    const URL = '/update';
    let DATA = {"sleep_tm":0.5, "header":"Not started yet","description":"content",
    "pos":0,"delta":0,"max_loop_pos":-1,"max_loop_delta":0};
    
    let WIN_CHARS = 10;
    const recalcWidth = () => {
        WIN_CHARS = Math.floor(window.innerWidth / (25 * 0.63));
    };

    window.onresize = recalcWidth;

    window.onload = runApp


    function runApp() {
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
                    console.log("Failed to fetch and parse: " + URL + " sleep for: 3 seconds" );
                    await new Promise(r => setTimeout(r, 3000));
                }                
            };

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

            while(true) {
                await getUpdate()
            }
        };

        async function redrawData() {

            function getStr (l1, l2) {
                [l1, l2] = [l1 * WIN_CHARS, l2 * WIN_CHARS]
                const chr1 = '\u2588';
                let s1 = '<span style="color: blue;">' + chr1.repeat(l1) + ' '.repeat(WIN_CHARS - l1) + "<br/></span>";
                let s2 = '<span style="color: cyan;">' + chr1.repeat(l2) + ' '.repeat(WIN_CHARS - l2) + "<br/></span>";
                return  (l2 > 0) ? s1 + s2 : s1 + s1
            };

            function getProgressHtml(DATA) {
                let pos1 = 0; // position in the song part
                let pos2 = 0; // position in the max loop of the song part, if there is max loop

                pos1 = (pos1 + DATA.delta) % 1;
                if (DATA.max_loop_delta > 0) {
                    pos2 = (pos2 + DATA.max_loop_delta) % 1
                };
                return getStr(pos1, pos2);
            };
            
            while(true) {
                PROGRESS.innerHTML = getProgressHtml(DATA);
                console.log("Redraw done sleep for " + DATA.sleep_tm + " seconds")
                await new Promise(r => setTimeout(r, DATA.sleep_tm * 1000));
            };
        };
    };

    
    