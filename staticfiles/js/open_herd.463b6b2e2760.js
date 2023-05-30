async function loadCows() {
    let herdID = sessionStorage.getItem("HerdId");
    let cows = await fetch("/herddata-" + herdID);

    if (!cows.ok) {
        alertreal("Error Loading Data", "Error loading herd data. Please try again.", "ok")
    }

    setSessionDict("Cows", await cows.json());
}

async function loadTraitNames() {
    let traitNames = await fetch("/traitnames");
    if (!traitNames.ok) {
        alertreal("Error Loading Data", "Error loading herd data. Please try again.", "ok")
    }

    setSessionDict("TraitNames", await traitNames.json());
}

async function loadHerdSummary() {
    let herdID = sessionStorage.getItem("HerdId");

    let summary = await fetch("/herdsummary-" + herdID);
    if (!summary.ok) {
        alertreal("Error Loading Data", "Error loading herd data. Please try again.", "ok")
    }

    setSessionDict("HerdSummary", await summary.json());
}

function displayCows() {
    let cows = getSessionDict("Cows");

    displayCowsBy("id", false, "bulls", cows);
    displayCowsBy("id", false, "cows", cows);
}

function displayCowsBy(orderby, reverse, gender, cowslist) {
    let cows = document.getElementById("herd-btns-" + gender);
    cows.replaceChildren();
    let keylist = [];

    for (let key in cowslist[gender]) {
        if (cowslist[gender].hasOwnProperty(key)) {
            keylist.push(key)
        }
    }

    if (orderby == "id") keylist.sort((a, b) => b - a)
    else if (orderby == "Generation") keylist.sort((a, b) => cowslist[gender][b]["Generation"] - cowslist[gender][a]["Generation"])
    else if (orderby == "Inbreeding Coefficient") keylist.sort((a, b) => cowslist[gender][b]["Inbreeding Coefficient"] - cowslist[gender][a]["Inbreeding Coefficient"])
    else if (orderby == "Sire") keylist.sort((a, b) => cowslist[gender][b]["Sire"] - cowslist[gender][a]["Sire"])
    else if (orderby == "Dam") keylist.sort((a, b) => cowslist[gender][b]["Dam"] - cowslist[gender][a]["Dam"])
    else keylist.sort((a, b) => cowslist[gender][b]["traits"][orderby] - cowslist[gender][a]["traits"][orderby])

    if (reverse) keylist.reverse();

    for (let key in keylist) {
        if (keylist.hasOwnProperty(key)) {
            let protectedKey = keylist[key];
            let btn = document.createElement("button");
            btn.textContent = cowslist[gender][protectedKey]["name"];
            btn.herdid = protectedKey;

            btn.onclick = (e) => {
                changeDisplayedCow(gender, e.target.herdid);
                btns = document.getElementsByClassName("focused-btn");
                for (let i = 0; i < btns.length; i++) {
                    btns[i].classList.remove("focused-btn");
                }
                e.target.classList.add("focused-btn");
            };

            cows.append(btn);
        }
    }
}

function displayTraits() {
    let traitnames = getSessionDict("TraitNames");

    let herdAverages = document.getElementById("cow-stats");
    let orderby = document.getElementById("order-by");

    function addFromKey(key) {
        let lbl = document.createElement("label");
        lbl.id = key + "-lbl";
        lbl.textContent = key;

        let ipt = document.createElement("input");
        ipt.id = key + "-ipt";
        ipt.disabled = true;
        ipt.classList.add("trait-ipt");

        let p = document.createElement("p");
        p.appendChild(lbl);
        p.appendChild(ipt);

        herdAverages.appendChild(p);

        let opt = document.createElement("option");
        opt.value = key;
        opt.textContent = key;
        orderby.appendChild(opt);
    }

    addFromKey("id")
    addFromKey("Generation")
    addFromKey("Sire")
    addFromKey("Dam")
    addFromKey("Inbreeding Coefficient")
    for (let key in traitnames) {
        if (traitnames.hasOwnProperty(key)) {
            addFromKey(key)
        }
    }
}

