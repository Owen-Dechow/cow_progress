let TRAITNAMES;
let COWS;
var DATALOADED;
var LOADEDGENDER;
var CanChangeID = true;


async function loadCows() {
    herdid = window.location.pathname.split("/").pop();
    var cows = await fetch("/herd-data/" + herdid);

    if (!cows.ok) {
        alert("Error loading herd data. Please try again.")
        return false;
    }

    COWS = await cows.json();
    DATALOADED = true;
    return true;
}

async function loadTraitNames() {
    var traitNames = await fetch("/traitnames");
    if (!traitNames.ok) {
        alert("Error loading herd data. Please try again.")
        return false;
    }
    TRAITNAMES = traitNames.json();
    return true;
}

async function displayCows() {
    var cows = await COWS;

    displayCowsBy("id", false, "bulls", cows);
    displayCowsBy("id", false, "cows", cows);
}

function displayCowsBy(orderby, reverse, gender, cowslist) {
    var cows = document.getElementById("herd-btns-" + gender);
    cows.replaceChildren();
    var keylist = [];

    for (var key in cowslist[gender]) {
        if (cowslist[gender].hasOwnProperty(key)) {
            keylist.push(key)
        }
    }

    if (orderby == "id") keylist.sort().reverse();
    else if (orderby == "Generation") keylist.sort((a, b) => cowslist[gender][b]["Generation"] - cowslist[gender][a]["Generation"])
    else if (orderby == "Sire") keylist.sort((a, b) => cowslist[gender][b]["Sire"] - cowslist[gender][a]["Sire"])
    else if (orderby == "Dam") keylist.sort((a, b) => cowslist[gender][b]["Dam"] - cowslist[gender][a]["Dam"])
    else keylist.sort((a, b) => cowslist[gender][b]["traits"][orderby] - cowslist[gender][a]["traits"][orderby])

    if (reverse) keylist.reverse();

    for (var key in keylist) {
        if (keylist.hasOwnProperty(key)) {
            key = keylist[key];
            btn = document.createElement("button");
            btn.textContent = cowslist[gender][key]["name"];
            btn.herdid = key;

            btn.onclick = (e) => {
                changeDisplayedCow(gender, e.target.herdid);
                btns = document.getElementsByClassName("focused-btn");
                for (var i = 0; i < btns.length; i++) {
                    btns[i].classList.remove("focused-btn");
                }
                e.target.classList.add("focused-btn");
            };

            cows.append(btn);
        }
    }
}

async function displayTraits() {
    var traitnames = await TRAITNAMES;

    var herdAverages = document.getElementById("cow-stats");
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

        opt = document.createElement("option");
        opt.value = key;
        opt.textContent = key;
        orderby.appendChild(opt);
    }

    addFromKey("id")
    addFromKey("Generation")
    addFromKey("Sire")
    addFromKey("Dam")
    for (var key in traitnames) {
        if (traitnames.hasOwnProperty(key)) {
            addFromKey(key)
        }
    }
}

async function changeDisplayedCow(gender, cowid) {
    if (gender != undefined && cowid != undefined) {
        document.getElementById("right-panel").classList.add("cow-selected");

        var cowname = document.getElementById("cow-name");
        if (cowname.classList.contains("owner")) {
            cowname.disabled = false;
        }

        LOADEDGENDER = gender;

        var stats = await COWS[gender][cowid];
        document.getElementById("cow-name").value = stats["name"]

        document.getElementById("id" + "-ipt").value = cowid;
        document.getElementById("Generation" + "-ipt").value = stats["Generation"];
        document.getElementById("Sire" + "-ipt").value = stats["Sire"];
        document.getElementById("Dam" + "-ipt").value = stats["Dam"];

        for (var key in stats["traits"]) {
            if (stats["traits"].hasOwnProperty(key)) {
                document.getElementById(key + "-ipt").value = stats["traits"][key];
            }
        }
    } else {
        LOADEDGENDER = gender;
        document.getElementById("cow-name").value = "~"
        document.getElementById("right-panel").classList.remove("cow-selected");
        document.getElementById("id" + "-ipt").value = "cowid";
        document.getElementById("Generation" + "-ipt").value = "";
        document.getElementById("Sire" + "-ipt").value = "";
        document.getElementById("Dam" + "-ipt").value = "";
        var stats = await TRAITNAMES;
        for (var key in stats) {
            if (stats.hasOwnProperty(key)) {
                document.getElementById(key + "-ipt").value = "";
            }
        }
    }
}

async function setUp() {
    await loadCows();
    await loadTraitNames();
    await displayTraits();
    await displayCows();
}

async function setSortOrder() {
    var reverse = document.getElementById("sort-pos-neg");
    var orderby = document.getElementById("order-by");
    var cows = await COWS;

    displayCowsBy(orderby.value, reverse.value == "neg", "bulls", cows);
    displayCowsBy(orderby.value, reverse.value == "neg", "cows", cows);
}

