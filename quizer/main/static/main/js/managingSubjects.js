function clearForms(el) {
    const elements = document.getElementsByClassName('form-control');
    for (const element of elements) {
        element.value = '';
    }
}

function selectFolder(e) {
    let theFiles = e.target.files;
    let relativePath = theFiles[0].webkitRelativePath;
    let folder = relativePath.split("/");
    let filesStr = '';
    for (let filePath of theFiles) {
        filesStr += (filePath.name.split('.')[0] + '<separator>');
    }
    document.getElementById('files_names').value = filesStr.substr(0, filesStr.length - 11);
    document.getElementById('load-subject-name-label').children[1].value = folder[0];

}

function fillEditModal(subjectID) {
    const idInput = document.getElementById('edit-subject-id');
    idInput.value = subjectID;

    const subjectNameH3 = document.getElementById(`subject-name-${subjectID}`)
    const nameInput = document.getElementById('edit-name');
    nameInput.value = subjectNameH3.innerHTML;

    const subjectDescriptionP = document.getElementById(`subject-description-${subjectID}`)
    const descriptionInput = document.getElementById('edit-description');
    descriptionInput.value = subjectDescriptionP.innerHTML;
}

function fillDeleteModal(subjectID) {
    const subjectNameH3 = document.getElementById(`subject-name-${subjectID}`)
    const deleteP = document.getElementById('delete-p');
    deleteP.innerHTML = `Вы действительно хотите удалить предмет '${subjectNameH3.innerHTML}'?<br>
    Тогда все связанные с ним тесты и вопросы будут удалены.`;

    const deleteSubjectInput = document.getElementById('delete-subject-id');
    deleteSubjectInput.value = subjectID;
}

function deleteSubject(editSubjectAPIUrl, getSubjectsAPIUrl, csrfToken) {
    const subjectID = document.getElementById("delete-subject-id").value;
    const params = {
        csrfmiddlewaretoken: csrfToken
    };
    $.post(
        editSubjectAPIUrl.replace(/subject_id/gi, subjectID), params).done((response) => {
            console.log(response['success']);
            renderSubjects(getSubjectsAPIUrl, dbIconUrl, editIconUrl, delIconUrl, csrfToken);
            const overlay = document.getElementById("overlay");
            overlay.classList.add("active");
            const infoModal = document.getElementById("info-modal");
            infoModal.classList.add("active");
            const infoModalH4 = document.getElementById("info-modal-title");
            infoModalH4.innerText = "Предмет удален";
            const infoModalP = document.getElementById("info-modal-p");
            infoModalP.innerText = response['success'];
        });
}

function loadSubject(editSubjectAPIUrl, getSubjectsAPIUrl, csrfToken) {
    const nameInput = document.getElementById("load-subject-name");
    const descriptionInput = document.getElementById("load-subject-description");
    const filesNamesInput = document.getElementById('files_names');
    const filesInput = document.getElementById('tests-files');

    let formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrfToken);
    formData.append('name', nameInput.value);
    formData.append('description', descriptionInput.value);
    formData.append('files_names', filesNamesInput.value);
    formData.append('csrfmiddlewaretoken', csrfToken);
    for (let file of filesInput.files) {
        console.log(file);
        formData.append('tests', file);
    }

    $.ajax({
        url: editSubjectAPIUrl.replace(/subject_id/gi, 'load'),
        type: 'post',
        data: formData,
        contentType: false,
        processData: false,
        success: (response) => {
            renderSubjects(getSubjectsAPIUrl, dbIconUrl, editIconUrl, delIconUrl, csrfToken);
            const overlay = document.getElementById("overlay");
            overlay.classList.add("active");
            const infoModal = document.getElementById("info-modal");
            infoModal.classList.add("active");
            const infoModalH4 = document.getElementById("info-modal-title");
            infoModalH4.innerText = "Новый предмет";
            const infoModalP = document.getElementById("info-modal-p");
            infoModalP.innerText = response['success'];
        }});
}

