function getForm(test, staticPath, url, tokenTag) {
    const form = document.createElement('form');
    form.action = url;
    form.method = 'post';
    form.innerHTML = tokenTag;

    const container = document.createElement('div');

    const hr = document.createElement('hr');
    hr.className = "my-4";

    const label = document.createElement('label');
    label.htmlFor = "test_name";

    const testNameH3 = document.createElement('h3');
    testNameH3.innerHTML = `${test.name}`;

    const description_p = document.createElement('p');
    description_p.innerHTML = `${test.description}`;

    const infoP = document.createElement('p');
    infoP.innerHTML = `<img src='${staticPath}main/images/subject.svg'> Предмет: ${test.subject.name}<br>
    <img src='${staticPath}main/images/research.svg'> Количество заданий в тесте: ${test.tasks_num}<br>
    <img src='${staticPath}main/images/clock.svg'> Время на выполнение: ${test.duration} с`;

    const btnCont1 = document.createElement('div');
    btnCont1.className = "btn-group mr-1";
    btnCont1.title = 'Запусить тест, чтобы слушатели могли приступить к его выполнению';

    const btnCont2 = document.createElement('div');
    btnCont2.className = "btn-group mr-1";
    btnCont2.title = 'Пробный запуск теста';

    const launchBtn = document.createElement('button');
    launchBtn.className = "btn btn-primary";
    launchBtn.innerHTML = `<img src='${staticPath}main/images/play.svg'> Запустить`;
    launchBtn.name =  "lecturer-running-test-id";
    launchBtn.value = test.id;

    const runTestBtn = document.createElement('button');
    runTestBtn.className = "btn btn-primary";
    runTestBtn.innerHTML = `<img src='${staticPath}main/images/play.svg'> Пройти`;
    runTestBtn.name =  "run-test";

    btnCont1.appendChild(launchBtn);
    btnCont2.appendChild(runTestBtn);

    const hiddenTestID = document.createElement('input');
    hiddenTestID.type = 'hidden';
    hiddenTestID.name = 'test_id';
    hiddenTestID.value = test.id;

    label.appendChild(testNameH3);
    label.appendChild(description_p);
    label.appendChild(infoP);
    label.appendChild(btnCont1);
    label.appendChild(btnCont2);
    label.appendChild(hiddenTestID);

    container.appendChild(hr);
    container.appendChild(label);

    form.appendChild(container);

    return form;
}

function main(testsUrl, staticPath, url, tokenTag) {
    const testsContainer = document.getElementById("tests_container");
    const subject = document.getElementById("subject");
    const nameFilter = document.getElementById("name_filter");

    let tests = [];
	$.get(testsUrl).done(function(response) {
        tests = response['tests'];
        for (let test of tests) {
            if (test.subject.id == subject.options[subject.selectedIndex].value) {
                testsContainer.appendChild(getForm(test, staticPath, url, tokenTag));
            }
        }
        activateModalWindows();
	});

    subject.onkeyup = subject.onchange = () =>  {
        testsContainer.innerHTML = '';
        for (let test of tests) {
            if (test.name.toLowerCase().includes(nameFilter.value.toLowerCase())) {
                if (test.subject.id == subject.options[subject.selectedIndex].value) {
                    testsContainer.appendChild(getForm(test, staticPath, url, tokenTag));
                }
            }
        }
    };

    nameFilter.onkeyup = nameFilter.onchange = () =>  {
        testsContainer.innerHTML = '';
        for (let test of tests) {
            if (test.name.toLowerCase().includes(nameFilter.value.toLowerCase())) {
                if (test.subject.id == subject.options[subject.selectedIndex].value) {
                    testsContainer.appendChild(getForm(test, staticPath, url, tokenTag));
                }
            }
        }
    };
}
