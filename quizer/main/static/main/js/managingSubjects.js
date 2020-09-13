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
    document.getElementById('filesNames').value = filesStr.substr(0, filesStr.length - 11);
    document.getElementById('load-subject-name').children[1].value = folder[0];

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