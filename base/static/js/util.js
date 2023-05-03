function Copy(text) {
    let copyText = document.createElement("input");
    copyText.value = text;
    copyText.select();
    navigator.clipboard.writeText(copyText.value);
    alertreal("Copied Text", text, "ok")
}

function alertreal(headerText, messageText, okText, func = () => { }) {
    let div = document.createElement("div");

    h1 = document.createElement("h1");
    h1.textContent = headerText;
    div.append(h1);

    let span = document.createElement("span");
    span.innerHTML = messageText;
    div.appendChild(span);

    let btn = document.createElement("button");
    btn.textContent = okText;
    btn.onclick = (event) => {
        func();
        event.target.parentNode.remove();
    };
    div.append(btn);

    document.getElementById("footer").append(div);
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
            "Waring",
            "This website depends on cookies to function. Please accept cookies before use.",
            "Accept Cookies",
            () => {
                setcookie("acceptedcookie", "true", 1)
            },
        )
    }

    if (window.setUp) {
        await window.setUp();
    }
});
