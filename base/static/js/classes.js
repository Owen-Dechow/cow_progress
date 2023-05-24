async function changeinfo(event, classID) {
    event.target.dissabled = true;
    let classinfo = document.getElementById("classinfo");
    let text = classinfo.value;
    if (text == "") {
        text = "<&:none>"
    }

    text = text.replace("/", "<&:slash>")

    let promise = await fetch(`/set-classinfo/${classID}/${encodeURIComponent(text)}`);
    let data = await promise.json();
    if (data["successful"]) {
        alertreal("Class Info Saved", "Class info has been successfully saved.", "ok");
    } else {
        alertreal("Save Failed", "Error! Class info failed to saved.", "ok");
    }
    event.target.dissabled = false;
}

async function deleteuser(event, userID, studentname) {
    event.target.dissabled = true;

    let remove = await alertreal(`Remove Student`, `Are you sure you want to remove ${studentname} from this class?`, "Remove Student", "Cancel");
    if (remove) {
        let promise = await fetch(`/delete-enrollment/${userID}`);
        let data = await promise.json();

        if (data["successful"]) {
            document.getElementById("member-" + userID).remove()
            alertreal("Enrollment Deleted", "Enrollment was successfully deleted.", "ok");
        } else {
            alertreal("Delete Failed", "Enrollment could not be deleted.", "ok");
        }
    }


    event.target.dissabled = false;
}