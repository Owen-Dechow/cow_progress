async function changeinfo(event, classID) {
    event.target.dissabled = true;
    var classinfo = document.getElementById("classinfo");
    var text = classinfo.value;
    if (text == "") {
        text = "<&:none>"
    }

    text = text.replace("/", "<&:slash>")

    var promise = await fetch(`/set-classinfo/${classID}/${encodeURIComponent(text)}`);
    var data = await promise.json();
    if (data["successful"]) {
        alertreal("Class Info Saved", "Class info has been successfully saved.", "ok");
    } else {
        alertreal("Save Failed", "Error! Class info failed to saved.", "ok");
    }
    event.target.dissabled = false;
}

async function deleteuser(event, userID) {
    event.target.dissabled = true;

    var promise = await fetch(`/delete-enrollment/${userID}`);
    var data = await promise.json();

    if (data["successful"]) {
        document.getElementById("member-" + userID).remove()
        alertreal("Enrollment Deleted", "Enrollment was successfully deleted.", "ok");
    } else {
        alertreal("Delete Failed", "Enrollment could not be deleted.", "ok");
    }

    event.target.dissabled = false;
}