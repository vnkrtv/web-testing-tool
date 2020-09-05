function getForm(i, tests, staticPath, url, tokenTag) {
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
    testNameH3.innerHTML = `${tests[i].name}`;

    const description_p = document.createElement('p');
    description_p.innerHTML = `${tests[i].description}`;

    const infoP = document.createElement('p');
    infoP.innerHTML = `<img src='${staticPath}main/images/subject.svg'> Предмет: ${tests[i].subject.name }<br>
    <img src='${staticPath}main/images/research.svg'> Количество заданий в тесте: ${tests[i].tasks_num}<br>
    <img src='${staticPath}main/images/clock.svg'> Время на выполнение: ${tests[i].duration} с`;

    const btn = document.createElement('button');
    btn.className = "btn btn-primary";
    btn.innerHTML = `<img src='${staticPath}main/images/play.svg'> Запустить`;
    btn.name =  "lecturer-running-test-id";
    btn.value = `${tests[i].id}`;

    label.appendChild(testNameH3);
    label.appendChild(description_p);
    label.appendChild(infoP);
    label.appendChild(btn);

    container.appendChild(hr);
    container.appendChild(label);

    form.appendChild(container);

    return form;
}

function main(testsJson, staticPath, url, tokenTag) {
    const tests = JSON.parse(testsJson.replace(/&quot;/gi, '"'));
    const testsCount = parseInt(tests.length);
    const testsContainer = document.getElementById("tests_container");

    const subject = document.getElementById("subject");
    const nameFilter = document.getElementById("name_filter");

    for (let i = 0; i < testsCount; ++i) {
        if (tests[i].subject.name === subject.options[0].text) {
            testsContainer.appendChild(getForm(i, tests, staticPath, url, tokenTag));
        }
    }
    activateModalWindows();

    subject.onkeyup = subject.onchange = () =>  {
        testsContainer.innerHTML = '';
        for (let i = 0; i < testsCount; ++i) {
            if (tests[i].name.includes(nameFilter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    testsContainer.appendChild(getForm(i, tests, staticPath, url, tokenTag));
                }
            }
        }
    };

    nameFilter.onkeyup = nameFilter.onchange = () =>  {
        testsContainer.innerHTML = '';
        for (let i = 0; i < testsCount; ++i) {
            if (tests[i].name.includes(nameFilter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    testsContainer.appendChild(getForm(i, tests, staticPath, url, tokenTag));
                }
            }
        }
    };
}
