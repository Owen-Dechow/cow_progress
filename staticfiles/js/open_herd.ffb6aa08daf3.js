var Cows;
var HerdSummary;
var HerdId;
var LoadedGender;
var CanChangeId;
var ClassId;

async function loadCows() {
    let cows = await fetch("/herddata-" + HerdId);

    if (!cows.ok) {
        alertreal("Error Loading Data", "Error loading herd data. Please try again.", "ok");
    }

    Cows = await cows.json();
}

async function loadHerdSummary() {
    let summary = await fetch("/herdsummary-" + HerdId);
    if (!summary.ok) {
        alertreal("Error Loading Data", "Error loading herd data. Please try again.", "ok");
    }

    HerdSummary = Object.freeze(await summary.json());
}

function displayCows() {
    displayCowsBy("id", false, "bulls", Cows);
    displayCowsBy("id", false, "cows", Cows);
}

function displayCowsBy(orderby, reverse, gender, cowslist) {
    let cows_btn_container = document.getElementById("herd-btns-" + gender);
    cows_btn_container.replaceChildren();

    let keylist = [];

    for (let key in cowslist[gender]) {
        if (cowslist[gender].hasOwnProperty(key)) {
            keylist.push(key);
        }
    }

    if (orderby == "id") keylist.sort((a, b) => b - a);
    else if (orderby == "Generation") keylist.sort((a, b) => cowslist[gender][b]["Generation"] - cowslist[gender][a]["Generation"]);
    else if (orderby == "Inbreeding Coefficient") keylist.sort((a, b) => cowslist[gender][b]["Inbreeding Coefficient"] - cowslist[gender][a]["Inbreeding Coefficient"]);
    else if (orderby == "Sire") keylist.sort((a, b) => cowslist[gender][b]["Sire"] - cowslist[gender][a]["Sire"]);
    else if (orderby == "Dam") keylist.sort((a, b) => cowslist[gender][b]["Dam"] - cowslist[gender][a]["Dam"]);
    else keylist.sort((a, b) => cowslist[gender][b]["traits"][orderby] - cowslist[gender][a]["traits"][orderby]);

    if (reverse) keylist.reverse();

    for (let key in keylist) {
        if (keylist.hasOwnProperty(key)) {
            let protectedKey = keylist[key];
            let btn = document.createElement("button");
            btn.textContent = cowslist[gender][protectedKey]["name"];
            btn.herdid = protectedKey;
            btn.setAttribute("type", "button");

            btn.onclick = (e) => {
                changeDisplayedCow(gender, e.target.herdid);
                btns = document.getElementsByClassName("focused-btn");
                for (let i = 0; i < btns.length; i++) {
                    btns[i].classList.remove("focused-btn");
                }
                e.target.classList.add("focused-btn");
            };

            cows_btn_container.append(btn);
        }
    }
}

function displayTraits() {
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

    addFromKey("id");
    addFromKey("Generation");
    addFromKey("Sire");
    addFromKey("Dam");
    addFromKey("Inbreeding Coefficient");
    for (let key in HerdSummary) {
        if (HerdSummary.hasOwnProperty(key)) {
            addFromKey(key);
        }
    }
}

