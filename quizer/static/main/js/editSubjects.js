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
    document.querySelector('input#filesNames').value = filesStr.substr(0, filesStr.length - 11);
    document.querySelector('input#subjectName.form-control').value = folder[0];

}

function fillEditModal(subjectID, subjectName, subjectDescription) {
    const idInput = document.getElementById('edit-subject-id');
    idInput.value = subjectID;

    const nameInput = document.getElementById('edit-name');
    nameInput.value = subjectName;

    const descriptionInput = document.getElementById('edit-description');
    descriptionInput.value = subjectDescription;
}

function fillDeleteModal(subjectID, subjectName) {
    const deleteP = document.getElementById('delete-p');
    deleteP.innerHTML = `Вы действительно хотите удалить предмет '${subjectName}'?<br>
    Тогда все связанные с ним тесты и вопросы будут удалены.`;

    const deleteSubjectInput = document.getElementById('delete-subject-id');
    deleteSubjectInput.value = subjectID;
}