function changeDisplayedCow(gender, cowID) {
    let cows = getSessionDict("Cows");

    if (gender != undefined) {
        sessionStorage.setItem("LoadedGender", gender);
    } else {
        sessionStorage.setItem("LoadedGender", "none")
    }

    if (gender != undefined && cowID != undefined) {
        let cowname = document.getElementById("cow-name");
        if (cowname.classList.contains("owner")) {
            cowname.disabled = false;
        }


        let stats = cows[gender][cowID];
        document.getElementById("cow-name").value = stats["name"]

        document.getElementById("id" + "-ipt").value = cowID;
        document.getElementById("Generation" + "-ipt").value = stats["Generation"];
        document.getElementById("Inbreeding Coefficient" + "-ipt").value = stats["Inbreeding Coefficient"];
        document.getElementById("Sire" + "-ipt").value = stats["Sire"];
        document.getElementById("Dam" + "-ipt").value = stats["Dam"];

        for (let key in stats["traits"]) {
            if (stats["traits"].hasOwnProperty(key)) {
                document.getElementById(key + "-ipt").value = stats["traits"][key];
            }
        }

        recessives = document.getElementById("cow-recessives");
        recessives.innerHTML = "";
        for (let key in stats["recessives"]) {
            if (stats["recessives"].hasOwnProperty(key)) {
                let carriercode;
                let carriernumber = stats["recessives"][key];

                if (carriernumber == 0) carriercode = "--";
                else if (carriernumber == 1) carriercode = "-+";
                else if (carriernumber == 2) carriercode = "++";

                recessives.innerHTML += key + " " + carriercode + "<br>";
            }
        }

        document.getElementById("pedigree-link").href = `/pedigree?animal_id=${cowID}`;

    } else {
        pedigreeLink = document.getElementById("pedigree-link")
        if (pedigreeLink) pedigreeLink.href = "javascript:void(0)";

        document.getElementById("cow-name").value = "[HERD SUMMARY]";
        document.getElementById("id" + "-ipt").value = "~";
        document.getElementById("Generation" + "-ipt").value = "~";
        document.getElementById("Inbreeding Coefficient" + "-ipt").value = "~";
        document.getElementById("Sire" + "-ipt").value = "~";
        document.getElementById("Dam" + "-ipt").value = "~";

        document.getElementById("cow-recessives").innerHTML = "~";
        let stats = getSessionDict("HerdSummary");
        for (let key in stats) {
            if (stats.hasOwnProperty(key)) {
                document.getElementById(key + "-ipt").value = stats[key];
            }
        }
    }

    for (let input of document.getElementsByClassName("trait-ipt")) {
        if (input.value == "~") {
            input.parentNode.classList.add("hide");
            input.parentNode.classList.remove("show");
        } else {
            input.parentNode.classList.remove("hide");
            input.parentNode.classList.add("show");
        }
    }
}

function setSortOrder() {
    let reverse = document.getElementById("sort-pos-neg");
    let orderby = document.getElementById("order-by");
    let cows = getSessionDict("Cows");

    displayCowsBy(orderby.value, reverse.value == "neg", "bulls", cows);
    displayCowsBy(orderby.value, reverse.value == "neg", "cows", cows);
}

function filterHasName(val) {
    filterHasNameBy(val, "cows");
    filterHasNameBy(val, "bulls");
}

function filterHasNameBy(val, gender) {
    setSortOrder();

    let container = document.getElementById("herd-btns-" + gender);
    let elements = [];
    for (let i = 0; i < container.children.length; i++) {
        elements.push(container.childNodes[i]);
        container.removeChild(elements[elements.length - 1]);
        i--;
    }

    let elements2 = [];
    for (let i = 0; i < elements.length; i++) {
        if (elements[i].textContent.toUpperCase().indexOf(val.toUpperCase()) > -1) {
            elements2.push(elements[i]);
        }

        elements2.forEach(element => {
            container.appendChild(element);
        });
    }
}

function addAnotherBull() {
    let p = document.createElement("p");
    p.classList.add("bull");
    p.classList.add("single-bull")
    p.id = "bull-" + document.getElementsByClassName("bull").length;

    let p2 = document.createElement("p");
    p.appendChild(p2);

    let ipt = document.createElement("input");
    p2.appendChild(ipt);
    ipt.type = "number";
    ipt.min = 0;
    ipt.name = p.id;
    ipt.required = true
    ipt.oninput = (event) => {
        IDChange(event.target);
    }

    let spn = document.createElement("span");
    p.appendChild(spn)
    spn.textContent = "Enter ID#"

    let btn = document.createElement("button");
    p2.appendChild(btn);
    btn.type = "button";
    btn.textContent = "Remove Bull";
    btn.onclick = (event) => {
        removeBull(event.target);
    }

    document.getElementById("bulls").appendChild(p);
}

