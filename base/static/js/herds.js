async function loadTraitNames() {
    let traitNames = await fetch("/traitnames");
    if (!traitNames.ok) {
        alert("Error loading herd data. Please try again.")
        return false;
    }

    setSessionDict("TraitNames", await traitNames.json());
    return true;
}

async function loadHerds() {
    let herds = await fetch("/herdsummaries");
    if (!herds.ok) {
        alert("Error loading herd data. Please try again.")
        return false;
    }

    setSessionDict("Summaries", await herds.json());
    return true;
}

function displayHerds() {
    let summaries = getSessionDict("Summaries");

    displayHerdsBy("id", false, "public", summaries);
    displayHerdsBy("id", false, "private", summaries);
}

function displayHerdsBy(orderby, reverse, protection, summaries) {
    let herds = document.getElementById("herd-btns-" + protection);
    herds.replaceChildren();
    let keylist = [];

    for (let key in summaries[protection]) {
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
    for (let key in keylist) {
        if (keylist.hasOwnProperty(key)) {
            let protectedKey = keylist[key];
            let herdName = summaries[protection][protectedKey]["name"];
            let className = summaries[protection][protectedKey]["class"];

            let btn = document.createElement("button");
            btn.textContent = `[${className}] ${herdName}`;

            btn.herdid = protectedKey;

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

function displayTraits() {
    let traitnames = getSessionDict("TraitNames");

    let herdAverages = document.getElementById("herd-averages");

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
            addFromKey(key)
        }
    }
}

function changeDisplayedHerd(publicprivate, herdid) {
    document.getElementById("right-panel").classList.add("herd-selected");

    let summaries = getSessionDict("Summaries");
    let herdsum = summaries[publicprivate][herdid]["traits"];

    document.getElementById("open-herd-link").href = "/openherd-" + herdid;
    document.getElementById("herd-name").textContent = summaries[publicprivate][herdid]["name"];

    document.getElementById("ID" + "-ipt").value = herdid;
    for (let key in herdsum) {
        if (herdsum.hasOwnProperty(key)) {
            document.getElementById(key + "-ipt").value = herdsum[key];
        }
    }
}

async function setUp() {
    await loadTraitNames();
    await loadHerds();
    displayTraits();
    displayHerds();
}