async function filterHasName(val) {
    filterHasNameBy(val, "cows");
    filterHasNameBy(val, "bulls");
}

async function filterHasNameBy(val, gender) {
    await setSortOrder();

    var container = document.getElementById("herd-btns-" + gender);
    var elements = [];
    for (var i = 0; i < container.children.length; i++) {
        elements.push(container.childNodes[i]);
        container.removeChild(elements[elements.length - 1]);
        i--;
    }

    var elements2 = [];
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].textContent.toUpperCase().indexOf(val.toUpperCase()) > -1) {
            elements2.push(elements[i]);
        }

        elements2.forEach(element => {
            container.appendChild(element);
        });
    }
}

async function setCowName(event) {
    if (LOADEDGENDER == undefined) return;
    event.target.disabled = true;

    gender = LOADEDGENDER == "bulls" ? "bull" : "cow";

    id = document.getElementById("id-ipt").value;
    newname = document.getElementById("cow-name").value;
    if (!/^[A-Za-z0-9-_ .]+$/.test(newname)) {
        alertreal("Invalid name", `Letters, numbers  plus -_ . only.`, "ok");
        event.target.disabled = false;
        return;
    }

    gender = LOADEDGENDER;

    data = await fetch(`/set-cow-name/${id}/${gender}/${newname}`);
    jsondata = await data.json();

    if (jsondata["successful"]) {
        COWS[gender][id]["name"] = newname;
        alertreal("Name Changed", `Name was successfully changed to <br> ${newname}`, "ok");
    } else {
        alertreal("Name Change Failed", "Name change was unsuccessful.", "ok");
    }

    setSortOrder();

    event.target.disabled = false;
}

async function moveToClassHerd(event) {
    if (LOADEDGENDER == undefined) return;
    event.target.disabled = true;

    gender = LOADEDGENDER == "bulls" ? "bull" : "cow";
    if (confirm(`Are you sure you want to move this ${gender} to class herd?\nThis action cannot be undone.`)) {

        gender = LOADEDGENDER;
        id = document.getElementById("id-ipt").value;
        data = await fetch(`/move-cow/${id}/${gender}`);
        jsondata = await data.json();
        jsondata = {
            "successful": true
        }

        if (jsondata["successful"]) {
            alertreal("Move Successful", `${COWS[gender][id]["name"]} was successfully moved to class herd.`, "ok");
            delete COWS[gender][id];
        } else {
            alertreal("Move Failed", `${COWS[gender][id]["name"]} could not be moved to class herd.`, "ok");
        }

        setSortOrder();
        changeDisplayedCow(undefined, undefined);
    }
    event.target.disabled = false;
}

function addAnotherBull() {
    p = document.createElement("p");
    p.classList.add("bull");
    p.classList.add("single-bull")
    p.id = "bull-" + document.getElementsByClassName("bull").length;

    p2 = document.createElement("p");
    p.appendChild(p2);

    ipt = document.createElement("input");
    p2.appendChild(ipt);
    ipt.type = "number";
    ipt.min = 0;
    ipt.name = p.id;
    ipt.required = true
    ipt.oninput = (event) => {
        IDChange(event.target);
    }

    spn = document.createElement("span");
    p.appendChild(spn)
    spn.textContent = "Enter ID#"

    btn = document.createElement("button");
    p2.appendChild(btn);
    btn.type = "button";
    btn.textContent = "Remove Bull";
    btn.onclick = (event) => {
        removeBull(event.target);
    }

    document.getElementById("bulls").appendChild(p);
}

function removeBull(target) {
    var bullsList = document.getElementsByClassName("bull");
    if (bullsList.length <= 1) return;
    target.parentNode.remove();

    var bullsList = document.getElementsByClassName("bull");
    for (var i = 0; i < bullsList.length; i++) {
        element = bullsList[i];
        element.id = "bull-" + i;
        element.getElementsByTagName("input")[0].name = "bull-" + i;
    }
}

function IDChange(target) {
    if (target.value > Number.MAX_SAFE_INTEGER) return;

    if (CanChangeID) {
        CanChangeID = false;
        FetchIDChange(target).finally(() => { CanChangeID = true; });
    }
}

async function FetchIDChange(target) {
    if (target.value != Math.round(target.value) || target.value == "") {
        target.parentNode.parentNode.getElementsByTagName("span")[0].value = "INVALID ID#";
        return;
    };

    var data = await fetch(`/get-cow-name/${target.value}`);
    var jsonData = await data.json();

    if (jsonData["name"] == null) {
        target.parentNode.parentNode.getElementsByTagName("span")[0].textContent = "INVALID ID#";

    } else {
        target.parentNode.parentNode.getElementsByTagName("span")[0].textContent = jsonData["name"];
    }
}

setUp();
