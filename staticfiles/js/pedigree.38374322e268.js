async function setUp() {
    let pedigreeID = sessionStorage.getItem("Pedigree");
    if (pedigreeID > -1) {
        let data = await fetch("get-pedigree-" + pedigreeID);
        if (data.ok) {
            setSessionDict("Pedigree", await data.json());
            displayTree();
            await loadCowData();
        } else {
            alertreal("Error Loading Data", "The pedigree you asked for could not be loaded.", "ok");
        }
    }
}

function displayTree() {
    let tree = getSessionDict("Pedigree");
    let container = document.getElementById("pedigree");
    let gender = tree["sex"] == "Male" ? "Bull" : "Cow"
    unpackDictToNode(container, tree, gender + " (", ")");
}

function unpackDictToNode(node, dict, textprefix, textsuffix) {
    let details = document.createElement("details");
    let summary = document.createElement("summary");
    let div = document.createElement("div");
    let a = document.createElement("a");

    summary.textContent = textprefix + dict["id"] + textsuffix;
    details.append(summary);

    a.href = `/pedigree?animal_id=${dict["id"]}`;
    a.textContent = "Open Pedigree";
    a.classList.add("as-link");
    summary.append(a);

    if (dict["sire"]) {
        unpackDictToNode(div, dict["sire"], "sire (", ")");
    }
    if (dict["dam"]) {
        unpackDictToNode(div, dict["dam"], "dam (", ")");
    }
    details.append(div);

    node.append(details);
}

function addTableRows(table, dict, overide) {
    for (let key in dict) {
        if (dict.hasOwnProperty(key)) {
            let tr = document.createElement("tr");
            let tdLeft = document.createElement("td");
            let tdRight = document.createElement("td");

            tdLeft.textContent = key;
            tdLeft.classList.add("leftcol");

            let text;
            if (overide) {
                if (dict[key] == 0) text = "Tested Free";
                else if (dict[key] == 1) text = "Carrier";
                else if (dict[key] == 2) text = "Positive";
            } else {
                text = dict[key];
            }

            tdRight.textContent = text;

            tr.append(tdLeft);
            tr.append(tdRight);
            table.append(tr);
        }
    }
}

function addTableToNode(node, dict, title, overide) {
    let table = document.createElement("table");
    let th = document.createElement("th");

    th.textContent = title;
    th.colSpan = 2;
    table.append(th);
    addTableRows(table, dict, overide);

    node.append(table);
}

async function loadCowData() {
    let tree = getSessionDict("Pedigree");
    let response = await fetch(`get-data-${tree["id"]}`);
    let data = await response.json();


    if (data["successful"]) {
        let container = document.getElementById("cow-data");

        let infoDict = {};
        infoDict["Name"] = data["name"];
        infoDict["Generation"] = data["Generation"];
        infoDict["Dam"] = data["Dam"];
        infoDict["Sire"] = data["Sire"];
        infoDict["Inbreeding Coefficient"] = data[["Inbreeding Coefficient"]];

        addTableToNode(container, infoDict, "Info", false)
        addTableToNode(container, data["traits"], "PTAs", false);
        addTableToNode(container, data["recessives"], "Recessives", true);
    } else {
        document.getElementById("recessive-info").classList.add("hide");
    }

}