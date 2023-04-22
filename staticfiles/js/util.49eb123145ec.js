function Copy(text) {
    var copyText = document.createElement("input");
    copyText.value = text;
    copyText.select();
    navigator.clipboard.writeText(copyText.value);
    alertreal("Copied Text", text, "ok")
}

function alertreal(headerText, messageText, okText, func = () => { }) {
    div = document.createElement("div");

    h1 = document.createElement("h1");
    h1.textContent = headerText;
    div.append(h1);

    span = document.createElement("span");
    span.innerHTML = messageText;
    div.appendChild(span);

    btn = document.createElement("button");
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