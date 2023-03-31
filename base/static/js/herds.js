let TRAITNAMES;
let SUMMARIES;

async function loadTraitNames() {
    var traitNames = await fetch("/traitnames");
    if (!traitNames.ok) {
        alert("Error loading herd data. Please try again.")
        return false;
    }
    TRAITNAMES = traitNames.json();
    return true;
}

async function loadHerds() {
    var herds = await fetch("/herdsummaries");
    if (!herds.ok) {
        alert("Error loading herd data. Please try again.")
        return false;
    }

    SUMMARIES = herds.json();
    return true;
}

async function displayHerds() {
    var summaries = await SUMMARIES;

    displayHerdsBy("id", false, "public", summaries);
    displayHerdsBy("id", false, "private", summaries);
}

function displayHerdsBy(orderby, reverse, protection, summaries) {
    var herds = document.getElementById("herd-btns-" + protection);
    herds.replaceChildren();
    var keylist = [];

    for (var key in summaries[protection]) {
        if (summaries[protection].hasOwnProperty(key)) {
            keylist.push(key)
        }
    }

    if (orderby == "id") {
        keylist.sort();
    } else {
        keylist.sort((a, b) => summaries[protection][b]["traits"][orderby] - summaries[protection][a]["traits"][orderby])
    }

    if (reverse) keylist.reverse();
    for (var key in keylist) {
        if (keylist.hasOwnProperty(key)) {
            key = keylist[key];
            btn = document.createElement("button");
            btn.textContent = summaries[protection][key]["name"];
            btn.herdid = key;

            btn.onclick = (e) => {
                changeDisplayedHerd(protection, e.target.herdid);
                btns = document.getElementsByClassName("focused-btn");
                for (var i = 0; i < btns.length; i++) {
                    btns[i].classList.remove("focused-btn");
                }
                e.target.classList.add("focused-btn");

            };

            herds.append(btn);
        }
    }
}

async function displayTraits() {
    var traitnames = await TRAITNAMES;

    var herdAverages = document.getElementById("herd-averages");
    var orderby = document.getElementById("order-by");

    function addFromKey(key) {
        lbl = document.createElement("label");
        lbl.id = key + "-lbl";
        lbl.textContent = key;

        ipt = document.createElement("input");
        ipt.id = key + "-ipt";
        ipt.disabled = true;

        p = document.createElement("p");
        p.appendChild(lbl);
        p.appendChild(ipt);

        herdAverages.appendChild(p);
    }

    addFromKey("ID");
    for (var key in traitnames) {
        if (traitnames.hasOwnProperty(key)) {
            addFromKey(key)
        }
    }
}

async function changeDisplayedHerd(publicprivate, herdid) {
    document.getElementById("right-panel").classList.add("herd-selected");

    var summaries = await SUMMARIES;
    var herdsum = summaries[publicprivate][herdid]["traits"];

    document.getElementById("open-herd-link").href = "/open-herd/" + herdid;
    document.getElementById("herd-name").textContent = summaries[publicprivate][herdid]["name"];

    document.getElementById("ID" + "-ipt").value = herdid;
    for (var key in herdsum) {
        if (herdsum.hasOwnProperty(key)) {
            document.getElementById(key + "-ipt").value = herdsum[key];
        }
    }
}

async function setUp() {
    await loadTraitNames();
    await loadHerds();
    await displayTraits();
    await displayHerds();
}

setUp();