function removeBull(target) {
    let bullsList = document.getElementsByClassName("bull");
    if (bullsList.length <= 1) return;
    target.parentNode.parentNode.remove();

    for (let i = 0; i < bullsList.length; i++) {
        let element = bullsList[i];
        element.id = "bull-" + i;
        element.getElementsByTagName("input")[0].name = "bull-" + i;
    }
}

function IDChange(target) {
    if (target.value > Number.MAX_SAFE_INTEGER) return;

    if (sessionStorage.getItem("CanChangeId") == "true") {
        sessionStorage.setItem("CanChangeId", "false");
        FetchIDChange(target).finally(() => {
            sessionStorage.setItem("CanChangeId", "true");
        });
    } else {
        setTimeout(() => {
            IDChange(target)
        }, 100);
    }
}

async function setCowName(event) {
    let loadedGender = sessionStorage.getItem("LoadedGender")

    if (loadedGender == "none") return;
    event.target.disabled = true;

    let id = document.getElementById("id-ipt").value;
    let newname = document.getElementById("cow-name").value;
    if (!/^[A-Za-z0-9-_ .']+$/.test(newname)) {
        alertreal("Invalid name", `-_'. letters, numbers and spaces only.`, "ok");
        event.target.disabled = false;
        return;
    }

    let data = await fetch(`/set-cow-name/${id}/${newname}`);
    let jsondata = await data.json();

    if (jsondata["successful"]) {
        cows = getSessionDict("Cows");
        cows[loadedGender][id]["name"] = newname;
        setSessionDict("Cows", cows);

        alertreal("Name Changed", `Name was successfully changed to <br> ${newname}`, "ok");
    } else {
        alertreal("Name Change Failed", "Name change was unsuccessful.", "ok");
    }

    setSortOrder();

    event.target.disabled = false;
}

async function moveToClassHerd(event) {
    let loadedGender = sessionStorage.getItem("LoadedGender");
    if (loadedGender == "none") return;

    let gender = loadedGender == "bulls" ? "bull" : "cow";

    event.target.disabled = true;

    let confirm = await alertreal(
        `Move ${gender}`,
        `Are you sure you want to move this ${gender} to class herd?\nThis action cannot be undone.`,
        `Move ${gender}`,
        "Cancel"
    )

    if (confirm) {

        let id = document.getElementById("id-ipt").value;
        let data = await fetch(`/move-cow/${id}`);
        let jsondata = await data.json();

        let cows = getSessionDict("Cows");
        if (jsondata["successful"]) {
            alertreal("Move Successful", `${cows[loadedGender][id]["name"]} was successfully moved to class herd.`, "ok");
            delete cows[loadedGender][id];
            setSessionDict("Cows", cows);
        } else {
            alertreal("Move Failed", `${cows[gender][id]["name"]} could not be moved to class herd.`, "ok");
        }

        setSortOrder();
        changeDisplayedCow();
    }
    event.target.disabled = false;
}

async function FetchIDChange(target) {
    if (target.value != Math.round(target.value) || target.value == "") {
        target.parentNode.parentNode.getElementsByTagName("span")[0].value = "INVALID ID#";
        return;
    };

    let data = await fetch(`/get-cow-name/${sessionStorage.getItem("ClassId")}/${target.value}`);
    let jsonData = await data.json();

    if (jsonData["name"] == null) {
        target.parentNode.parentNode.getElementsByTagName("span")[0].textContent = "INVALID ID#";

    } else {
        target.parentNode.parentNode.getElementsByTagName("span")[0].textContent = jsonData["name"];
    }
}

async function setUp() {
    sessionStorage.setItem("CanChangeId", "true");
    sessionStorage.setItem("LoadedGender", "none");

    await loadHerdSummary();
    await loadCows();
    await loadTraitNames();
    displayTraits();
    displayCows();
    changeDisplayedCow();
}