function editSubject(editSubjectAPIUrl, getSubjectsAPIUrl, csrfToken) {
    const idInput = document.getElementById("edit-subject-id");
    const nameInput = document.getElementById("edit-name");
    const descriptionInput = document.getElementById("edit-description");
    const params = {
        csrfmiddlewaretoken: csrfToken,
        name: nameInput.value,
        description: descriptionInput.value
    };
    $.post(
        editSubjectAPIUrl.replace(/subject_id/gi, idInput.value), params).done((response) => {
            renderSubjects(getSubjectsAPIUrl, dbIconUrl, editIconUrl, delIconUrl, csrfToken);
            const overlay = document.getElementById("overlay");
            overlay.classList.add("active");
            const infoModal = document.getElementById("info-modal");
            infoModal.classList.add("active");
            const infoModalH4 = document.getElementById("info-modal-title");
            infoModalH4.innerText = "Предмет отредактирован";
            const infoModalP = document.getElementById("info-modal-p");
            infoModalP.innerText = response['success'];
        });
}

function addSubject(editSubjectAPIUrl, getSubjectsAPIUrl, csrfToken) {
    const nameInput = document.getElementById("id_name");
    const descriptionInput = document.getElementById("id_description");
    const params = {
        csrfmiddlewaretoken: csrfToken,
        name: nameInput.value,
        description: descriptionInput.value
    };
    $.post(
        editSubjectAPIUrl.replace(/subject_id/gi, 'new'), params).done((response) => {
            renderSubjects(getSubjectsAPIUrl, dbIconUrl, editIconUrl, delIconUrl, csrfToken);
            const overlay = document.getElementById("overlay");
            overlay.classList.add("active");
            const infoModal = document.getElementById("info-modal");
            infoModal.classList.add("active");
            const infoModalH4 = document.getElementById("info-modal-title");
            infoModalH4.innerText = "Новый предмет";
            const infoModalP = document.getElementById("info-modal-p");
            infoModalP.innerText = response['success'];
        });
}

function renderSubjects(getSubjectsAPIUrl, dbIconUrl, editIconUrl, delIconUrl) {
    $.get(getSubjectsAPIUrl).done((response) => {
        const subjects = response['subjects'];
        const subjectsDiv = document.getElementById("subjects-container");
        subjectsDiv.innerHTML = "";
        for (const subject of subjects) {
            const container = document.createElement("div");
            const hr = document.createElement("hr");
            hr.className = "my-h4";
            container.appendChild(hr);

            const nameH3 = document.createElement("h3");
            nameH3.id = "subject-name-" + subject.id;
            nameH3.innerText = subject.name;
            container.appendChild(nameH3);

            const descriptionP = document.createElement("p");
            descriptionP.id = "subject-description-" + subject.id;
            descriptionP.innerText = subject.description;
            container.appendChild(descriptionP);

            const dbImg = document.createElement("img");
            dbImg.setAttribute("src", dbIconUrl);

            const testsP = document.createElement("p");
            testsP.appendChild(dbImg);
            testsP.append(` Тестов к предмету: ${subject.tests_count}`);
            container.appendChild(testsP);

            const editDiv = document.createElement("div");
            editDiv.className = "btn-group mr-2";

            const editButton = document.createElement("button");
            editButton.className = "btn btn-primary js-open-modal";
            editButton.setAttribute("data-modal", "edit-modal");
            editButton.setAttribute("onclick", `fillEditModal("${subject.id}")`);

            const editImg = document.createElement("img");
            editImg.setAttribute("src", editIconUrl);
            editButton.appendChild(editImg);
            editButton.append(" Редактировать");

            editDiv.appendChild(editButton);
            container.appendChild(editDiv);


            const delDiv = document.createElement("div");
            delDiv.className = "btn-group mr-2";

            const delButton = document.createElement("button");
            delButton.className = "btn btn-danger js-open-modal";
            delButton.setAttribute("data-modal", "delete-modal");
            delButton.setAttribute("onclick", `fillDeleteModal("${subject.id}")`);

            const delImg = document.createElement("img");
            delImg.setAttribute("src", delIconUrl);
            delButton.appendChild(delImg);
            delButton.append(" Удалить");

            delDiv.appendChild(delButton);
            container.appendChild(delDiv);

            subjectsDiv.appendChild(container);
        }
        activateModalWindows();
    });
}