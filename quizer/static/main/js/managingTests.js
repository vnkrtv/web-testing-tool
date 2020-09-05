function getDivElement(i, tests, staticPath) {
    const container = document.createElement('div');

    const hr = document.createElement('hr');
    hr.className = "my-4";

    const label = document.createElement('label');
    label.htmlFor = "test_name";

    const test_name_h3 = document.createElement('h3');
    test_name_h3.innerHTML = `${tests[i].name}`;

    const description_p = document.createElement('p');
    description_p.innerHTML = `${tests[i].description}`;

    const info_p = document.createElement('p');
    info_p.innerHTML = `<img src='${staticPath}main/images/subject.svg'> Предмет: ${tests[i].subject.name }<br>
    <img src='${staticPath}main/images/research.svg'> Количество заданий в тесте: ${tests[i].tasks_num}<br>
    <img src='${staticPath}main/images/clock.svg'> Время на выполнение: ${tests[i].duration} с<br>
    <img src='${staticPath}main/images/database.svg'> Вопросов к тесту: ${tests[i].questions_num}`;

    const btn_cont_1 = document.createElement('div');
    btn_cont_1.className = "btn-group mr-3";
    const btn_cont_2 = document.createElement('div');
    btn_cont_2.className = "btn-group mr-1";
    const btn_cont_3 = document.createElement('div');
    btn_cont_3.className = "btn-group mr-3";
    const btn_cont_4 = document.createElement('div');
    btn_cont_4.className = "btn-group mr-1";
    const btn_cont_5 = document.createElement('div');
    btn_cont_5.className = "btn-group mr-1";

    const edit_btn = document.createElement('button');
    edit_btn.className = "btn btn-primary js-open-modal";
    edit_btn.innerHTML = `<img src='${staticPath}main/images/edit.svg'> Редактировать`;
    edit_btn.setAttribute('data-modal', 'edit-modal');
    edit_btn.setAttribute('onclick',
        `fillEditModal(${tests[i].id}, "${tests[i].name}", "${tests[i].description}", "${tests[i].tasks_num}", "${tests[i].duration}")`);

    const add_qstn_btn = document.createElement('button');
    add_qstn_btn.className = "btn btn-success js-open-modal";
    add_qstn_btn.innerHTML = `<img src='${staticPath}main/images/add.svg'> Добавить вопрос`;
    add_qstn_btn.setAttribute('data-modal', 'add-question-modal');
    add_qstn_btn.setAttribute('onclick', `fillAddQuestionModal(${tests[i].id})`);

    const load_qstn_btn = document.createElement('button');
    load_qstn_btn.className = "btn btn-success js-open-modal";
    load_qstn_btn.innerHTML = `<img src='${staticPath}main/images/download.svg'> Загрузить вопросы`;
    load_qstn_btn.setAttribute('data-modal', 'load-questions-modal');
    load_qstn_btn.setAttribute('onclick', `fillLoadQuestionsModal(${tests[i].id})`);

    const del_qstn_btn = document.createElement('button');
    del_qstn_btn.className = "btn btn-danger js-open-modal";
    del_qstn_btn.innerHTML = `<img src='${staticPath}main/images/delete.svg'> Удалить вопросы`;
    del_qstn_btn.id = `test_name_${tests[i].name}`;
    del_qstn_btn.name = `test_name_${tests[i].id}`;
    del_qstn_btn.value = "del_qstn_btn";

    const del_test_btn = document.createElement('button');
    del_test_btn.className = "btn btn-danger js-open-modal";
    del_test_btn.innerHTML = `<img src='${staticPath}main/images/delete.svg'> Удалить тест`;
    del_test_btn.setAttribute('data-modal', 'delete-modal');
    del_test_btn.setAttribute('onclick',
        `fillDeleteModal(${tests[i].id}, "${tests[i].name}")`);

    btn_cont_1.appendChild(edit_btn);

    btn_cont_2.appendChild(add_qstn_btn);
    btn_cont_3.appendChild(load_qstn_btn);

    btn_cont_4.appendChild(del_qstn_btn);
    btn_cont_5.appendChild(del_test_btn);

    label.appendChild(test_name_h3);
    label.appendChild(description_p);
    label.appendChild(info_p);
    label.appendChild(btn_cont_1);
    label.appendChild(btn_cont_2);
    label.appendChild(btn_cont_3);
    label.appendChild(btn_cont_4);
    label.appendChild(btn_cont_5);

    container.appendChild(hr);
    container.appendChild(label);

    return container;
}

function fillEditModal(testID, testName, testDescription, testTasksNum, testDuration) {
    const idInput = document.getElementById('edit-test-id');
    idInput.value = testID;

    const nameInput = document.getElementById('edit-test-name');
    nameInput.value = testName;

    const descriptionInput = document.getElementById('edit-test-description');
    descriptionInput.value = testDescription;

    const tasksNumInput = document.getElementById('edit-test-tasks-num');
    tasksNumInput.value = testTasksNum;

    const durationInput = document.getElementById('edit-test-duration');
    durationInput.value = testDuration;
}

function fillDeleteModal(testID, testName) {
    const deleteP = document.getElementById('delete-p');
    deleteP.innerHTML = `Вы действительно хотите удалить тест '${testName}'?<br>
 		                 Тогда все связанные с ним вопросы будут удалены.`;

    const deleteTestInput = document.getElementById('delete-test-id');
    deleteTestInput.value = testID;
}

function fillAddQuestionModal(testID) {
    const testIDInput = document.getElementById('add-question-test-id');
    testIDInput.value = testID;
}

function fillLoadQuestionsModal(testID) {
    const testIDInput = document.getElementById('load-questions-test-id');
    testIDInput.value = testID;
}

function main(testsJson, staticPath) {
    const tests = JSON.parse(testsJson.replace(/&quot;/gi, '"'));
    const testsCount = parseInt(tests.length);
    const testsContainer = document.getElementById("tests_container");

    const subject = document.getElementById("subject");
    const nameFilter = document.getElementById("name_filter");

    for (let i = 0; i < testsCount; ++i) {
        if (tests[i].subject.name == subject.options[0].text) {
            testsContainer.appendChild(getDivElement(i, tests, staticPath));
        }
    }
    activateModalWindows();

    subject.onkeyup = subject.onchange = () =>  {
        testsContainer.innerHTML = '';
        for (let i = 0; i < testsCount; ++i) {
            if (tests[i].name.includes(nameFilter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    testsContainer.appendChild(getDivElement(i, tests, staticPath));
                }
            }
        }
        activateModalWindows();
    };

    nameFilter.onkeyup = nameFilter.onchange = () =>  {
        testsContainer.innerHTML = '';
        for (let i = 0; i < testsCount; ++i) {
            if (tests[i].name.includes(nameFilter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    testsContainer.appendChild(getDivElement(i, tests, staticPath));
                }
            }
        }
        activateModalWindows();
    };
}
