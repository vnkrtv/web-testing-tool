function fillAddTestModal() {
    const nameInput = document.getElementById("id_name");
    nameInput.value = '';
    const descriptionInput = document.getElementById("id_description");
    descriptionInput.value = '';
    const tasksNumInput = document.getElementById("id_tasks_num");
    tasksNumInput.value = '';
    const durationInput = document.getElementById("id_duration");
    durationInput.value = '';
    const subject = document.getElementById("subject");
    const subjectSelect = document.getElementById("id_subject");
    subjectSelect.selectedIndex = subject.selectedIndex;
}

function fillEditModal(testID) {
    const idInput = document.getElementById('edit-test-id');
    idInput.value = testID;

    const nameH3 = document.getElementById(`test-name-${testID}`);
    const nameInput = document.getElementById('edit-test-name');
    nameInput.value = nameH3.innerHTML;

    const descriptionP = document.getElementById(`test-description-${testID}`);
    const descriptionInput = document.getElementById('edit-test-description');
    descriptionInput.value = descriptionP.innerHTML;

    const tasksNumHiddenInput = document.getElementById(`test-tasks-num-${testID}`);
    const tasksNumInput = document.getElementById('edit-test-tasks-num');
    tasksNumInput.value = tasksNumHiddenInput.value;

    const durationHiddenInput = document.getElementById(`test-duration-${testID}`);
    const durationInput = document.getElementById('edit-test-duration');
    durationInput.value = parseFloat(durationHiddenInput.value) / 60;
}

function fillDeleteModal(testID) {
    const nameH3 = document.getElementById(`test-name-${testID}`);
    const deleteP = document.getElementById('delete-p');
    deleteP.innerHTML = `Вы действительно хотите удалить тест '${nameH3.innerHTML}'?<br>
 		                 Тогда все связанные с ним вопросы будут удалены.`;

    const deleteTestInput = document.getElementById('delete-test-id');
    deleteTestInput.value = testID;
}

function fillAddQuestionModal(testID) {
    const testIDInput = document.getElementById('add-question-test-id');
    testIDInput.value = testID;
}

function fillLoadQuestionsModal(testID) {
    const fileLabel = document.getElementById('fileLabel')
    fileLabel.innerText = 'Выберите файл';
    const loadQuestionsInput = document.getElementById('file');
    loadQuestionsInput.value = '';
    const testIDInput = document.getElementById('load-questions-test-id');
    testIDInput.value = testID;
}

function editTest() {
    const idInput = document.getElementById("edit-test-id");
    const nameInput = document.getElementById("edit-test-name");
    const descriptionInput = document.getElementById("edit-test-description");
    const tasksNumInput = document.getElementById("edit-test-tasks-num");
    const durationInput = document.getElementById("edit-test-duration");

    const testDurationInSeconds = parseFloat(durationInput.value) * 60;

    let formData = new FormData();
    formData.append('name', nameInput.value);
    formData.append('description', descriptionInput.value);
    formData.append('tasks_num', tasksNumInput.value);
    formData.append('duration', testDurationInSeconds.toString());

    $.ajax({
        url: editTestsAPIUrl.replace('test_id', idInput.value),
        type: 'put',
        data: formData,
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            renderTests();
            renderInfoModalWindow("Тест отредактирован", response['success']);
        }});
}

function addTest() {
    const nameInput = document.getElementById("id_name");
    const descriptionInput = document.getElementById("id_description");
    const tasksNumInput = document.getElementById("id_tasks_num");
    const durationInput = document.getElementById("id_duration");
    const subjectSelect = document.getElementById("id_subject");

    const testDurationInSeconds = parseFloat(durationInput.value) * 60;

    let formData = new FormData();
    formData.append('name', nameInput.value);
    formData.append('description', descriptionInput.value);
    formData.append('tasks_num', tasksNumInput.value);
    formData.append('duration', testDurationInSeconds.toString());
    formData.append('subject_id', subjectSelect.options[subjectSelect.selectedIndex].value);
    formData.append('author_id', userID);

    $.ajax({
        url: testsAPIUrl,
        type: 'post',
        data: formData,
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            renderTests();
            renderInfoModalWindow("Новый тест", response['success']);
        }});
}

function deleteTest() {
    const testID = document.getElementById("delete-test-id").value;
    $.ajax({
        url: editTestsAPIUrl.replace('test_id', testID.toString()),
        type: 'delete',
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            renderTests();
            renderInfoModalWindow("Тест удален", response['success']);
        }});
}

function loadQuestions() {
    const testID = document.getElementById("load-questions-test-id").value;
    const questionsFileInput = document.getElementById("file");
    let formData = new FormData();
    formData.append('file', questionsFileInput.files[0]);
    formData.append('load', 'true');

    $.ajax({
        url: questionsAPIUrl.replace('test_id', testID.toString()),
        type: 'post',
        data: formData,
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            renderTests();
            if (response['success'] !== undefined) {
                renderInfoModalWindow("Вопросы загружены", response['success']);
            } else {
                renderInfoModalWindow("Ошибка", response['error']);
            }
        }});
}

