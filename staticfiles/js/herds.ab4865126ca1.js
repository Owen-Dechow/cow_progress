var Sumaries;

async function loadHerds() {
    let herds = await fetch(new URL("summaries/", window.location));
    if (!herds.ok) {
        alertreal("Error Loading Data", "Error loading herd data. Please try again.", "ok");
        return false;
    }

    Sumaries = Object.freeze(await herds.json());
    return true;
}

function displayHerds() {
    displayHerdsBy("id", false, "public", Sumaries);
    displayHerdsBy("id", false, "private", Sumaries);
}

function displayHerdsBy(orderby, reverse, protection, summaries) {
    let herds = document.getElementById("herd-btns-" + protection);
    herds.replaceChildren();
    let keylist = [];

    for (let key in summaries[protection]) {
        if (summaries[protection].hasOwnProperty(key)) {
            keylist.push(key);
        }
    }

    if (orderby == "id") {
        keylist.sort();
    } else {
        keylist.sort((a, b) => summaries[protection][b]["traits"][orderby] - summaries[protection][a]["traits"][orderby]);
    }

    if (reverse) keylist.reverse();
    for (let key in keylist) {
        if (keylist.hasOwnProperty(key)) {
            let protectedKey = keylist[key];

            let btn = document.createElement("button");

            btn.textContent = summaries[protection][protectedKey]["name"];
            btn.herdid = protectedKey;
            btn.setAttribute('type', "button");

            btn.onclick = (e) => {
                changeDisplayedHerd(protection, e.target.herdid);
                btns = document.getElementsByClassName("focused-btn");
                for (let i = 0; i < btns.length; i++) {
                    btns[i].classList.remove("focused-btn");
                }
                e.target.classList.add("focused-btn");

            };

            herds.append(btn);
        }
    }
}

function displayTraits(herdsum) {
    let traitnames = herdsum;

    let herdAverages = document.getElementById("herd-averages");
    herdAverages.innerHTML = "";

    function addFromKey(key) {
        let lbl = document.createElement("label");
        lbl.id = key + "-lbl";
        lbl.textContent = key;

        let ipt = document.createElement("input");
        ipt.id = key + "-ipt";
        ipt.disabled = true;

        let p = document.createElement("p");
        p.appendChild(lbl);
        p.appendChild(ipt);

        herdAverages.appendChild(p);
    }

    addFromKey("ID");
    for (let key in traitnames) {
        if (traitnames.hasOwnProperty(key)) {
            addFromKey(key);
        }
    }
}

function changeDisplayedHerd(publicprivate, herdid) {
    document.getElementById("right-panel").classList.add("herd-selected");

    let herdsum = Sumaries[publicprivate][herdid]["traits"];

    displayTraits(herdsum);

    document.getElementById("open-herd-link").href = new URL(herdid, window.location);
    document.getElementById("herd-name").textContent = Sumaries[publicprivate][herdid]["name"];

    document.getElementById("ID" + "-ipt").value = herdid;
    for (let key in herdsum) {
        if (herdsum.hasOwnProperty(key)) {
            document.getElementById(key + "-ipt").value = herdsum[key];
        }
    }
}

async function setUp() {
    await loadHerds();
    displayHerds();
}