function changeDisplayedCow(gender = null, cowID = null) {
    LoadedGender = gender;

    if (LoadedGender != null && cowID != null) {
        let cowname = document.getElementById("cow-name");
        if (cowname.classList.contains("owner")) {
            cowname.disabled = false;
        }

        if (LoadedGender == "bulls") {
            document.getElementById("add-to-bull-stack").style.display = "";
        } else {
            document.getElementById("add-to-bull-stack").style.display = "none";
        }

        let stats = Cows[LoadedGender][cowID];
        document.getElementById("cow-name").value = stats["name"];

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

                if (carriernumber == 0) carriercode = "Tested Free";
                else if (carriernumber == 1) carriercode = "Carrier (Heterozygous)";
                else if (carriernumber == 2) carriercode = "Positive";

                recessives.innerHTML += key + ": " + carriercode + "<br>";
            }
        }

        document.getElementById("pedigree-link").href = `/pedigree?animal_id=${cowID}`;

    } else {
        pedigreeLink = document.getElementById("pedigree-link");
        if (pedigreeLink) pedigreeLink.href = "javascript:void(0)";

        document.getElementById("cow-name").value = "[HERD SUMMARY]";
        document.getElementById("id" + "-ipt").value = "~";
        document.getElementById("Generation" + "-ipt").value = "~";
        document.getElementById("Inbreeding Coefficient" + "-ipt").value = "~";
        document.getElementById("Sire" + "-ipt").value = "~";
        document.getElementById("Dam" + "-ipt").value = "~";

        document.getElementById("add-to-bull-stack").style.display = "none";

        document.getElementById("cow-recessives").innerHTML = "~";
        for (let key in HerdSummary) {
            if (HerdSummary.hasOwnProperty(key)) {
                document.getElementById(key + "-ipt").value = HerdSummary[key];
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

    displayCowsBy(orderby.value, reverse.value == "neg", "bulls", Cows);
    displayCowsBy(orderby.value, reverse.value == "neg", "cows", Cows);
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
    p.classList.add("single-bull");
    p.id = "bull-" + document.getElementsByClassName("bull").length;

    let p2 = document.createElement("p");
    p.appendChild(p2);

    let ipt = document.createElement("input");
    p2.appendChild(ipt);
    ipt.type = "number";
    ipt.min = 0;
    ipt.name = p.id;
    ipt.required = true;
    ipt.oninput = (event) => {
        IDChange(event.target);
    };

    let spn = document.createElement("span");
    p.appendChild(spn);
    spn.textContent = "Enter ID#";

    let btn = document.createElement("button");
    p2.appendChild(btn);
    btn.setAttribute("type", "button");
    btn.textContent = "Remove Bull";
    btn.onclick = (event) => {
        removeBull(event.target);
    };

    document.getElementById("bulls").appendChild(p);
    return ipt;
}

function loadBreedingStack() {
    let stack = getcookie("bullstack");
    stack = stack.split(",");

    stack.forEach(elem => {
        if (elem) {
            let ipt = addAnotherBull();
            ipt.value = elem;
            IDChange(ipt);
        }
    });

    alertreal("Stack Loaded", "Breeding stack loaded", "Ok");
}

function clearBreedingStack() {
    let txt = "Are you sure you want to clear your breeding stack? This action cannot be undone.";
    if (alertreal("Clear Breeding Stack?", txt, "Clear", "Cancel")) {
        setcookie("bullstack", "", 0);
    }
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

    if (CanChangeId) {
        CanChangeId = false;
        FetchIDChange(target).finally(() => {
            CanChangeId = true;
        });
    } else {
        setTimeout(() => {
            IDChange(target);
        }, 100);
    }
}

async function setCowName(event) {
    if (LoadedGender == null) return;
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
        Cows[LoadedGender][id]["name"] = newname;

        alertreal("Name Changed", `Name was successfully changed to <br>"${newname}"`, "ok");
    } else {
        alertreal("Name Change Failed", "Name change was unsuccessful.", "ok");
    }

    setSortOrder();

    event.target.disabled = false;
}

async function moveToClassHerd(event) {
    if (LoadedGender == null) return;

    let gender = LoadedGender == "bulls" ? "bull" : "cow";

    event.target.disabled = true;

    let confirm = await alertreal(
        `Move ${gender}`,
        `Are you sure you want to move this ${gender} to class herd?\nThis action cannot be undone.`,
        `Move ${gender}`,
        "Cancel"
    );

    if (confirm) {

        let id = document.getElementById("id-ipt").value;
        let data = await fetch(`/move-cow/${id}`);
        let jsondata = await data.json();

        if (jsondata["successful"]) {
            alertreal("Move Successful", `${Cows[LoadedGender][id]["name"]} was successfully moved to class herd.`, "ok");
            delete Cows[LoadedGender][id];
        } else {
            alertreal("Move Failed", `${Cows[gender][id]["name"]} could not be moved to class herd.`, "ok");
        }

        setSortOrder();
        changeDisplayedCow();
    }
    event.target.disabled = false;
}

async function FetchIDChange(target) {
    let submit = target.closest("form").querySelector("button[type=submit]");
    submit.disabled = true;

    if (target.value != Math.round(target.value) || target.value == "") {
        target.parentNode.parentNode.getElementsByTagName("span")[0].value = "INVALID ID#";
        return;
    };

    let data = await fetch(`/get-cow-name/${ClassId}/${target.value}`);
    let jsonData = await data.json();

    if (jsonData["name"] == null) {
        target.parentNode.parentNode.getElementsByTagName("span")[0].textContent = "INVALID ID#";

    } else {
        target.parentNode.parentNode.getElementsByTagName("span")[0].textContent = jsonData["name"];
        submit.disabled = false;
    }
}

function addToBullStack() {
    let stack = getcookie("bullstack");
    stack = new Set(stack.split(","));
    let id = document.getElementById("id-ipt").value;
    stack.add(id);
    setcookie("bullstack", Array.from(stack).join(","), 1);
    alertreal("Bull Added", `Bull ${id} has been added to your breeding stack.`, "Ok");
}

async function setUp() {
    CanChangeId = true;
    LoadedGender = null;

    await loadHerdSummary();
    await loadCows();
    displayTraits();
    displayCows();
    changeDisplayedCow();
}

