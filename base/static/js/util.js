async function cancelNav(object, headerText, messageText, okText, cancelText) {
    let result = await alertreal(headerText, messageText, okText, cancelText);
    if (result) {
        window.location = object.href;
    }
}

async function cancelClick(object, headerText, messageText, okText, cancelText) {
    let result = await alertreal(headerText, messageText, okText, cancelText);
    if (result) {
        let clickMethod = object.onclick;
        object.onclick = () => true;
        object.click();
        object.onclick = clickMethod;
    }
}

async function cancelSubmit(object, headerText, messageText, okText, cancelText) {
    let result = await alertreal(headerText, messageText, okText, cancelText);
    console.log(result);
    if (result) {
        object.submit();
    }
}

function waitFor(conditionFunc) {
    const poll = resolve => {
        if (conditionFunc()) resolve();
        else setTimeout(_ => poll(resolve), 400);
    }

    return new Promise(poll);
}

function Copy(text) {
    let copyText = document.createElement("input");
    copyText.value = text;
    copyText.select();
    navigator.clipboard.writeText(copyText.value);
    alertreal("Copied Text", text, "ok")
}

async function alertreal(headerText, messageText, okText, cancelText = null, func = () => { }) {
    let response = null;

    let div = document.createElement("div");

    h1 = document.createElement("h1");
    h1.textContent = headerText;
    div.append(h1);

    let span = document.createElement("span");
    span.innerHTML = messageText;
    div.appendChild(span);

    let btn = document.createElement("button");
    btn.textContent = okText;
    btn.onclick = () => {
        response = true;
    };
    div.append(btn);
    document.activeElement.blur();

    if (cancelText != null) {
        let btn2 = document.createElement("button");
        btn2.textContent = cancelText;
        btn2.onclick = () => {
            response = false;
        };
        div.append(btn2);
    }

    let alert = document.getElementById("alert");
    alert.append(div);
    alert.classList.add("on");

    await waitFor(() => response != null)
    func();
    div.remove();
    document.getElementById("alert").classList.remove("on");
    return response;
}

function setcookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    let expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function getcookie(cookie) {
    let name = cookie + "=";
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i];
        while (cookie.charAt(0) == ' ') {
            cookie = cookie.substring(1);
        }
        if (cookie.indexOf(name) == 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    return "";
}

function getSessionDict(id) {
    return JSON.parse(sessionStorage.getItem(id));
}

async function setSessionDict(id, obj) {
    sessionStorage.setItem(id, JSON.stringify(obj))
}

window.addEventListener("DOMContentLoaded", async () => {
    if (getcookie("acceptedcookie") != "true") {
        alertreal(
            "COOKIES IN USE!",
            `
                This program utilizes cookies for security and user authentication.
                All cookies used are required for website functionality.
                At no time will any cookies be used to collect information about you.
                By using this website you recognize and accept the use of cookies.
            `,
            "Accept Cookies",
            null,
            () => {
                setcookie("acceptedcookie", "true", 1)
            },
        )
    }

    if (window.setUp) {
        await window.setUp();
    }
});
