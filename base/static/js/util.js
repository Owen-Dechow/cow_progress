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
    };

    return new Promise(poll);
}

function Copy(text) {
    let copyText = document.createElement("input");
    copyText.value = text;
    copyText.select();
    navigator.clipboard.writeText(copyText.value);
    alertreal("Copied Text", text, "ok");
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
    btn.setAttribute("type", "button");
    btn.setAttribute("title", `Confirm: ${headerText}`);
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

    await waitFor(() => response != null);
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

function toggleTheme() {
    if (getcookie("theme") == "dark") {
        setcookie("theme", "light", 365);
    } else {
        setcookie("theme", "dark", 365);
    }

    document.body.classList.remove("dark");
    document.body.classList.remove("light");
    document.body.classList.add(getcookie("theme"));
}

window.addEventListener("DOMContentLoaded", async () => {
    if (getcookie("acceptedcookie") != "true" && window.location.pathname != "/cookies/") {
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
                setcookie("acceptedcookie", "true", 365);
            },
        );

        let div = document.getElementById("alert").getElementsByTagName("div")[0];
        let a = document.createElement("a");
        a.textContent = "More Info";
        a.href = "/cookies/";
        a.classList.add("as-btn");
        div.append(a);
    }

    if (window.setUp) {
        await window.setUp();
    }
});