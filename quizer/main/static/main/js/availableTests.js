function getTestContainer(test) {
    const container = document.createElement('div');

    const hr = document.createElement('hr');
    hr.className = "my-4";

    const label = document.createElement('label');
    label.htmlFor = "test_name";

    const testNameH3 = document.createElement('h3');
    testNameH3.innerHTML = `${test.name}`;

    const descriptionP = document.createElement('p');
    descriptionP.innerHTML = `${test.description}`;

    const infoP = document.createElement('p');
    infoP.innerHTML = `<img src='${staticUrl}main/images/subject.svg'> Предмет: ${test.subject.name}<br>
    <img src='${staticUrl}main/images/research.svg'> Количество заданий в тесте: ${test.tasks_num}<br>
    <img src='${staticUrl}main/images/clock.svg'> Время на выполнение: ${test.duration / 60} мин`;

    const btnCont1 = document.createElement('div');
    btnCont1.className = "btn-group mr-1";
    btnCont1.title = 'Запусить тест, чтобы слушатели могли приступить к его выполнению';

    const btnCont2 = document.createElement('div');
    btnCont2.className = "btn-group mr-1";
    btnCont2.title = 'Пробный запуск теста';

    const launchBtn = document.createElement('button');
    launchBtn.className = "btn btn-primary";
    launchBtn.innerHTML = `<img src='${staticUrl}main/images/play.svg'> Запустить`;
    launchBtn.setAttribute("onclick", `launchTest(${test.id})`);

    const runTestBtn = document.createElement('button');
    runTestBtn.className = "btn btn-primary";
    runTestBtn.innerHTML = `<img src='${staticUrl}main/images/play.svg'> Пройти`;
    runTestBtn.setAttribute("onclick", `runTest(${test.id}, ${test.tasks_num})`);

    btnCont1.appendChild(launchBtn);
    btnCont2.appendChild(runTestBtn);

    label.appendChild(testNameH3);
    label.appendChild(descriptionP);
    label.appendChild(infoP);
    label.appendChild(btnCont1);
    label.appendChild(btnCont2);

    container.appendChild(hr);
    container.appendChild(label);

    return container;
}

function launchTest(testID) {
    $.ajax({
        url: launchTestAPIUrl.replace('test_id', testID),
        type: 'put',
        contentType: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            if (response.ok) {
                renderInfoModalWindow("Тест запущен", response.message);
                renderAvailableTests();

                let launchData = {
                    action: 'test was launched'
                }
                socket.send(JSON.stringify(launchData));
            } else {
                renderInfoModalWindow("Ошибка", response.message);
            }
        }
    });
}

function runTest(testID, testTasksCount) {
    $.get(questionsAPIUrl.replace('test_id', testID)).done((response) => {
        if (response.questions.length >= testTasksCount) {
            window.location.href = runTestForLecturerUrl.replace('test_id', testID);
        } else {
            renderInfoModalWindow("Ошибка", `Тест не запущен, так как вопросов в базе меньше ${testTasksCount}.`);
        }
    });
}

function getRunningTestsWebSocket(socketPath) {
    let loc = window.location;
    let wsStart = 'ws://'
    if (loc.protocol === 'https:') {
        wsStart = 'wss://';
    }
    let endpoint = wsStart + loc.host + socketPath;
    return new WebSocket(endpoint);
}

function renderAvailableTests() {
    const testsContainer = document.getElementById("tests_container");
    const subject = document.getElementById("subject");
    const nameFilter = document.getElementById("name_filter");

    let tests = [];
    $.get(testsAPIUrl + '?state=not_running').done((response) => {
        tests = response.tests;
        testsContainer.innerHTML = '';
        for (let test of tests) {
            if (test.subject.id.toString() === subject.options[subject.selectedIndex].value) {
                testsContainer.appendChild(getTestContainer(test));
            }
        }
        activateModalWindows();
    });

    subject.onkeyup = subject.onchange = nameFilter.onkeyup = nameFilter.onchange = () => {
        testsContainer.innerHTML = '';
        for (let test of tests) {
            if (test.name.toLowerCase().includes(nameFilter.value.toLowerCase())) {
                if (test.subject.id.toString() === subject.options[subject.selectedIndex].value) {
                    testsContainer.appendChild(getTestContainer(test));
                }
            }
        }
    };
}

function getAvailableTestDiv(test) {
    const container = document.createElement('div');
    container.classList.add('jumbotron');

    const nameH3 = document.createElement('h3');
    nameH3.innerText = `${test.subject.name}: ${test.name}`;

    const descP = document.createElement('p');
    descP.innerText = test.description;

    const infoP = document.createElement('p');
    infoP.innerHTML = `<img src='${refsDict.userIcon}'> Запустил: ${test.launched_lecturer.username}<br>
        <img src='${refsDict.researchIcon}'> Количество заданий в тесте: ${test.tasks_num}<br>
        <img src='${refsDict.clockIcon}'> Время на выполнение: ${test.duration / 60} мин`;

    const form = document.createElement('form');
    form.setAttribute('action', refsDict.formUrl);
    form.setAttribute('method', 'post');
    form.innerHTML = refsDict.csrfToken + `<input type="hidden" name="test_id", value="${test.id}"> 
        <button class="btn btn-primary"><img src='${refsDict.playIcon}'> Приступить</button>`;

    container.appendChild(nameH3);
    container.appendChild(descP);
    container.appendChild(infoP);
    container.appendChild(form);

    return container;
}

function studentRenderAvailableTests() {
    const noRunningTestsDiv = document.getElementById('noRunningTestsDiv');
    let runningTests = [];
    $.get(testsAPIUrl + '?state=running')
        .done(function (response) {
            runningTests = response['tests'];
            runningTestsDiv.innerHTML = '';
            if (runningTests.length) {
                noRunningTestsDiv.style.display = 'none';
                for (let test of runningTests) {
                    runningTestsDiv.appendChild(getAvailableTestDiv(test));
                }
            } else {
                noRunningTestsDiv.style.display = '';
            }
        });
}
