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

function deleteSubject() {
    const subjectID = document.getElementById("delete-subject-id").value;
    $.ajax({
        url: editSubjectAPIUrl.replace(/subject_id/gi, subjectID),
        type: 'delete',
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            renderSubjects();
            renderInfoModalWindow("Предмет удален", response['success']);
        }});
}

function loadSubject() {
    const nameInput = document.getElementById("load-subject-name");
    const descriptionInput = document.getElementById("load-subject-description");
    const filesNamesInput = document.getElementById('files_names');
    const filesInput = document.getElementById('tests-files');

    let formData = new FormData();
    formData.append('name', nameInput.value);
    formData.append('description', descriptionInput.value);
    formData.append('load', '');
    formData.append('files_names', filesNamesInput.value);
    for (let file of filesInput.files) {
        formData.append('tests', file);
    }
    $.ajax({
        url: subjectAPIUrl,
        type: 'post',
        data: formData,
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            renderSubjects();
            renderInfoModalWindow("Новый предмет", response['success']);
        }});
}

function editSubject() {
    const idInput = document.getElementById("edit-subject-id");
    const nameInput = document.getElementById("edit-name");
    const descriptionInput = document.getElementById("edit-description");

    let formData = new FormData();
    formData.append('name', nameInput.value);
    formData.append('description', descriptionInput.value);

    $.ajax({
        url: editSubjectAPIUrl.replace(/subject_id/gi, idInput.value),
        type: 'put',
        data: formData,
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            renderSubjects();
            renderInfoModalWindow("Предмет отредактирован", response['success']);
        }});
}

function addSubject() {
    const nameInput = document.getElementById("id_name");
    const descriptionInput = document.getElementById("id_description");

    let formData = new FormData();
    formData.append('name', nameInput.value);
    formData.append('description', descriptionInput.value);

    $.ajax({
        url: subjectAPIUrl,
        type: 'post',
        data: formData,
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            renderSubjects();
            renderInfoModalWindow("Новый предмет", response['success']);
        }});
}

function renderSubjects() {
    $.get(subjectAPIUrl)
        .done((response) => {
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