function getDivElement(test) {
    const container = document.createElement('div');

    const hr = document.createElement('hr');
    hr.className = "my-4";

    const label = document.createElement('label');
    label.htmlFor = "test_name";

    const testNameH3 = document.createElement('h3');
    testNameH3.id = `test-name-${test.id}`;
    testNameH3.innerHTML = `${test.name}`;

    const descriptionP = document.createElement('p');
    descriptionP.id = `test-description-${test.id}`;
    descriptionP.innerHTML = `${test.description}`;

    const infoP = document.createElement('p');
    infoP.innerHTML = `<img src='${staticUrl}main/images/subject.svg'> Предмет: ${test.subject.name}<br>
    <img src='${staticUrl}main/images/research.svg'> Количество заданий в тесте: ${test.tasks_num}<br>
    <img src='${staticUrl}main/images/clock.svg'> Время на выполнение: ${test.duration / 60} мин<br>
    <img src='${staticUrl}main/images/database.svg'> Вопросов к тесту: ${test.questions_num}`;

    const btnCont1 = document.createElement('div');
    btnCont1.className = "btn-group mr-3";
    const btnCont2 = document.createElement('div');
    btnCont2.className = "btn-group mr-1";
    const btnCont3 = document.createElement('div');
    btnCont3.className = "btn-group mr-1";
    const btnCont4 = document.createElement('div');
    btnCont4.className = "btn-group mr-3";
    const btnCont5 = document.createElement('div');
    btnCont5.className = "btn-group mr-1";

    const editTestBtn = document.createElement('button');
    editTestBtn.className = "btn btn-primary js-open-modal";
    editTestBtn.innerHTML = `<img src='${staticUrl}main/images/edit.svg'> Редактировать`;
    editTestBtn.setAttribute('data-modal', 'edit-modal');
    editTestBtn.setAttribute('onclick', `fillEditModal(${test.id})`);

    const qstnsRef = document.createElement('a');
    qstnsRef.className = "btn btn-success";
    qstnsRef.innerHTML = `<img src='${staticUrl}main/images/white_database.svg'> Вопросы к тесту`;
    qstnsRef.href = questionsUrl.replace(/test_id/gi, `${test.id}`);

    const addQstnBtn = document.createElement('button');
    addQstnBtn.className = "btn btn-success js-open-modal";
    addQstnBtn.innerHTML = `<img src='${staticUrl}main/images/add.svg'> Добавить вопрос`;
    addQstnBtn.setAttribute('data-modal', 'add-question-modal');
    addQstnBtn.setAttribute('onclick', `fillAddQuestionModal(${test.id})`);

    const loadQstnBtn = document.createElement('button');
    loadQstnBtn.className = "btn btn-success js-open-modal";
    loadQstnBtn.innerHTML = `<img src='${staticUrl}main/images/download.svg'> Загрузить вопросы`;
    loadQstnBtn.setAttribute('data-modal', 'load-questions-modal');
    loadQstnBtn.setAttribute('onclick', `fillLoadQuestionsModal(${test.id})`);

    const delTestBtn = document.createElement('button');
    delTestBtn.className = "btn btn-danger js-open-modal";
    delTestBtn.innerHTML = `<img src='${staticUrl}main/images/delete.svg'> Удалить тест`;
    delTestBtn.setAttribute('data-modal', 'delete-modal');
    delTestBtn.setAttribute('onclick',
        `fillDeleteModal(${test.id})`);

    const tasksNumInput = document.createElement('input');
    tasksNumInput.id = `test-tasks-num-${test.id}`;
    tasksNumInput.type = 'hidden';
    tasksNumInput.value = test.tasks_num;

    const durationInput = document.createElement('input');
    durationInput.id = `test-duration-${test.id}`;
    durationInput.type = 'hidden';
    durationInput.value = test.duration;

    btnCont1.appendChild(editTestBtn);
    btnCont2.appendChild(qstnsRef);

    btnCont3.appendChild(addQstnBtn);
    btnCont4.appendChild(loadQstnBtn);

    btnCont5.appendChild(delTestBtn);

    label.appendChild(testNameH3);
    label.appendChild(descriptionP);
    label.appendChild(infoP);
    label.appendChild(btnCont1);
    label.appendChild(btnCont2);
    label.appendChild(btnCont3);
    label.appendChild(btnCont4);
    label.appendChild(btnCont5);

    container.appendChild(hr);
    container.appendChild(label);
    container.appendChild(tasksNumInput);
    container.appendChild(durationInput);

    return container;
}

function renderTests() {
    const testsContainer = document.getElementById("tests_container");
    const subject = document.getElementById("subject");
    const nameFilter = document.getElementById("name_filter");

    let tests = [];
	$.get(testsAPIUrl + '?state=not_running')
        .done(function(response) {
            tests = response['tests'];
            testsContainer.innerHTML = '';
            for (let test of tests) {
                if (test.subject.id.toString() === subject.options[subject.selectedIndex].value) {
                    testsContainer.appendChild(getDivElement(test));
                }
            }
            activateModalWindows();
	    });

    subject.onkeyup = subject.onchange = nameFilter.onkeyup = nameFilter.onchange = () =>  {
        testsContainer.innerHTML = '';
        for (let test of tests) {
            if (test.name.toLowerCase().includes(nameFilter.value.toLowerCase())) {
                if (test.subject.id.toString() === subject.options[subject.selectedIndex].value) {
                    testsContainer.appendChild(getDivElement(test));
                }
            }
        }
        activateModalWindows();
    };
}
